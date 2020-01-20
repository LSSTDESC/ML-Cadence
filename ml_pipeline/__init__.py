#!/usr/bin/env python3.7
# -*- coding: UTF-8 -*-

from os import environ as _environ
from warnings import warn as _warn

if 'CADENCE_SIMS' not in _environ:
    _warn(
        'Could not find path of simulated data in the current environment. '
        'Please set the ``CADENCE_SIMS`` variable.')
