#
# Copyright 2008,2009 Free Software Foundation, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

# The presence of this file turns this directory into a Python package

'''
This is the GNU Radio SIGMF_UTILS module. Place your Python package
description here (python/__init__.py).
'''
import os

# import pybind11 generated symbols into the sigmf_utils namespace
try:
    # this might fail if the module is python-only
    from .sigmf_utils_python import *
except ModuleNotFoundError:
    pass

# import any pure python here
from .pdu_meta_writer import pdu_meta_writer
from .tag_meta_writer import tag_meta_writer
from .sigmf_file_source import sigmf_file_source
from .add_tags_from_sigmf import add_tags_from_sigmf
#
