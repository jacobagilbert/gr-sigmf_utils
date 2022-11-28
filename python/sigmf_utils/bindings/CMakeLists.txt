# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT sigmf_utils_sources)
    MESSAGE(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT sigmf_utils_sources)

########################################################################
# Check for pygccxml
########################################################################
GR_PYTHON_CHECK_MODULE_RAW(
    "pygccxml"
    "import pygccxml"
    PYGCCXML_FOUND
    )

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND sigmf_utils_python_files
    python_bindings.cc)

GR_PYBIND_MAKE_OOT(sigmf_utils
   ../../..
   gr::sigmf_utils
   "${sigmf_utils_python_files}")

# copy bindings extension for use in QA test module
add_custom_command(TARGET sigmf_utils_python POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:sigmf_utils_python>
    ${PROJECT_BINARY_DIR}/test_modules/gnuradio/sigmf_utils/
)

install(TARGETS sigmf_utils_python DESTINATION ${GR_PYTHON_DIR}/gnuradio/sigmf_utils COMPONENT pythonapi)
