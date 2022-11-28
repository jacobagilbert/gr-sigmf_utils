#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 J. A. Gilbert
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

def check_metadata(metadata):
    """
    Will ensure that the top level keys exist and are of the correct type, and that
    the basic required objects exist
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