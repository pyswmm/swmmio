from io import StringIO

from swmmio.elements import Links
from swmmio.tests.data import (MODEL_FULL_FEATURES_PATH, MODEL_FULL_FEATURES__NET_PATH,
                               BUILD_INSTR_01, MODEL_XSECTION_ALT_01, df_test_coordinates_csv,
                               MODEL_FULL_FEATURES_XY, DATA_PATH, MODEL_XSECTION_ALT_03,
                               MODEL_CURVE_NUMBER, MODEL_MOD_HORTON, MODEL_GREEN_AMPT, MODEL_MOD_GREEN_AMPT,
                               MODEL_INFILTRAION_PARSE_FAILURE, OWA_RPT_EXAMPLE)
from swmmio.utils.dataframes import (dataframe_from_rpt, dataframe_from_inp, dataframe_from_bi)
import swmmio

import pandas as pd
import pytest
import shutil
import os


@pytest.fixture
def test_model_01():
    return swmmio.Model(MODEL_FULL_FEATURES_XY)


@pytest.fixture
def test_model_02():
    return swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)


def makedirs(newdir):
    """
    replicate this in Py2 campatible way
    os.makedirs(temp_vc_dir_02, exist_ok=True)
    """
    if os.path.exists(newdir):
        shutil.rmtree(newdir)
    os.makedirs(newdir)


def test_dataframe_from_bi():

    bi_juncs = dataframe_from_bi(BUILD_INSTR_01, 'junctions')
    print(bi_juncs.to_string())
    assert bi_juncs.loc['dummy_node1', 'InvertElev'] == pytest.approx(-15.0, 0.01)
    assert bi_juncs.loc['dummy_node5', 'InvertElev'] == pytest.approx(-6.96, 0.01)

    assert bi_juncs.loc['dummy_node5', 'Comment'] == 'Altered'

    # test with spaces in path
    temp_dir_01 = os.path.join(DATA_PATH, 'path with spaces')
    makedirs(temp_dir_01)
    shutil.copy(BUILD_INSTR_01, temp_dir_01)
    BUILD_INSTR_01_spaces = os.path.join(temp_dir_01, BUILD_INSTR_01)

    bi_juncs = dataframe_from_bi(BUILD_INSTR_01_spaces, section='[JUNCTIONS]')
    assert bi_juncs.loc['dummy_node1', 'InvertElev'] == pytest.approx(-15, 0.01)
    assert bi_juncs.loc['dummy_node5', 'InvertElev'] == pytest.approx(-6.96, 0.01)
    shutil.rmtree(temp_dir_01)


def test_node_dataframe_from_rpt(test_model_02):
    m = test_model_02

    depth_summ = swmmio.dataframe_from_rpt(m.rpt.path, "Node Depth Summary")
    print('\n', depth_summ)
    inflo_summ = swmmio.dataframe_from_rpt(m.rpt.path, "Node Inflow Summary")
    print(inflo_summ)
    flood_summ = swmmio.dataframe_from_rpt(m.rpt.path, "Node Flooding Summary")
    print(flood_summ)

    assert (inflo_summ.loc['J3', 'TotalInflowV'] == 6.096)
    assert (inflo_summ.loc['J1', 'MaxTotalInflow'] == 3.52)

    assert (depth_summ.loc['J3', 'MaxNodeDepth'] == 1.64)
    assert (depth_summ.loc['4', 'MaxNodeDepth'] == 0.87)

    # need to ensure indices are strings always
    assert (flood_summ.loc['5', 'TotalFloodVol'] == 0)


def test_conduits_dataframe(test_model_01):
    m = swmmio.Model(MODEL_FULL_FEATURES_PATH)
    conduits = m.conduits()
    assert (list(conduits.index) == ['C1:C2'])


