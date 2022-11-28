#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright J. A. Gilbert, 2022
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
import json
import pmt
from sigmf import sigmffile
from os.path import isfile
from gnuradio import gr

class add_tags_from_sigmf(gr.sync_block):
    """
    docstring for block add_tags_from_sigmf
    """
    def __init__(self, dtype, metadata, add_annotation_tags=True):
        gr.sync_block.__init__(self,
            name="add_tags_from_sigmf",
            in_sig=[dtype],
            out_sig=[dtype])

        if isinstance(metadata, dict):
            if 'global' in metadata and 'captures' in metadata and 'annotations' in metadata:
                self.sigmf_metadata = sigmffile.SigMFFile(metadata)
            else:
                # something is wrong with the sigmf spec... load this
                self.sigmf_metadata = sigmffile.SigMFFile()
        elif isinstance(metadata, str) and metadata.endswith('.sigmf-meta'):
            if isfile(metadata):
                print(f'Loading SigMF metadata from {metadata}')
                self.sigmf_metadata = sigmffile.fromfile(metadata)
            else:
                raise RuntimeError(f'SigMF metadata file {metadata} does not exist')
        else:
            raise RuntimeError(f'Invalid SigMF metadata specification {metadata}')


        if ncaps := len(self.sigmf_metadata.get_captures()) > 1:
            print(f'Warning! SigMF has {ncaps} captures, only the first will be used!')


        self.begin_tags = []
        self.sample_rate = self.sigmf_metadata.get_global_info().get('core:sample_rate')
        self.frequency = self.sigmf_metadata.get_capture_info(0).get('core:frequency')
        if self.sample_rate is not None:
            self.begin_tags.append(gr.tag_utils.python_to_tag((0, pmt.intern("sample_rate"), pmt.from_double(self.sample_rate))))
        if self.frequency is not None:
            self.begin_tags.append(gr.tag_utils.python_to_tag((0, pmt.intern("frequency"), pmt.from_double(self.frequency))))
            

        self.anno_tags = []
        if add_annotation_tags:
            # tags have keys of `new_burst` or `gone_burst and values dictionaries respectively:
            # ((bandwidth . 263671) (noise_density . -153.272) (sample_rate . 4e+07) (magnitude . 62.6101) (center_frequency . 9.15e+08) (relative_frequency . 0.0878906) (burst_id . 0))
            # ((burst_id . 0))
            sob = pmt.intern('new_burst')
            eob = pmt.intern('gone_burst')
            for ii, anno in enumerate(self.sigmf_metadata.get_annotations()):
                offset = anno.get('core:sample_start')
                end = offset + anno.get('core:sample_count')
                tag_dict = {'sample_rate': self.sample_rate, 'center_frequency': self.frequency, 'burst_id': ii}
                f_lower = anno.get('core:core:freq_lower_edge')
                f_upper = anno.get('core:core:freq_upper_edge')
                if f_lower and f_upper:
                    tag_dict['bandwidth'] = f_upper - f_lower
                    tag_dict['relative_frequency'] = ((f_upper - f_lower) / 2 - self.frequency) / self.sample_rate
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
