from swmmio.tests.data import (MODEL_XSECTION_BASELINE, MODEL_FULL_FEATURES_PATH,
                               MODEL_XSECTION_ALT_02, MODEL_XSECTION_ALT_03, MODEL_BLANK)

from swmmio.version_control import utils as vc_utils
from swmmio.version_control import inp
from swmmio.utils import functions as funcs


def test_complete_inp_headers():

    headers = [
        '[TITLE]', '[OPTIONS]', '[EVAPORATION]', '[JUNCTIONS]', '[OUTFALLS]',
        '[CONDUITS]', '[XSECTIONS]', '[DWF]', '[REPORT]', '[TAGS]', '[MAP]',
        '[COORDINATES]', '[VERTICES]',
    ]

    h1 = funcs.complete_inp_headers(MODEL_XSECTION_BASELINE)

    assert(all(h in h1['headers'] for h in headers))
    assert(h1['order'] == headers)


def test_create_inp_build_instructions():

    inp.create_inp_build_instructions(MODEL_XSECTION_BASELINE,
                                      MODEL_XSECTION_ALT_03,
                                      'vc_dir',
                                      'test_version_id', 'cool comments')

    latest_bi = vc_utils.newest_file('vc_dir')
    bi = inp.BuildInstructions(latest_bi)

    juncs = bi.instructions['[JUNCTIONS]']
    assert(all(j in juncs.altered.index for j in [
           'dummy_node1', 'dummy_node5']))


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