def test_pumps_composite(test_model_01):

    # load with Links composite object
    pumps = Links(model=test_model_01, inp_sections=['pumps'],
                  rpt_sections=['Link Flow Summary'])
    assert pumps.dataframe.loc['C2', 'PumpCurve'] == 'P1_Curve'
    assert pumps.geojson['features'][0]['properties']['PumpCurve'] == 'P1_Curve'
    assert pumps.geodataframe.loc['C2', 'PumpCurve'] == 'P1_Curve'

    # access from model attribute
    pumps = test_model_01.pumps
    assert pumps.dataframe.loc['C2', 'PumpCurve'] == 'P1_Curve'
    assert pumps.geojson['features'][0]['properties']['PumpCurve'] == 'P1_Curve'
    assert pumps.geodataframe.loc['C2', 'PumpCurve'] == 'P1_Curve'


def test_weirs_composite(test_model_01):
    weirs = test_model_01.weirs
    df = weirs.dataframe
    print(df)
    assert df.loc['C3', 'DischCoeff'] == 3.33


def test_nodes_dataframe():
    m = swmmio.Model(MODEL_XSECTION_ALT_01)
    nodes = m.nodes()

    node_ids_01 = ['dummy_node1', 'dummy_node2', 'dummy_node3', 'dummy_node4',
                   'dummy_node5', 'dummy_node6', 'dummy_outfall']

    assert (list(nodes.index) == node_ids_01)
    assert (nodes.loc['dummy_node1', 'InvertElev'] == -10.99)
    assert (nodes.loc['dummy_node2', 'MaxDepth'] == 20)
    assert (nodes.loc['dummy_node3', 'coords'] == [(-4205.457, 9695.024)])
    assert (nodes.loc['dummy_node4', 'MaxDepth'] == 12.59314)
    assert (nodes.loc['dummy_node5', 'PondedArea'] == 73511)


def test_infiltration_section():
    # horton
    m = swmmio.Model(MODEL_FULL_FEATURES_XY)
    inf = m.inp.infiltration
    assert(inf.columns.tolist() == ['MaxRate', 'MinRate', 'Decay', 'DryTime', 'MaxInfil'])

    # curve number
    m = swmmio.Model(MODEL_CURVE_NUMBER)
    inf = m.inp.infiltration
    assert m.inp.options.loc['INFILTRATION', 'Value'] == 'CURVE_NUMBER'
    assert (inf.columns.tolist() == ['CurveNum', 'Conductivity (depreciated)', 'DryTime'])

    # mod horton
    m = swmmio.Model(MODEL_MOD_HORTON)
    inf = m.inp.infiltration
    assert m.inp.options.loc['INFILTRATION', 'Value'] == 'MODIFIED_HORTON'
    assert (inf.columns.tolist() == ['MaxRate', 'MinRate', 'Decay', 'DryTime', 'MaxInfil'])

    # green ampt
    m = swmmio.Model(MODEL_GREEN_AMPT)
    inf = m.inp.infiltration
    assert m.inp.options.loc['INFILTRATION', 'Value'] == 'GREEN_AMPT'
    assert (inf.columns.tolist() == ['Suction', 'HydCon', 'IMDmax'])

    # mod green ampt
    m = swmmio.Model(MODEL_MOD_GREEN_AMPT)
    inf = m.inp.infiltration
    assert m.inp.options.loc['INFILTRATION', 'Value'] == 'MODIFIED_GREEN_AMPT'
    assert (inf.columns.tolist() == ['Suction', 'Ksat', 'IMD'])


def test_parse_infiltration_section_with_extra_params():
    # mod green ampt
    m = swmmio.Model(MODEL_INFILTRAION_PARSE_FAILURE)
    inf = m.inp.infiltration
    assert m.inp.options.loc['INFILTRATION', 'Value'] == 'GREEN_AMPT'
    assert (inf.columns.tolist() == ['Suction', 'HydCon', 'IMDmax', 'Param4', 'Param5'])


