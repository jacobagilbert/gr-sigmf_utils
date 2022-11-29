#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 J. A. Gilbert
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

def get_capture_metadata(captures, sample_number, key=None):
    """
    Iterate over the captures array to determine which capture a given sample
    corresponds to. Will return metadata for a particular key, or the entire
    capture if the key is not given.
    """
    return_val = None
    for index, capture in enumerate(captures):
        if capture.get('core:sample_start') > sample_number:
            break
        elif key is None:
            return_val = capture
        else:
            return_val = capture.get(key, return_val)
    return return_val


def check_metadata(metadata):
    """
    Will ensure that the top level keys exist and are of the correct type, and that
    the basic required objects exist.
    """
    if not isinstance(metadata.get('global'), dict):
        raise ValueError(f'Invalid SigMF Metadata, missing `global` dictionary object')
    else:
        if metadata['global'].get('core:sample_rate') is None:
            raise ValueError(f'Invalid SigMF `global` Metadata, missing `core:sample_rate`')
        if metadata['global'].get('core:datatype') is None:
            raise ValueError(f'Invalid SigMF `global` Metadata, missing `core:datatype`')

    if not isinstance(metadata.get('captures'), list):
        raise ValueError(f'Invalid SigMF Metadata, missing `captures` list')
    else:
        for idx, capture in enumerate(metadata['captures']):
            if not isinstance(capture, dict):
                raise ValueError(f'Invalid SigMF Capture {idx}, not a dictionary object')
            else:
                if capture.get('core:sample_start') is None:
                    raise ValueError(f'Invalid SigMF Capture {idx}, missing sample_start')

    if not isinstance(metadata.get('annotations'), list):
        raise ValueError(f'Invalid SigMF Metadata, missing `annotations` list')
    else:
        for idx, annotation in enumerate(metadata['annotations']):
            if not isinstance(annotation, dict):
                raise ValueError(f'Invalid SigMF Annotation {idx}, not a dictionary object')
            else:
                if annotation.get('core:sample_start') is None:
                    raise ValueError(f'Invalid SigMF Annotation {idx}, missing sample_start')
