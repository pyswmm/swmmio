from swmmio.tests.data import MODEL_FULL_FEATURES__NET_PATH
from swmmio import Model
from swmmio.elements import ModelSection
from swmmio.utils import functions
import pytest


@pytest.fixture
def test_model():
    return Model(MODEL_FULL_FEATURES__NET_PATH)


def test_model_section(test_model):
    group = ModelSection(test_model, 'junctions')
    print(group)

    bayside = Model(MODEL_FULL_FEATURES__NET_PATH)

    a = bayside.inp.junctions
    print(a)
    # tsb_ids = [1213, 13131, 232131, 12313]
    # tsbs = bayside.conduits(data=['MaxDepth, MaxQ', 'geometry'])


def test_complete_headers(test_model):
    headers = functions.complete_inp_headers(test_model.inp.path)
    sections_in_inp = [
        '[TITLE]', '[OPTIONS]', '[EVAPORATION]', '[RAINGAGES]', '[SUBCATCHMENTS]', '[SUBAREAS]', '[INFILTRATION]',
        '[JUNCTIONS]', '[OUTFALLS]', '[STORAGE]', '[CONDUITS]', '[PUMPS]', '[WEIRS]', '[XSECTIONS]', '[INFLOWS]',
        '[CURVES]', '[TIMESERIES]', '[REPORT]', '[TAGS]', '[MAP]', '[COORDINATES]', '[VERTICES]', '[Polygons]',
        '[SYMBOLS]'
    ]
    assert (all(section in headers['headers'] for section in sections_in_inp))
