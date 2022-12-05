import swmmio
from swmmio.tests.data import MODEL_FULL_FEATURES__NET_PATH, OWA_RPT_EXAMPLE, RPT_FULL_FEATURES
from swmmio.utils.functions import format_inp_section_header
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

    links = m.links()
    assert(len(links) == len(G.edges()))