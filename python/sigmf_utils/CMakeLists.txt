# Copyright 2011 Free Software Foundation, Inc.
#
# This file was generated by gr_modtool, a tool from the GNU Radio framework
# This file is a part of gr-sigmf_utils
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Include python install macros
########################################################################
include(GrPython)
if(NOT PYTHONINTERP_FOUND)
    return()
endif()

add_subdirectory(bindings)

########################################################################
# Install python sources
########################################################################
GR_PYTHON_INSTALL(
    FILES
    __init__.py
    pdu_meta_writer.py
    tag_meta_writer.py
    sigmf_file_source.py
    add_tags_from_sigmf.py
    sigmf_tools.py
    DESTINATION ${GR_PYTHON_DIR}/gnuradio/sigmf_utils
)

########################################################################
# Handle the unit tests
########################################################################
include(GrTest)

set(GR_TEST_TARGET_DEPS gnuradio-sigmf_utils)

# Create a package directory that tests can import. It includes everything
# from `python/`.
add_custom_target(
  copy_module_for_tests ALL
  COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}
          ${PROJECT_BINARY_DIR}/test_modules/gnuradio/sigmf_utils/
)
GR_ADD_TEST(qa_pdu_meta_writer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_pdu_meta_writer.py)
GR_ADD_TEST(qa_tag_meta_writer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_tag_meta_writer.py)
GR_ADD_TEST(qa_sigmf_file_source ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_sigmf_file_source.py)
GR_ADD_TEST(qa_add_tags_from_sigmf ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_add_tags_from_sigmf.py)
