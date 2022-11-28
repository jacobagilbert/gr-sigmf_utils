#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright J. A. Gilbert, 2022
#
# SPDX-License-Identifier: GPL-3.0-or-later
#



from gnuradio import gr
from gnuradio import blocks
import pmt
from sigmf import sigmffile
from os.path import isfile, splitext

VALID_SIGMF_INPUT_TYPES = ['ci16_le', 'cf32_le']
VALID_SIGMF_OUTPUT_TYPES = ['ci16_le', 'cf32_le']

class sigmf_file_source(gr.hier_block2):
    """
    docstring for block sigmf_file_source
    """
    def __init__(self, sigmf_filename, output_type, nsamples, tags, repeat):
        if output_type not in VALID_SIGMF_OUTPUT_TYPES:
            print(f'ERROR, This block does not support requested output type {output_type}')

        filebase, ext = splitext(sigmf_filename)
        if ext not in ['.sigmf-meta', '.sigmf-data', '.sigmf-']:
            filebase = sigmf_filename
        meta_filename = filebase + '.sigmf-meta'
        data_filename = filebase + '.sigmf-data'
        if not isfile(meta_filename):
            raise RuntimeError(f'SigMF meta file {meta_filename} does not exist')
        if not isfile(data_filename):
            raise RuntimeError(f'SigMF data file {data_filename} does not exist')
        print(f'Using SigMF file: {meta_filename}')
        # Parse the SigMF File for Metadata
        sigmf_metadata = sigmffile.fromfile(meta_filename)
        input_type = sigmf_metadata.get_global_field('core:datatype')
        if input_type not in VALID_SIGMF_INPUT_TYPES:
            print(f'ERROR, This block does not support requested input type {input_type}')
        input_size = sigmf_metadata.get_sample_size()
        if input_type == 'ci16_le':
            # for short complex tyoes, GR will read these one I or Q part at a time
            input_size //= 2

        output_size = gr.sizeof_gr_complex
        if output_type == 'ci16_le':
            output_size = gr.sizeof_short

        print(f'SigMF Source is reading data of type {input_type}({input_size}) and producing data of type {output_type}({output_size})')
        gr.hier_block2.__init__(self,
            "sigmf_file_source",
            gr.io_signature(0, 0, 0),               # Input signature
            gr.io_signature(1, 1, output_size))   # Output signature

        ##################################################
        # Blocks and Connections
        ##################################################
        self.file_source = blocks.file_source(input_size, data_filename, repeat, 0, nsamples)
        self.file_source.set_begin_tag(tags)
        
        if input_type == output_type:
            self.connect((self.file_source, 0), (self, 0))
        elif input_type == 'ci16_le' and output_type == 'cf32_le':
            self.ishort_to_complex = blocks.interleaved_short_to_complex(False, False, pow(2,15))
            self.connect((self.file_source, 0), (self.ishort_to_complex, 0))
            self.connect((self.ishort_to_complex, 0), (self, 0))
        elif input_type == 'cf32_le' and output_type == 'ci16_le':
            self.complex_to_ishort = blocks.complex_to_interleaved_short(False, pow(2,15))        
            self.connect((self.file_source, 0), (self.complex_to_ishort, 0))
            self.connect((self.complex_to_ishort, 0), (self, 0))
        else:
            raise RuntimeError(f'illegal combination of input/output {input_type} / {output_type}')

