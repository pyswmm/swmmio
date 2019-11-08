import swmmio
from swmmio.tests.data import MODEL_FULL_FEATURES__NET_PATH
from swmmio.utils.functions import format_inp_section_header


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


def test_model_to_networkx():
    m = swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)
    G = m.network

    assert (G['J2']['J3']['C2.1']['Length'] == 666)
    assert (G['J1']['J2']['C1:C2']['Length'] == 244.63)
    assert (round(G.nodes['J2']['InvertElev'], 3) == 13.0)

    links = m.links()
    assert(len(links) == len(G.edges()))