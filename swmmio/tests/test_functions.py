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

