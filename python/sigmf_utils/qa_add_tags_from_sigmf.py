#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 J. A. Gilbert
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr, gr_unittest
# from gnuradio import blocks
from gnuradio.sigmf_utils import add_tags_from_sigmf
import numpy as np

class qa_add_tags_from_sigmf(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        md = {'global':{'core:sample_rate':1e6, 'core:datatype':'ci16_le'}, 'captures':[], 'annotations':[]}
        instance = add_tags_from_sigmf(np.int16, md)

    def test_001_descriptive_test_name(self):
        # set up fg
        self.tb.run()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_add_tags_from_sigmf)
