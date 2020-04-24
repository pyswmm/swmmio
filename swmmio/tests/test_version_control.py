import swmmio.utils.functions
import swmmio.utils.text
from swmmio.tests.data import (DATA_PATH, MODEL_XSECTION_BASELINE,
                               MODEL_FULL_FEATURES_XY, MODEL_XSECTION_ALT_03,
                               OUTFALLS_MODIFIED, BUILD_INSTR_01, MODEL_FULL_FEATURES_XY_B, MODEL_BLANK)
from swmmio.version_control import utils as vc_utils
from swmmio.version_control import inp
from swmmio.version_control.inp import INPSectionDiff, merge_models
from swmmio.utils.dataframes import dataframe_from_inp

import os
import shutil
import pytest


def makedirs(newdir):
    """
    replicate this in Py2 campatible way
    os.makedirs(temp_vc_dir_02, exist_ok=True)
    """
    if os.path.exists(newdir):
        shutil.rmtree(newdir)
    os.makedirs(newdir)


def test_complete_inp_headers():
    headers = [
        'TITLE', 'OPTIONS', 'EVAPORATION', 'JUNCTIONS', 'OUTFALLS',
        'CONDUITS', 'XSECTIONS', 'DWF', 'REPORT', 'TAGS', 'MAP',
        'COORDINATES', 'VERTICES',
    ]

    h1 = swmmio.utils.text.get_inp_sections_details(MODEL_XSECTION_BASELINE)

    assert (all(h in h1 for h in headers))
    assert (list(h1.keys()) == headers)


def test_create_inp_build_instructions():
    temp_vc_dir_01 = os.path.join(DATA_PATH, 'vc_dir')
    temp_vc_dir_02 = os.path.join(DATA_PATH, 'vc root with spaces')
    temp_vc_dir_03 = os.path.join(temp_vc_dir_02, 'vc_dir')
    inp.create_inp_build_instructions(MODEL_XSECTION_BASELINE,
                                      MODEL_XSECTION_ALT_03,
                                      temp_vc_dir_01,
                                      'test_version_id', 'cool comments')

    latest_bi = vc_utils.newest_file(temp_vc_dir_01)
    bi = inp.BuildInstructions(latest_bi)
    print(bi.instructions)
    juncs = bi.instructions['JUNCTIONS']
    print(juncs)
    assert (all(j in juncs.altered.index for j in [
        'dummy_node1', 'dummy_node5']))

    # assert (filecmp.cmp(latest_bi, BUILD_INSTR_01))
    shutil.rmtree(temp_vc_dir_01)

    # reproduce test with same files in a directory structure with spaces in path
    makedirs(temp_vc_dir_02)
    shutil.copy(MODEL_XSECTION_BASELINE, temp_vc_dir_02)
    shutil.copy(MODEL_XSECTION_ALT_03, temp_vc_dir_02)
    MODEL_XSECTION_BASELINE_spaces = os.path.join(temp_vc_dir_02, MODEL_XSECTION_BASELINE)
    MODEL_XSECTION_ALT_03_spaces = os.path.join(temp_vc_dir_02, MODEL_XSECTION_ALT_03)

    inp.create_inp_build_instructions(MODEL_XSECTION_BASELINE_spaces,
                                      MODEL_XSECTION_ALT_03_spaces,
                                      temp_vc_dir_03,
                                      'test_version_id', 'cool comments')

    latest_bi_spaces = vc_utils.newest_file(temp_vc_dir_03)
    bi_sp = inp.BuildInstructions(latest_bi_spaces)

    juncs_sp = bi_sp.instructions['JUNCTIONS']
    print(juncs_sp.altered)
    assert (all(j in juncs_sp.altered.index for j in [
        'dummy_node1', 'dummy_node5']))

    shutil.rmtree(temp_vc_dir_02)


