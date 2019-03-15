from swmmio.tests.data import (MODEL_FULL_FEATURES_PATH, MODEL_FULL_FEATURES__NET_PATH,
                               MODEL_BROWARD_COUNTY_PATH, MODEL_XSECTION_ALT_01, df_test_coordinates_csv,
                               MODEL_FULL_FEATURES_XY)
import swmmio
from swmmio import create_dataframeINP
import pandas as pd


def test_create_dataframeRPT():
    m = swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)

    depth_summ = swmmio.create_dataframeRPT(m.rpt.path, "Node Depth Summary")
    flood_summ = swmmio.create_dataframeRPT(
        m.rpt.path, "Node Flooding Summary")
    inflo_summ = swmmio.create_dataframeRPT(m.rpt.path, "Node Inflow Summary")

    print('\n', depth_summ)
    print(inflo_summ)
    print(flood_summ)

    assert (inflo_summ.loc['J3', 'TotalInflowV'] == 6.1)
    assert (inflo_summ.loc['J1', 'MaxTotalInflow'] == 3.52)

    assert (depth_summ.loc['J3', 'MaxNodeDepth'] == 1.64)
    assert (depth_summ.loc['4', 'MaxNodeDepth'] == 0.87)

    # need to ensure indices are strings always
    assert (flood_summ.loc[5, 'TotalFloodVol'] == 0)


def test_conduits_dataframe():
    m = swmmio.Model(MODEL_FULL_FEATURES_PATH)
    conduits = m.conduits()
    assert (list(conduits.index) == ['C1:C2'])


def test_nodes_dataframe():
    m = swmmio.Model(MODEL_XSECTION_ALT_01)
    nodes = m.nodes()

    node_ids_01 = ['dummy_node1', 'dummy_node2', 'dummy_node3', 'dummy_node4',
                   'dummy_node5', 'dummy_node6', 'dummy_outfall']

    assert (list(nodes.index) == node_ids_01)
    assert (nodes.loc['dummy_node1', 'InvertElev'] == -10.99)
    assert (nodes.loc['dummy_node2', 'MaxDepth'] == 20)
    assert (nodes.loc['dummy_node3', 'X'] == -4205.457)
    assert (nodes.loc['dummy_node4', 'MaxDepth'] == 12.59314)
    assert (nodes.loc['dummy_node5', 'PondedArea'] == 73511)


def test_model_to_networkx():
    m = swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)
    G = m.network

    assert (G['J2']['J3']['C2.1']['Length'] == 666)
    assert (G['J1']['J2']['C1:C2']['Length'] == 244.63)
    assert (round(G.node['J2']['InvertElev'], 3) == 13.0)

    links = m.links()
    assert(len(links) == len(G.edges()))


def test_coordinates():
    m = swmmio.Model(MODEL_FULL_FEATURES_XY)
    coordinates = m.inp.coordinates
    # coordinates.to_csv(df_test_coordinates_csv)
    test_coords = pd.read_csv(df_test_coordinates_csv, index_col=0)

    assert(coordinates.equals(test_coords))

    # change projection


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
        rpt = model.rpt

        # create dataframes of relevant sections from the INP
        pumps_df = create_dataframeINP(inp.path, "[PUMPS]", comment_cols=False)
        if pumps_df.empty:
            return pd.DataFrame()

        # add conduit coordinates
        xys = pumps_df.apply(lambda r: swmmio.get_link_coords(r, inp.coordinates, inp.vertices), axis=1)
        df = pumps_df.assign(coords=xys.map(lambda x: x[0]))
        df.InletNode = df.InletNode.astype(str)
        df.OutletNode = df.OutletNode.astype(str)

        model._pumps_df = df

        return df

    pumps_old_method = pumps_old_method(m)
    pumps = m.pumps()

    assert(pumps_old_method.equals(pumps))