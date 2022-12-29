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
MODEL_A_PATH = os.path.join(DATA_PATH, 'model_state_plane.inp')
MODEL_FULL_FEATURES_PATH = os.path.join(DATA_PATH, 'model_full_features.inp')
MODEL_FULL_FEATURES_XY = os.path.join(
    DATA_PATH, 'model_full_features_network_xy.inp')
MODEL_FULL_FEATURES_XY_B = os.path.join(DATA_PATH, 'model_full_features_b.inp')
MODEL_FULL_FEATURES__NET_PATH = os.path.join(
    DATA_PATH, 'model_full_features_network.inp')
MODEL_FULL_FEATURES_INVALID = os.path.join(DATA_PATH, 'invalid_model.inp')
MODEL_GREEN_AMPT = os.path.join(DATA_PATH, 'model_green_ampt.inp')
MODEL_MOD_GREEN_AMPT = os.path.join(DATA_PATH, 'model_mod_green_ampt.inp')
MODEL_CURVE_NUMBER = os.path.join(DATA_PATH, 'model_curve_num.inp')
MODEL_MOD_HORTON = os.path.join(DATA_PATH, 'model_mod_horton.inp')
MODEL_EX_1 = os.path.join(DATA_PATH, 'Example1.inp')
MODEL_EX_1B = os.path.join(DATA_PATH, 'Example1b.inp')
MODEL_EXAMPLE6 = os.path.join(DATA_PATH, 'Example6.inp')
MODEL_EX_1_PARALLEL_LOOP = os.path.join(DATA_PATH, 'Example1_parallel_loop.inp')
MODEL_INFILTRAION_PARSE_FAILURE = os.path.join(DATA_PATH, 'model-with-infiltration-parse-failure.inp')

# test rpt paths
RPT_FULL_FEATURES = os.path.join(DATA_PATH, 'model_full_features_network.rpt')
OWA_RPT_EXAMPLE = os.path.join(DATA_PATH, 'owa-rpt-example.rpt')

# version control test models
MODEL_XSECTION_BASELINE = os.path.join(DATA_PATH, 'baseline_test.inp')
MODEL_XSECTION_ALT_01 = os.path.join(DATA_PATH, 'alt_test1.inp')
MODEL_XSECTION_ALT_02 = os.path.join(DATA_PATH, 'alt_test2.inp')
MODEL_XSECTION_ALT_03 = os.path.join(DATA_PATH, 'alt_test3.inp')
MODEL_BLANK = os.path.join(DATA_PATH, 'model_blank_01.inp')
BUILD_INSTR_01 = os.path.join(DATA_PATH, 'test_build_instructions_01.txt')

df_test_coordinates_csv = os.path.join(DATA_PATH, 'df_test_coordinates.csv')
OUTFALLS_MODIFIED = os.path.join(DATA_PATH, 'outfalls_modified_10.csv')
