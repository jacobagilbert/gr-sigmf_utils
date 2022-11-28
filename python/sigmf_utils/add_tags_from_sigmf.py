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
import sigmf_utils

class add_tags_from_sigmf(gr.sync_block):
    """
    This block will generate stream tags from either a SigMF Metadata or a `.sigmf-meta`
    file. The following stream tags are generated:

    Global Scope:
        `sample_rate` - on the first sample generated only

    Captures Scope:
        `frequency` - first sample only, limited to captures[0] metadata for now

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
    """
    def __init__(self, dtype, metadata, add_annotation_tags=True):
        gr.sync_block.__init__(self,
            name="add_tags_from_sigmf",
            in_sig=[dtype],
            out_sig=[dtype])

        self.interleaved = True if dtype == numpy.int16 else False

        if isinstance(metadata, dict):
            self.sigmf_metadata = metadata
        elif isinstance(metadata, str) and metadata.endswith('.sigmf-meta'):
            with open(metadata, 'r') as f:
                gr.log.info(f'Loading SigMF metadata from {metadata}')
                self.sigmf_metadata = json.load(f)
        else:
            raise ValueError(f'Invalid SigMF metadata specification {metadata}')
        sigmf_utils.check_metadata(self.sigmf_metadata)

        if ncaps := len(self.sigmf_metadata['captures']) > 1:
            gr.log.warn(f'SigMF has {ncaps} captures, only the first will be used!')

        self.begin_tags = []
        self.sample_rate = self.sigmf_metadata['global'].get('core:sample_rate')
        if self.sample_rate is not None:
            self.begin_tags.append(gr.tag_utils.python_to_tag((0, pmt.intern("sample_rate"), pmt.from_double(self.sample_rate))))
        self.frequency = self.sigmf_metadata['captures'][0].get('core:frequency')
        if self.frequency is not None:
            self.begin_tags.append(gr.tag_utils.python_to_tag((0, pmt.intern("frequency"), pmt.from_double(self.frequency))))

        self.anno_tags = []
        if add_annotation_tags:
            # tags have keys of `new_burst` or `gone_burst and values dictionaries respectively:
            # ((bandwidth . 263671) (noise_density . -153.272) (sample_rate . 4e+07) (magnitude . 62.6101) (center_frequency . 9.15e+08) (relative_frequency . 0.0878906) (burst_id . 0))
            # ((burst_id . 0))
            sob = pmt.intern('new_burst')
            eob = pmt.intern('gone_burst')
            for ii, anno in enumerate(self.sigmf_metadata['annotations']):
                offset = anno.get('core:sample_start', 0)
                end = offset + anno.get('core:sample_count', offset)
                offset = offset * 2 if self.interleaved else offset
                end = end * 2 if self.interleaved else end
                tag_dict = {'sample_rate': self.sample_rate, 'center_frequency': self.frequency, 'burst_id': ii}
                f_lower = anno.get('core:freq_lower_edge')
                f_upper = anno.get('core:freq_upper_edge')
                if f_lower and f_upper:
                    tag_dict['bandwidth'] = (f_upper - f_lower) * 1.0
                    freq = f_lower + tag_dict['bandwidth'] / 2.0
                    tag_dict['relative_frequency'] = (freq - self.frequency) / self.sample_rate
                tag_dict['magnitude']=0.0   # dumb... but this field needs to be present
                self.anno_tags.append(gr.tag_utils.python_to_tag((offset, sob, pmt.to_pmt(tag_dict))))
                self.anno_tags.append(gr.tag_utils.python_to_tag((end, eob, pmt.to_pmt({'burst_id': ii}))))           

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        out[:] = in0

        # add all the tags on the first work function call
        if self.nitems_written(0) == 0:
            for tag in self.begin_tags:
                self.add_item_tag(0, tag) 
            for tag in self.anno_tags:
                self.add_item_tag(0, tag)            
        return len(output_items[0])
