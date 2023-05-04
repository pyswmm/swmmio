import pytest
import swmmio
from swmmio.tests.data import (MODEL_FULL_FEATURES__NET_PATH,
                               OWA_RPT_EXAMPLE, RPT_FULL_FEATURES,
                               MODEL_EX_1_PARALLEL_LOOP, MODEL_EX_1)
from swmmio.utils.functions import format_inp_section_header, find_network_trace
from swmmio.utils import error
from swmmio.utils.text import get_rpt_metadata


def test_format_inp_section_header():

    header_string = '[CONDUITS]'
    header_string = format_inp_section_header(header_string)
    assert(header_string == '[CONDUITS]')

    header_string = '[conduits]'
    header_string = format_inp_section_header(header_string)
    assert (header_string == '[CONDUITS]')

    header_string = 'JUNCTIONS'
    header_string = format_inp_section_header(header_string)
    assert (header_string == '[JUNCTIONS]')

    header_string = 'pumps'
    header_string = format_inp_section_header(header_string)
    assert (header_string == '[PUMPS]')


def test_get_rpt_metadata_owa_swmm():
    meta = get_rpt_metadata(OWA_RPT_EXAMPLE)
    assert meta['swmm_version'] == {'major': 5, 'minor': 1, 'patch': 14}


def test_get_rpt_metadata_epa_swmm():
    meta = get_rpt_metadata(RPT_FULL_FEATURES)
    assert meta['swmm_version'] == {'major': 5, 'minor': 0, 'patch': 22}


def test_model_to_networkx():
    m = swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)
    G = m.network

    assert (G['J2']['J3']['C2.1']['Length'] == 666)
    assert (G['J1']['J2']['C1:C2']['Length'] == 244.63)
    assert (round(G.nodes['J2']['InvertElev'], 3) == 13.0)

    links = m.links.dataframe
    assert(len(links) == len(G.edges()))


def test_network_trace_loop():
    m = swmmio.Model(MODEL_EX_1_PARALLEL_LOOP)
    start_node = "9"
    end_node = "18"
    path_selection = find_network_trace(m, start_node, end_node,
                                        include_nodes=[],
                                        include_links=["LOOP"])
    correct_path = [('9', '10', '1'),
                    ('10', '21', '6'),
                    ('21', '24', 'LOOP'),
                    ('24', '17', '16'),
                    ('17', '18', '10')]
    assert (path_selection == correct_path)


def test_network_trace_bad_link():
    m = swmmio.Model(MODEL_EX_1)
    start_node = "9"
    end_node = "18"
    with pytest.raises(error.LinkNotInInputFile) as execinfo:
        path_selection = find_network_trace(m, start_node, end_node,
                                            include_links=["LOOP"])


def test_network_trace_bad_start_node():
    m = swmmio.Model(MODEL_EX_1)
    start_node = "9000"
    end_node = "18"
    with pytest.raises(error.NodeNotInInputFile):
        path_selection = find_network_trace(m, start_node, end_node)


def test_network_trace_bad_end_node():
    m = swmmio.Model(MODEL_EX_1)
    start_node = "9"
    end_node = "18000"
    with pytest.raises(error.NodeNotInInputFile):
        path_selection = find_network_trace(m, start_node, end_node)


def test_network_trace_bad_include_node():
    m = swmmio.Model(MODEL_EX_1)
    start_node = "9"
    end_node = "18"
    with pytest.raises(error.NodeNotInInputFile):
        path_selection = find_network_trace(m, start_node,
                                            end_node,
                                            include_nodes=["1000"])
