#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 J. A. Gilbert
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr, gr_unittest
# from gnuradio import blocks
from gnuradio.sigmf_utils import tag_meta_writer

class qa_tag_meta_writer(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        instance = tag_meta_writer('/tmp/a', 900e6, 40e6, 'burst', 'ci16_le')

    def test_001_descriptive_test_name(self):
        # set up fg
        self.tb.run()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_tag_meta_writer)
