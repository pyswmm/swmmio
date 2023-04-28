# =================
# DEFINE INP HEADER THAT SHOULD BE REPLACED
# =================
from collections import OrderedDict


def parse_inp_section_config(raw_conf):
    """
    normalize the config information in the YAML
    :return:
    >>> from swmmio.defs import INP_OBJECTS
    >>> conds_config = INP_OBJECTS['CONDUITS']
    >>> parse_inp_section_config(conds_config)
    OrderedDict([('columns', ['Name', 'InletNode', 'OutletNode', 'Length', 'ManningN', 'InOffset', 'OutOffset', 'InitFlow', 'MaxFlow'])])
    >>> parse_inp_section_config(INP_OBJECTS['LOSSES'])
    OrderedDict([('columns', ['Link', 'Inlet', 'Outlet', 'Average', 'Flap Gate', 'SeepageRate'])])
    """

    conf = OrderedDict()
    if isinstance(raw_conf, list):
        # has a simple list, assumed to be columns
        conf['columns'] = raw_conf
    elif isinstance(raw_conf, (dict, OrderedDict)):
        if 'keys' in raw_conf:
            # object is special case like OPTIONS
            conf.update(raw_conf)
            conf['columns'] = ['Key', 'Value']
        else:
            conf.update(raw_conf)

    return conf


def normalize_inp_config(inp_obects):
    """
    Unpack the config details for each inp section and organize in a standard format.
    This allows the YAML file to be more short hand and human readable.
    :param inp_obects:
    :return:
    >>> from swmmio.defs import INP_OBJECTS
    >>> conf = normalize_inp_config(INP_OBJECTS)
    >>> print(conf['JUNCTIONS'])
    >>> print(conf)
    OrderedDict([('columns', ['Name', 'InvertElev', 'MaxDepth', 'InitDepth', 'SurchargeDepth', 'PondedArea'])])
    """
    normalized = OrderedDict()
    for sect, raw_conf in inp_obects.items():
        conf = parse_inp_section_config(raw_conf)
        normalized[sect] = conf

    return normalized