<<<<<<< HEAD
from definitions import PARCEL_FEATURES, GEODATABASE
=======
from swmmio.defs.config import PARCEL_FEATURES, GEODATABASE
>>>>>>> 20c5e0571a9e48d405822dc963669df8811e6d33
from constants import *

font_file = r"C:\Data\Code\Fonts\Raleway-Regular.ttf"
basemap_options = {
'gdb': GEODATABASE,
'features': [
    #this is an array so we can control the order of basemap layers
    {
        'feature': 'PhiladelphiaParks',
        'fill': park_green,
        'cols': ["OBJECTID"]#, "SHAPE@"]
    },
    {
        'feature': 'HydroPolyTrim',
        'fill':water_grey,
        'cols': ["OBJECTID"]#, "SHAPE@"]
    },
    {
        'feature': 'Streets_Dissolved5_SPhilly',
        'fill': lightgrey,
        'fill_anno': grey,
        'cols': ["OBJECTID", "ST_NAME"] #"SHAPE@",
    }
  ],
}
