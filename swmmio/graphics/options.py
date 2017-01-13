from definitions import PARCEL_FEATURES, GEODATABASE
from constants import *


basemap_options = {
'gdb': GEODATABASE,
'features': [
    #this is an array so we can control the order of basemap layers
    {
        'feature': 'PhiladelphiaParks',
        'fill': park_green,
        'outline': None,
        'featureDict': None,
        'cols': ["OBJECTID", "SHAPE@"]
    },
    {
        'feature': 'HydroPolyTrim',
        'fill':water_grey,
        'outline': None,
        'featureDict': None,
        'cols': ["OBJECTID", "SHAPE@"]
    },
    {
        'feature': 'Streets_Dissolved5_SPhilly',
        'fill': lightgrey,
        'width': 0,
        'fill_anno': grey,
        'outline': None,
        'featureDict': None,
        'cols': ["OBJECTID", "SHAPE@", "ST_NAME"]
    }
  ],
}
