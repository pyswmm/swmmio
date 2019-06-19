from swmmio.tests.data import (DATA_PATH, MODEL_XSECTION_BASELINE,
                               MODEL_FULL_FEATURES_XY, MODEL_XSECTION_ALT_03,
                               OUTFALLS_MODIFIED, BUILD_INSTR_01)
from swmmio.version_control import utils as vc_utils
from swmmio.version_control import inp
from swmmio.utils import functions as funcs
import os
import filecmp
import shutil


def test_complete_inp_headers():
    headers = [
        '[TITLE]', '[OPTIONS]', '[EVAPORATION]', '[JUNCTIONS]', '[OUTFALLS]',
        '[CONDUITS]', '[XSECTIONS]', '[DWF]', '[REPORT]', '[TAGS]', '[MAP]',
        '[COORDINATES]', '[VERTICES]',
    ]

    h1 = funcs.complete_inp_headers(MODEL_XSECTION_BASELINE)

    assert (all(h in h1['headers'] for h in headers))
    assert (h1['order'] == headers)


def test_create_inp_build_instructions():
    temp_vc_dir = os.path.join(DATA_PATH, 'vc_dir')
    inp.create_inp_build_instructions(MODEL_XSECTION_BASELINE,
                                      MODEL_XSECTION_ALT_03,
                                      temp_vc_dir,
                                      'test_version_id', 'cool comments')

    latest_bi = vc_utils.newest_file(temp_vc_dir)
    bi = inp.BuildInstructions(latest_bi)

    juncs = bi.instructions['[JUNCTIONS]']
    assert (all(j in juncs.altered.index for j in [
        'dummy_node1', 'dummy_node5']))

    assert(filecmp.cmp(latest_bi, BUILD_INSTR_01))
    shutil.rmtree(temp_vc_dir)


# def test_add_models():
#     inp.create_inp_build_instructions(MODEL_BLANK,
#                                       MODEL_XSECTION_ALT_03,
#                                       'vc_dir',
#                                       'test_version_id', 'cool comments')
#     bi_1 = vc_utils.newest_file('vc_dir')
#     bi1 = inp.BuildInstructions(bi_1)
#
#     inp.create_inp_build_instructions(MODEL_BLANK,
#                                       MODEL_FULL_FEATURES_PATH,
#                                       'vc_dir',
#                                       'test_model_full_feat', 'cool comments')
#     bi_2 = vc_utils.newest_file('vc_dir')
#     bi2 = inp.BuildInstructions(bi_2)
#
#     bi3 = bi1 + bi2
#     bi3.build(MODEL_BLANK, 'added_model.inp')


def test_modify_model():
    from swmmio.utils.modify_model import replace_inp_section
    from swmmio import Model, create_dataframeINP
    import pandas as pd
    import os
    import shutil

    # initialize a baseline model object
    baseline = Model(MODEL_FULL_FEATURES_XY)
    of_test = pd.read_csv(OUTFALLS_MODIFIED, index_col=0)
    rise = 10.0  # set the starting sea level rise condition

    # create a dataframe of the model's outfalls
    outfalls = create_dataframeINP(baseline.inp.path, '[OUTFALLS]')

    # add the current rise to the outfalls' stage elevation
    outfalls['OutfallType'] = 'FIXED'
    outfalls.loc[:, 'InvertElev'] = pd.to_numeric(outfalls.loc[:, 'InvertElev']) + rise
    of_test.loc[:, 'InvertElev'] = pd.to_numeric(of_test.loc[:, 'InvertElev'])


    # copy the base model into a new directory
    newdir = os.path.join(baseline.inp.dir, str(rise))
    os.mkdir(newdir)
    newfilepath = os.path.join(newdir, baseline.inp.name + "_" + str(rise) + '_SLR.inp')
    shutil.copyfile(baseline.inp.path, newfilepath)

    # Overwrite the OUTFALLS section of the new model with the adjusted data
    replace_inp_section(newfilepath, '[OUTFALLS]', outfalls)

    m2 = Model(newfilepath)
    of2 = m2.inp.outfalls
    shutil.rmtree(newdir)
    # of2.to_csv(os.path.join(newdir, baseline.inp.name + "_new_outfalls.csv"))
    assert(of2.loc['J4', 'InvertElev'].round(1) == of_test.loc['J4', 'InvertElev'].round(1))
