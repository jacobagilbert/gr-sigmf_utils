#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 J. A. Gilbert
#
# SPDX-License-Identifier: GPL-3.0-or-later
#



from gnuradio import gr
from gnuradio import blocks
import pmt
import json
from os.path import isfile, splitext
import sigmf_utils
import numpy


VALID_SIGMF_INPUT_TYPES = ['ci16_le', 'cf32_le']
VALID_SIGMF_OUTPUT_TYPES = ['ci16_le', 'cf32_le']

class sigmf_file_source(gr.hier_block2):
    """
    This is a simple hier block that abstracts the process of loading a SigMF Recording
    and making it useful in GNU Radio. Data type conversion is handled by loading the
    SigMF Metadata file and automatically instantiating blocks to convert to the desired
    gnuradio output type.

    The rest of the parameters are similar to the file source:

        sigmf_filename: either the sigmf-meta or sigmf-data filename
        output_type:    gnuradio output type (sigmf data will be converted to this type)
        nsamples:       number of items to read from the file
        add_begin_tag:  key for tag to be placed on the first sample
        repeat:         repeat the data (`tags` generated on the start of each repeat)
        add_sigmf_tags: add tags for sigmf metadata fields and annotations
    """
    def __init__(self, sigmf_filename, output_type, nsamples, add_begin_tag, repeat, add_sigmf_tags):
        # Determine the SigMF meta and data files
        filebase, ext = splitext(sigmf_filename)
        if ext not in ['.sigmf-meta', '.sigmf-data', '.sigmf-']:
            filebase = sigmf_filename
        meta_filename = filebase + '.sigmf-meta'
        data_filename = filebase + '.sigmf-data'
        if not isfile(meta_filename):
            raise ValueError(f'SigMF meta file {meta_filename} does not exist')
        if not isfile(data_filename):
            raise ValueError(f'SigMF data file {data_filename} does not exist')

        # Parse the SigMF File for Metadata
        with open(meta_filename, 'r') as f:
            self.sigmf_metadata = json.load(f)
        if 'global' not in self.sigmf_metadata or 'captures' not in self.sigmf_metadata or 'annotations' not in self.sigmf_metadata:
            raise RuntimeError(f'Invalid SigMF Metadata, missing required top level object')

        # Setup and validate the data types
        input_type = self.sigmf_metadata['global'].get('core:datatype')
        if input_type not in VALID_SIGMF_INPUT_TYPES:
            raise ValueError(f'This block does not support the SigMF data type {input_type}')
        if output_type not in VALID_SIGMF_OUTPUT_TYPES:
            raise ValueError(f'This block does not support requested output type {output_type}')
        input_size = 2 if input_type == 'ci16_le' else 8 # cf32_le
        output_size = gr.sizeof_short if output_type == 'ci16_le' else gr.sizeof_gr_complex

        # Construct the hier block
        gr.hier_block2.__init__(self,
            "sigmf_file_source",
            gr.io_signature(0, 0, 0),               # Input signature
            gr.io_signature(1, 1, output_size))     # Output signature
        self.log = gr.logger('gr_log.' + self.to_basic_block().alias())
        self.log.info(f'SigMF File Source using metafile: {meta_filename}')
        self.log.info(f'SigMF File Source reading data of type {input_type}, producing data of type {output_type}')

        ##################################################
        # Blocks and Connections
        ##################################################
        self.file_source = blocks.file_source(input_size, data_filename, repeat, 0, nsamples)
        self.file_source.set_begin_tag(add_begin_tag)
        if add_sigmf_tags:
            tag_type = numpy.int16 if output_type == 'ci16_le' else numpy.complex64
            self.add_tags = sigmf_utils.add_tags_from_sigmf(tag_type, meta_filename, True)

        if input_type == output_type:
            if add_sigmf_tags:
                self.connect((self.file_source, 0), (self.add_tags, 0), (self, 0))
            else:
                self.connect((self.file_source, 0), (self, 0))

        elif input_type == 'ci16_le' and output_type == 'cf32_le':
            self.ishort_to_complex = blocks.interleaved_short_to_complex(False, False, pow(2,15))
            if add_sigmf_tags:
                self.connect((self.file_source, 0), (self.ishort_to_complex, 0), (self.add_tags, 0), (self, 0))
            else:
                self.connect((self.file_source, 0), (self.ishort_to_complex, 0), (self, 0))

        elif input_type == 'cf32_le' and output_type == 'ci16_le':
            self.complex_to_ishort = blocks.complex_to_interleaved_short(False, pow(2,15))
            if add_sigmf_tags:
                self.connect((self.file_source, 0), (self.complex_to_ishort, 0), (self.add_tags, 0), (self, 0))
            else:
                self.connect((self.file_source, 0), (self.complex_to_ishort, 0), (self, 0))

        else:
            raise RuntimeError(f'illegal combination of input/output {input_type} / {output_type}')


