# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018 Adam Erispaha
#
# Licensed under the terms of the BSD2 License
# See LICENSE.txt for details
# -----------------------------------------------------------------------------
"""SWMM5 test models."""

# Standard library imports
import os

DATA_PATH = os.path.abspath(os.path.dirname(__file__))

# Test models paths
MODEL_FULL_FEATURES_PATH = os.path.join(DATA_PATH, 'model_full_features.inp')
MODEL_BROWARD_COUNTY_PATH = os.path.join(DATA_PATH, 'RUNOFF46_SW5.INP')
