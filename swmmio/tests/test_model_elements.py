import swmmio.utils.functions
import swmmio.utils.text
from swmmio.tests.data import MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES__NET_PATH
from swmmio import Model
from swmmio.elements import ModelSection
from swmmio.utils import functions
import pytest
from swmmio.utils.text import get_rpt_sections_details


@pytest.fixture
def test_model_01():
    return Model(MODEL_FULL_FEATURES_XY)


@pytest.fixture
def test_model_02():
    return Model(MODEL_FULL_FEATURES__NET_PATH)


def test_model_section(test_model_01):
    group = ModelSection(test_model_01, 'junctions')
    print(group)

    bayside = Model(MODEL_FULL_FEATURES__NET_PATH)

    a = bayside.inp.junctions
    print(a)
    # tsb_ids = [1213, 13131, 232131, 12313]
    # tsbs = bayside.conduits(data=['MaxDepth, MaxQ', 'geometry'])


def test_complete_headers(test_model_01):
    headers = swmmio.utils.text.get_inp_sections_details(test_model_01.inp.path)
    print (list(headers.keys()))
    sections_in_inp = [
        'TITLE', 'OPTIONS', 'EVAPORATION', 'RAINGAGES', 'SUBCATCHMENTS', 'SUBAREAS', 'INFILTRATION',
        'JUNCTIONS', 'OUTFALLS', 'STORAGE', 'CONDUITS', 'PUMPS', 'WEIRS', 'XSECTIONS', 'INFLOWS',
        'CURVES', 'TIMESERIES', 'REPORT', 'TAGS', 'MAP', 'COORDINATES', 'VERTICES', 'Polygons',
        'SYMBOLS'
    ]
    assert (all(section in headers for section in sections_in_inp))


def test_complete_headers_rpt(test_model_02):

    headers = get_rpt_sections_details(test_model_02.rpt.path)
    sections_in_rpt = [
        'Link Flow Summary', 'Link Flow Summary', 'Subcatchment Summary',
        'Cross Section Summary', 'Link Summary'
    ]

    assert(all(section in headers for section in sections_in_rpt))
    assert headers['Link Summary']['columns'] == ['Name', 'FromNode', 'ToNode',
                                                  'Type', 'Length', 'SlopePerc',
                                                  'Roughness']


def test_get_set_curves(test_model_01):

    curves = test_model_01.inp.curves

    print (curves)