def test_inflow_dwf_dataframe():
    m = swmmio.Model(MODEL_XSECTION_ALT_03)
    dwf = dataframe_from_inp(m.inp.path, 'dwf')
    assert(dwf.loc['dummy_node2', 'AverageValue'] == pytest.approx(0.000275, 0.0001))

    inf = m.inp.inflows
    assert (inf.loc['dummy_node2', 'Time Series'] == 'my_time_series')
    assert (pd.isna(inf.loc['dummy_node6', 'Time Series']))


def test_coordinates():
    m = swmmio.Model(MODEL_FULL_FEATURES_XY)
    coordinates = m.inp.coordinates
    # coordinates.to_csv(df_test_coordinates_csv)
    test_coords = pd.read_csv(df_test_coordinates_csv, index_col=0)

    assert(coordinates.equals(test_coords))

    # change projection


def test_links_dataframe_from_rpt(test_model_02):

    link_flow_summary = dataframe_from_rpt(test_model_02.rpt.path, 'Link Flow Summary')
    # print(f'\n{link_flow_summary.to_string()}')
    s = '''
    Name   Type  MaxQ  MaxDay  MaxHr  MaxV  MaxQPerc  MaxDPerc                                                      
    C1:C2  CONDUIT  2.45       0  10:19  6.23      1.32      0.50
    C2.1   CONDUIT  0.00       0  00:00  0.00      0.00      0.50
    1      CONDUIT  2.54       0  10:00  3.48      1.10      0.89
    2      CONDUIT  2.38       0  10:03  3.64      1.03      0.85
    3      CONDUIT  1.97       0  09:59  2.92      0.67      1.00
    4      CONDUIT  0.16       0  10:05  0.44      0.10      0.63
    5      CONDUIT  0.00       0  00:00  0.00      0.00      0.50
    C2        PUMP  4.33       0  09:59  0.22       NaN       NaN
    C3        WEIR  7.00       0  10:00  0.33       NaN       NaN
    '''
    lfs_df = pd.read_csv(StringIO(s), index_col=0, delim_whitespace=True, skiprows=[0])
    assert(lfs_df.equals(link_flow_summary))


def test_subcatchments_dataframe_from_rpt(test_model_02):

    sub_ro_summary = dataframe_from_rpt(test_model_02.rpt.path, 'Subcatchment Runoff Summary')
    tot_ro = sub_ro_summary['TotalRunoffMG'].sum()
    assert tot_ro == pytest.approx(0.28, 0.001)

    # test retrieving timeseries results
    s1_results = dataframe_from_rpt(test_model_02.rpt.path, 'Subcatchment Results', 'S1')
    assert s1_results['RunoffCFS'].max() == pytest.approx(0.5526, 0.00001)


def test_node_flooding_dataframe_from_rpt_1(test_model_02):

    node_flooding = dataframe_from_rpt(test_model_02.rpt.path, 'Node Flooding Summary')
    assert node_flooding['MaxQFlooding'].max() == pytest.approx(0.07, 0.0001)


def test_node_flooding_dataframe_from_rpt_2():

    node_flooding = dataframe_from_rpt(OWA_RPT_EXAMPLE, 'Node Flooding Summary')
    assert node_flooding.empty


def test_polygons(test_model_02):
    s = """
    Name        X        Y 
    S1    110.154  195.885
    S1    110.154   47.351
    S1    -56.323   42.367
    S1    -63.301  181.928
    S1    110.154  195.885
    S2    394.261  131.088
    S2    410.211  -20.436
    S2    245.728  -19.439
    S2    235.759  110.154
    S2    394.261  131.088
    S3    660.425   55.326
    S3    657.435 -104.173
    S3    519.867  -96.198
    S3    509.898   50.342
    S3    660.425   55.326
    S4    -63.523 -116.383
    S4    -82.996 -174.805
    S4   -154.695 -168.608
    S4   -148.499 -126.120
    """
    poly1 = pd.read_csv(StringIO(s), index_col=0, delim_whitespace=True, skiprows=[0])

    assert poly1.equals(test_model_02.inp.polygons)

    # print()
