import os

import pytest
import tempfile
import pandas as pd
import swmmio
import swmmio.utils.functions
import swmmio.utils.text
from swmmio.tests.data import MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES__NET_PATH, MODEL_A_PATH, MODEL_EX_1, MODEL_EX_1B
from swmmio import Model, dataframe_from_inp

from swmmio.utils.dataframes import get_link_coords
from swmmio.utils.text import get_rpt_sections_details, get_inp_sections_details


@pytest.fixture
def test_model_01():
    return Model(MODEL_FULL_FEATURES_XY)


@pytest.fixture
def test_model_02():
    return Model(MODEL_FULL_FEATURES__NET_PATH)


def test_complete_headers(test_model_01):
    headers = swmmio.utils.text.get_inp_sections_details(test_model_01.inp.path)
    print (list(headers.keys()))
    sections_in_inp = [
        'TITLE', 'OPTIONS', 'EVAPORATION', 'RAINGAGES', 'SUBCATCHMENTS', 'SUBAREAS', 'INFILTRATION',
        'JUNCTIONS', 'OUTFALLS', 'STORAGE', 'CONDUITS', 'PUMPS', 'WEIRS', 'XSECTIONS', 'INFLOWS',
        'CURVES', 'TIMESERIES', 'REPORT', 'TAGS', 'MAP', 'COORDINATES', 'VERTICES', 'POLYGONS',
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


@pytest.mark.uses_geopandas
def test_dataframe_composite(test_model_02):
    m = test_model_02
    links = m.links

    feat = links.geojson[2]
    assert feat['properties']['Name'] == '1'
    assert feat['properties']['MaxQ'] == 2.54

    links_gdf = links.geodataframe
    assert links_gdf.index[2] == '1'
    assert links_gdf.loc['1', 'MaxQ'] == 2.54


def test_model_section():
    m = swmmio.Model(MODEL_FULL_FEATURES_XY)

    def pumps_old_method(model):
        """
        collect all useful and available data related model pumps and
        organize in one dataframe.
        """

        # check if this has been done already and return that data accordingly
        if model._pumps_df is not None:
            return model._pumps_df

        # parse out the main objects of this model
        inp = model.inp

        # create dataframes of relevant sections from the INP
        pumps_df = dataframe_from_inp(inp.path, "[PUMPS]")
        if pumps_df.empty:
            return pd.DataFrame()

        # add conduit coordinates
        xys = pumps_df.apply(lambda r: get_link_coords(r, inp.coordinates, inp.vertices), axis=1)
        df = pumps_df.assign(coords=xys.map(lambda x: x[0]))
        df.InletNode = df.InletNode.astype(str)
        df.OutletNode = df.OutletNode.astype(str)

        model._pumps_df = df

        return df

    pumps_old_method = pumps_old_method(m)
    pumps = m.pumps()

    assert(pumps_old_method.equals(pumps))


def test_subcatchment_composite(test_model_02):

    subs = test_model_02.subcatchments
    assert subs.dataframe.loc['S3', 'Outlet'] == 'j3'
    assert subs.dataframe['TotalRunoffIn'].sum() == pytest.approx(2.45, 0.001)


def test_remove_model_section():

    with tempfile.TemporaryDirectory() as tempdir:
        m1 = swmmio.Model(MODEL_A_PATH)

        # create a copy of the model without subcatchments
        # m1.inp.infiltration = m1.inp.infiltration.iloc[0:0]
        m1.inp.subcatchments = m1.inp.subcatchments.iloc[0:0]
        # m1.inp.subareas = m1.inp.subareas.iloc[0:0]
        # m1.inp.polygons = m1.inp.polygons.iloc[0:0]

        # save to temp location
        temp_inp = os.path.join(tempdir, f'{m1.inp.name}.inp')
        m1.inp.save(temp_inp)

        m2 = swmmio.Model(temp_inp)

        sects1 = get_inp_sections_details(m1.inp.path)
        sects2 = get_inp_sections_details(m2.inp.path)

        # confirm saving a copy retains all sections except those removed
        assert ['SUBCATCHMENTS'] == [x for x in sects1 if x not in sects2]

        # confirm subcatchments returns an empty df
        assert m2.subcatchments.dataframe.empty


def test_example_1():
    model = swmmio.Model(MODEL_EX_1)
    element_types = ['nodes', 'links', 'subcatchments']
    elem_dict = {element: model.__getattribute__(element).geojson for element in element_types}
    swmm_version = model.rpt.swmm_version
    assert(swmm_version['major'] == 5)
    assert(swmm_version['minor'] == 1)
    assert(swmm_version['patch'] == 12)

    model_b = swmmio.Model(MODEL_EX_1B)
    swmm_version = model_b.rpt.swmm_version
    assert(swmm_version['patch'] == 13)
    elem_dict = {element: model_b.__getattribute__(element).geojson for element in element_types}

    subs = model.subcatchments.dataframe
    assert subs['TotalInfil'].sum() == pytest.approx(12.59, rel=0.001)
    assert subs['TotalRunoffMG'].sum() == pytest.approx(2.05, rel=0.001)

    # access lower level api
    peak_runoff = model.rpt.subcatchment_runoff_summary['PeakRunoff']
    assert peak_runoff.values == pytest.approx([4.66, 4.52, 2.45, 2.45, 6.56, 1.5, 0.79, 1.33], rel=0.001)
    assert peak_runoff.values == pytest.approx(subs['PeakRunoff'].values, rel=0.001)

def test_get_set_timeseries(test_model_02):

    ts = test_model_02.inp.timeseries
    assert(all(ts.columns == ['Date', 'Time', 'Value']))
    assert(ts.loc['TS2'].Date == 'FILE')
    assert('"' in ts.loc['TS2'].Value)
    assert(ts.Value.isnull().sum() == 0)
    print (ts)