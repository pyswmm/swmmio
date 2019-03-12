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
MODEL_FULL_FEATURES_XY = os.path.join(
    DATA_PATH, 'model_full_features_network_xy.inp')
MODEL_FULL_FEATURES__NET_PATH = os.path.join(
    DATA_PATH, 'model_full_features_network.inp')
MODEL_BROWARD_COUNTY_PATH = os.path.join(DATA_PATH, 'RUNOFF46_SW5.INP')

# version control test models
MODEL_XSECTION_BASELINE = os.path.join(DATA_PATH, 'baseline_test.inp')
MODEL_XSECTION_ALT_01 = os.path.join(DATA_PATH, 'alt_test1.inp')
MODEL_XSECTION_ALT_02 = os.path.join(DATA_PATH, 'alt_test2.inp')
MODEL_XSECTION_ALT_03 = os.path.join(DATA_PATH, 'alt_test3.inp')

df_test_coordinates_csv = os.path.join(DATA_PATH, 'df_test_coordinates.csv')
