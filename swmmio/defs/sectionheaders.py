#=================
#DEFINE INP HEADER THAT SHOULD BE REPLACED
#=================
from collections import OrderedDict

inp_header_dict = {
    '[TITLE]':'blob',
    '[OPTIONS]':'Name Value',
    '[FILES]': 'Action FileType FileName',
    '[CONDUITS]': 'Name InletNode OutletNode Length ManningN InOffset OutOffset InitFlow MaxFlow',
    '[COORDINATES]': 'Name X Y',
    '[JUNCTIONS]': 'Name InvertElev MaxDepth InitDepth SurchargeDepth PondedArea',
    '[ORIFICES]': 'Name InletNode OutletNode OrificeType CrestHeight DischCoeff FlapGate OpenCloseTime',
    '[OUTFALLS]': 'Name InvertElev OutfallType StageOrTimeseries TideGate',
    '[STORAGE]': 'Name InvertElev MaxD InitDepth StorageCurve Coefficient Exponent Constant PondedArea EvapFrac SuctionHead Conductivity InitialDeficit',
    '[VERTICES]': 'Name X Y',
    '[WEIRS]': 'Name InletNode OutletNode WeirType CrestHeight DischCoeff FlapGate EndCon EndCoeff Surcharge  RoadWidth  RoadSurf',
    '[XSECTIONS]':'Link Shape Geom1 Geom2 Geom3 Geom4 Barrels',
    '[SUBCATCHMENTS]':'Name Raingage Outlet Area PercImperv Width PercSlope CurbLength SnowPack',
    '[SUBAREAS]':'Name N-Imperv N-Perv S-Imperv S-Perv PctZero RouteTo PctRouted',
    '[LOSSES]':'Link Inlet Outlet Average FlapGate',
    '[PUMPS]':'Name InletNode OutletNode PumpCurve InitStatus Depth ShutoffDepth',
    '[DWF]':'Node Parameter AverageValue TimePatterns',
    '[RAINGAGES]':'Name RainType TimeIntrv SnowCatch DataSourceType DataSourceName',
    '[INFILTRATION]':'Subcatchment Suction HydCon IMDmax',
    '[Polygons]':'Name X Y',
    '[REPORT]':'Param Status',
    '[TAGS]':'ElementType Name Tag',
    '[MAP]': 'x1 y1 x2 y2',
    '[CURVES]': 'Name Type X-Value Y-Value',
    '[TIMESERIES]': 'Name Date Time Value'
}



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