def test_inp_diff_from_bi():

    change = INPSectionDiff(build_instr_file=BUILD_INSTR_01, section='JUNCTIONS')

    alt_juncs = change.altered
    assert alt_juncs.loc['dummy_node1', 'InvertElev'] == pytest.approx(-15, 0.01)
    assert alt_juncs.loc['dummy_node5', 'InvertElev'] == pytest.approx(-6.96, 0.01)

    # test with spaces in path
    temp_dir_01 = os.path.join(DATA_PATH, 'path with spaces')
    makedirs(temp_dir_01)
    shutil.copy(BUILD_INSTR_01, temp_dir_01)
    BUILD_INSTR_01_spaces = os.path.join(temp_dir_01, BUILD_INSTR_01)

    change = INPSectionDiff(build_instr_file=BUILD_INSTR_01_spaces, section='[JUNCTIONS]')

    alt_juncs = change.altered
    assert alt_juncs.loc['dummy_node1', 'InvertElev'] == pytest.approx(-15, 0.01)
    assert alt_juncs.loc['dummy_node5', 'InvertElev'] == pytest.approx(-6.96, 0.01)

    # test with parent models in directory structure with spaces in path
    temp_dir_02 = os.path.join(DATA_PATH, 'root with spaces')
    temp_dir_03 = os.path.join(temp_dir_02, 'vc_dir')
    makedirs(temp_dir_02)
    shutil.copy(MODEL_XSECTION_BASELINE, temp_dir_02)
    shutil.copy(MODEL_XSECTION_ALT_03, temp_dir_02)
    MODEL_XSECTION_BASELINE_spaces = os.path.join(temp_dir_02, MODEL_XSECTION_BASELINE)
    MODEL_XSECTION_ALT_03_spaces = os.path.join(temp_dir_02, MODEL_XSECTION_ALT_03)

    inp.create_inp_build_instructions(MODEL_XSECTION_BASELINE_spaces,
                                      MODEL_XSECTION_ALT_03_spaces,
                                      temp_dir_03,
                                      'test_version_id', 'cool comments')

    latest_bi_spaces = vc_utils.newest_file(temp_dir_03)
    change = INPSectionDiff(build_instr_file=latest_bi_spaces, section='[JUNCTIONS]')
    alt_juncs = change.altered
    assert alt_juncs.loc['dummy_node1', 'InvertElev'] == pytest.approx(-15, 0.01)
    assert alt_juncs.loc['dummy_node5', 'InvertElev'] == pytest.approx(-6.96, 0.01)

    shutil.rmtree(temp_dir_01)
    shutil.rmtree(temp_dir_02)


def test_add_models():
    """
    create build instructions for entire models with respect to a blank (empty) model
    such that BIs include additions for each model element. This is experimental.
    """

    tdir = os.path.join(DATA_PATH, 'vc_dir')

    bi_b = inp.create_inp_build_instructions(MODEL_BLANK,
                                      MODEL_FULL_FEATURES_XY_B,
                                      tdir,
                                      'from_blank_model_b', 'cool comments')
    bi_a = inp.create_inp_build_instructions(MODEL_BLANK,
                                      MODEL_FULL_FEATURES_XY,
                                      tdir,
                                      'from_blank_model_a', 'should have all we need')

    bi_final = bi_a + bi_b
    bi_final.save(tdir, 'merged-build-instr.txt')
    bi_final.build(MODEL_BLANK, os.path.join(tdir, 'merged-model.inp'))


def test_merge_models():

    from swmmio import Model
    import pandas as pd
    # MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES_XY_B
    target_merged_model_ab = os.path.join(DATA_PATH, 'merged-model-test-ab.inp')
    target_merged_model_ba = os.path.join(DATA_PATH, 'merged-model-test-ba.inp')
    merged_model_ab = merge_models(MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES_XY_B, target_merged_model_ab)
    merged_model_ba = merge_models(MODEL_FULL_FEATURES_XY_B, MODEL_FULL_FEATURES_XY, target_merged_model_ba)
    ma = Model(MODEL_FULL_FEATURES_XY)
    mb = Model(MODEL_FULL_FEATURES_XY_B)

    conds_ab = pd.concat([ma.inp.conduits, mb.inp.conduits]).sort_index()
    mab = Model(merged_model_ab)
    mba = Model(merged_model_ba)
    conds_ab_merged = mab.inp.conduits.sort_index()
    conds_ba_merged = mba.inp.conduits.sort_index()

    assert conds_ab.equals(conds_ab_merged)
    assert conds_ab.equals(conds_ba_merged)

    os.remove(target_merged_model_ab)
    os.remove(target_merged_model_ba)


def test_modify_model():
    from swmmio.utils.modify_model import replace_inp_section
    from swmmio import Model
    import pandas as pd
    import os
    import shutil

    # initialize a baseline model object
    baseline = Model(MODEL_FULL_FEATURES_XY)
    of_test = pd.read_csv(OUTFALLS_MODIFIED, index_col=0)
    rise = 10.0  # set the starting sea level rise condition

    # create a dataframe of the model's outfalls
    outfalls = dataframe_from_inp(baseline.inp.path, '[OUTFALLS]')

    # add the current rise to the outfalls' stage elevation
    outfalls['OutfallType'] = 'FIXED'
    outfalls.loc[:, 'InvertElev'] = pd.to_numeric(outfalls.loc[:, 'InvertElev']) + rise
    of_test.loc[:, 'InvertElev'] = pd.to_numeric(of_test.loc[:, 'InvertElev'])

    # copy the base model into a new directory
    newdir = os.path.join(baseline.inp.dir, str(rise))
    makedirs(newdir)
    newfilepath = os.path.join(newdir, baseline.inp.name + "_" + str(rise) + '_SLR.inp')
    shutil.copyfile(baseline.inp.path, newfilepath)

    # Overwrite the OUTFALLS section of the new model with the adjusted data
    replace_inp_section(newfilepath, '[OUTFALLS]', outfalls)

    m2 = Model(newfilepath)
    of2 = m2.inp.outfalls
    shutil.rmtree(newdir)
    # of2.to_csv(os.path.join(newdir, baseline.inp.name + "_new_outfalls.csv"))
    assert (of2.loc['J4', 'InvertElev'].round(1) == of_test.loc['J4', 'InvertElev'].round(1))
