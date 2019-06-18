from swmmio.defs.config import GEODATABASE
from swmmio.graphics.constants import *

basemap_options = {
    'gdb': GEODATABASE,
    'features': [
        # this is an array so we can control the order of basemap layers
        {
            'feature': 'PhiladelphiaParks',
            'fill': park_green,
            'cols': ["OBJECTID"]  # , "SHAPE@"]
        },
        {
            'feature': 'HydroPolyTrim',
            'fill': water_grey,
            'cols': ["OBJECTID"]  # , "SHAPE@"]
        },
        {
            'feature': 'Streets_Dissolved5_SPhilly',
            'fill': lightgrey,
            'fill_anno': grey,
            'cols': ["OBJECTID", "ST_NAME"]  # "SHAPE@",
        }
    ],
}
