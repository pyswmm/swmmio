from swmmio.tests.data import MODEL_FULL_FEATURES_PATH, MODEL_BROWARD_COUNTY_PATH
from swmmio import swmmio

def test_conduits_dataframe():

    m = swmmio.Model(MODEL_FULL_FEATURES_PATH)
    conduits = m.conduits()
    assert(list(conduits.index) == ['C1:C2'])
