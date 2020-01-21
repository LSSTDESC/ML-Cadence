#!/usr/bin/env python3.7
# -*- coding: UTF-8 -*-

"""This package provides functionality for analyzing simulated light-curves
for different LSST cadences with ``snmachine``.

Usage Example
-------------

>>> from snmachine import snfeatures
>>>
>>> from ml_pipeline.data import CadenceData
>>> from ml_pipeline.classification import extract_features
>>>
>>> # Read in data for a given cadence
>>> data_set = CadenceData('alt_sched', '/parent/directory/of/fits/files')
>>>
>>> # Retrieve a single light-curve
>>> demo_sn_id = data_set.object_names[0]
>>> demo_lightcurve = data_set.get_lightcurve(demo_sn_id)
>>> print(demo_lightcurve)
>>>
>>> # Perform feature extraction
>>> mod1Feats = snfeatures.ParametricFeatures('newling', sampler='leastsq')
>>> f = extract_features(mod1Feats, data_set, cache_dir='./')
"""

from os import environ as _environ
from warnings import warn as _warn

if 'CADENCE_SIMS' not in _environ:
    _warn(
        'Could not find path of simulated data in the current environment. '
        'Please set the ``CADENCE_SIMS`` variable.')
