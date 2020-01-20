#!/usr/bin/env python3.7
# -*- coding: UTF-8 -*-

"""Read and parse simulated light-curves for different cadences"""

from os import environ
from pathlib import Path

DATA_DIR = Path(environ['CADENCE_SIMS'])
