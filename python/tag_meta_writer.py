#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright J. A. Gilbert, 2022
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy
from gnuradio import gr
import json
import pmt
from os.path import splitext
from math import isnan, isinf


class tag_meta_writer(gr.sync_block):
    """
    This block takes GR stream tags with gr-fhss_utils style metadata and
    produces SigMF annotations from them.
    """
    def __init__(self, filename, freq, rate, label, dtype):
        gr.sync_block.__init__(self,
            name="tag_meta_writer",
            in_sig=[numpy.complex64],
            out_sig=None)

        self.d_filename = filename
        if not filename.endswith('.sigmf-meta'):
            pre, ext = splitext(filename)
            self.d_filename = pre + '.sigmf-meta'
            gr.log.warn("SigMF metadata filename does not end with `sigmf-meta` - using " + self.d_filename)

        self.freq = freq
        self.rate = rate
        self.soo = 0
        self.bw_min = rate/1000.0
        self.label = label
        
        self.in_progress_tags = {}

        self.initialize_sigmf_dict([{'core:sample_start': 0, 'core:frequency': freq}],
                                   {'core:datatype': dtype, 'core:sample_rate': rate, 'antenna:gain': 0})

    def stop(self):
        try:
            f = open(self.d_filename, 'w+')
            f.write(json.dumps(self.d_dict,indent=4))
            f.close()
            print(f"wrote file {self.d_filename} with {len(self.d_dict['annotations'])} annotations")
        except IOError as e:
            print("ERROR: could write to {}".format(self.d_filename), "because", e)
            quit()

        return True

    def initialize_sigmf_dict(self, sigmf_captures, sigmf_global, sigmf_annotations = []):
        self.d_dict = {}
        self.d_dict['captures'] = sigmf_captures
        self.d_dict['global'] = sigmf_global
        self.d_dict['annotations'] = sigmf_annotationss

    def add_annotation(self, burst_id, end_offset):
        anno = {}
        metadata = self.in_progress_tags.pop(burst_id, None)
        if metadata is None:
            print(f'\tERROR: attempted to retrieve metadata for burst {burst_id} that has not been enqueued yet!!')
            return

        anno['core:sample_start'] = metadata.get('sample_start', None)
        anno['core:sample_count'] = end_offset - metadata.get('sample_start', None)
        anno_center_freq = metadata.get('center_frequency', None) + metadata.get('sample_rate', None) * metadata.get('relative_frequency', None)
        anno['core:freq_upper_edge'] = anno_center_freq + metadata.get('bandwidth', None) / 2
        anno['core:freq_lower_edge'] = anno_center_freq - metadata.get('bandwidth', None) / 2
        anno['core:label'] = self.label
        self.d_dict['annotations'].append(anno)

    def work(self, input_items, output_items):
        in0 = input_items[0]

        tags = self.get_tags_in_window(0, 0, len(in0))
        # good tags have keys of `new_burst` or `gone_burst and values dictionaries respectively:
        # ((bandwidth . 263671) (noise_density . -153.272) (sample_rate . 4e+07) (magnitude . 62.6101) (center_frequency . 9.15e+08) (relative_frequency . 0.0878906) (burst_id . 0))
        # ((burst_id . 0))
        for tag in tags:
            try:
                val_dict = pmt.to_python(tag.value)
                val_dict['sample_start'] = tag.offset
                burst_id = val_dict.get('burst_id', None)
                if pmt.eqv(tag.key, pmt.intern("new_burst")) and burst_id is not None:
                    print(f'\t\tenqueueing burst {burst_id}')
                    self.in_progress_tags[burst_id] = val_dict
                elif pmt.eqv(tag.key, pmt.intern("gone_burst")) and burst_id is not None:
                    print(f'\t\twriting anno for burst {burst_id}')
                    self.add_annotation(burst_id, tag.offset)
            except:
                print(f'error processing tag...\n\tKEY: {tag.key}\n\tVAL: {tag.value}')
        return len(in0)



