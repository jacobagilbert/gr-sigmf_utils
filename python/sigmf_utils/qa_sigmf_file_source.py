#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 J. A. Gilbert
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr, gr_unittest
# from gnuradio import blocks
from gnuradio.sigmf_utils import sigmf_file_source
import numpy as np
import pmt


class qa_sigmf_file_source(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        try:
            instance = sigmf_file_source('/tmp/x', np.complex64, 0, pmt.PMT_NIL, False, True)
        except ValueError:
            pass

    def test_001_descriptive_test_name(self):
        # set up fg
        self.tb.run()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_sigmf_file_source)
