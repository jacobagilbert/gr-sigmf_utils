#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 J. A. Gilbert
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
import json
import pmt
from os.path import isfile
from gnuradio import gr
from gnuradio import sigmf_utils

class add_tags_from_sigmf(gr.sync_block):
    """
    This block will generate stream tags from either a SigMF Metadata or a `.sigmf-meta`
    file. The following stream tags are generated:

    Global Scope (always on the 0th sample and at the start of every capture)
        `offset` - int from `core:offset` field
        `sample_rate` - double from `core:sample_rate` field
        `geolocation` - geojson point object from `core:sample_rate` field

    Captures Scope:
        `frequency` - from `core:frequency` field
        `datetime` - string from `core:datetime` field

    Annotations Scope (configurable):
        `new_burst` - Value is a dictionary similar to the gr-fhss_utils tags:
            - `burst_id` - annotation number (as indexed by annotations list in file)
            - `bandwidth` - double representing annotation bandwidth
            - `sample_rate` - from `global` scope metadata
            - `center_frequency` - from `captures` scope metadata
            - `relative_frequency` - relative center frequency of the annotation (-0.5 to 0.5]
        `gone_burst` - Value is a dictionary similar to the gr-fhss_utils tags:
            - `burst_id` - annotation number (as indexed by annotations list in file)

    Tags are all generated on the first work function call, but their offset values are
    representative of what is in the SigMF metadata. For complex interleaved types tags
    are placed on the first (real component) item.

    Block paramters:

        dtype:                  gnuradio data type for streaming inputs
        metadata:               either a SigMF format metadata dictionary or sigmf-meta
                                filename to use for tag generation
        add_annotation_tags:    optional parameter that can be used to control whether
                                tags for annotations are generated or not
        start_tag_key:          PMT object representing the key for a tag signifying the
                                start of file, this will be used to repeat the tags

    TODO:   produce tags just in time instead of all at once as soon as they are known so
            annotations that overextend actual generated data are not tagged
    """
    def __init__(self, dtype, metadata, add_annotation_tags=True, start_tag_key=pmt.PMT_NIL):
        gr.sync_block.__init__(self,
            name="add_tags_from_sigmf",
            in_sig=[dtype],
            out_sig=[dtype])

        self.interleaved = True if dtype == numpy.int16 else False
        self.add_annotation_tags = add_annotation_tags
        self.start_tag_key = start_tag_key

        if isinstance(metadata, dict):
            self.sigmf_metadata = metadata
        elif isinstance(metadata, str) and metadata.endswith('.sigmf-meta'):
            with open(metadata, 'r') as f:
                gr.log.info(f'Loading SigMF metadata from {metadata}')
                self.sigmf_metadata = json.load(f)
        else:
            raise ValueError(f'Invalid SigMF metadata specification {metadata}')
        sigmf_utils.check_metadata(self.sigmf_metadata)
        self.build_tag_list()

    def build_tag_list(self, item_offset=0):
        self.global_tags = []   # global tags will emitted at the start of every capture segment
        self.offset = self.sigmf_metadata['global'].get('core:offset')
        if self.offset is not None:
            self.global_tags.append(gr.tag_utils.python_to_tag((item_offset, pmt.intern("offset"), pmt.from_uint64(self.offset), pmt.intern('SigMF Global'))))
        self.sample_rate = float(self.sigmf_metadata['global'].get('core:sample_rate'))
        if self.sample_rate is not None:
            self.global_tags.append(gr.tag_utils.python_to_tag((item_offset, pmt.intern("sample_rate"), pmt.from_double(self.sample_rate), pmt.intern('SigMF Global'))))
        self.geolocation = self.sigmf_metadata['global'].get('core:geolocation')
        if self.geolocation is not None:
            self.global_tags.append(gr.tag_utils.python_to_tag((item_offset, pmt.intern("geolocation"), pmt.to_pmt(self.geolocation), pmt.intern('SigMF Global'))))

        self.item_tags = []
        self.captures = self.sigmf_metadata['captures']
        for idx, capture in enumerate(self.captures):
            offset = capture.get('core:sample_start', 0)
            # if the first capture does not start with sample zero, add global tags
            if idx == 0 and offset != 0:
                for tag in self.global_tags:
                    self.item_tags.append(tag)
            # add tags if they exist
            frequency = sigmf_utils.get_capture_metadata(self.captures, offset, 'core:frequency')
            if frequency is not None:
                self.item_tags.append(gr.tag_utils.python_to_tag((offset + item_offset, pmt.intern("frequency"), pmt.from_double(frequency), pmt.intern(f'SigMF Capture {idx}'))))
            datetime = capture.get('core:datetime')
            if datetime is not None:
                self.item_tags.append(gr.tag_utils.python_to_tag((offset + item_offset, pmt.intern("datetime"), pmt.intern(datetime), pmt.intern(f'SigMF Capture {idx}'))))
            for tag in self.global_tags:
                self.item_tags.append(gr.tag_utils.python_to_tag((offset + item_offset, tag.key, tag.value, tag.srcid)))

        if self.add_annotation_tags:
            # tags have keys of `new_burst` or `gone_burst and values dictionaries respectively:
            # ((bandwidth . 263671) (noise_density . -153.272) (sample_rate . 4e+07) (magnitude . 62.6101) (center_frequency . 9.15e+08) (relative_frequency . 0.0878906) (burst_id . 0))
            # ((burst_id . 0))
            sob = pmt.intern('new_burst')
            eob = pmt.intern('gone_burst')
            for idx, anno in enumerate(self.sigmf_metadata['annotations']):
                offset = anno.get('core:sample_start', 0)

                frequency = float(sigmf_utils.get_capture_metadata(self.captures, offset, 'core:frequency'))
                end = offset + anno.get('core:sample_count', offset)
                offset = offset * 2 if self.interleaved else offset
                end = end * 2 if self.interleaved else end

                tag_dict = {'sample_rate': self.sample_rate, 'center_frequency': frequency, 'burst_id': idx}

                f_lower = anno.get('core:freq_lower_edge')
                f_upper = anno.get('core:freq_upper_edge')
                if f_lower and f_upper:
                    tag_dict['bandwidth'] = float(f_upper - f_lower)
                    freq = f_lower + float(tag_dict['bandwidth']) / 2.0
                    tag_dict['relative_frequency'] = (freq - frequency) * 1.0 / self.sample_rate

                self.item_tags.append(gr.tag_utils.python_to_tag((offset + item_offset, sob, pmt.to_pmt(tag_dict), pmt.intern(f'SigMF Annotation'))))
                self.item_tags.append(gr.tag_utils.python_to_tag((end + item_offset, eob, pmt.to_pmt({'burst_id': idx}), pmt.intern(f'SigMF Annotation'))))

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        if pmt.eqv(pmt.PMT_NIL, self.start_tag_key):
            # add all the tags on the first work function call only once
            if self.nitems_written(0) == 0:
                for tag in self.item_tags:
                    self.add_item_tag(0, tag)
        else:
            # look for the start of file tag key and add tags when it is observed
            tags = self.get_tags_in_range(0, self.nitems_read(0), self.nitems_read(0) + len(in0))
            for tag in tags:
                if pmt.eqv(tag.key, self.start_tag_key):
                    self.build_tag_list(tag.offset)
                    for tag in self.item_tags:
                        self.add_item_tag(0, tag)

        out[:] = in0

        return len(output_items[0])
