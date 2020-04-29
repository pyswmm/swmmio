from swmmio.defs.config import FONT_PATH
from swmmio.defs.constants import park_green, water_grey, lightgrey, grey


class _dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


"""
this allows module wide configuration of drawing methods. The dotdict allows for
convenient access.
Example:

    from swmmio import graphics
    from swmmio.graphics import swmm_graphics as sg

    #configure
    graphics.config.inlcude_parcels = True

    #draws the model with parcels
    sg.drawModel(swmmio.Model(/path/to/model), bbox=su.d68d70)

"""
_o = {
    'include_basemap': False,
    'include_parcels': False,
    'basemap_shapefile_dir': r'C:\Data\ArcGIS\Shapefiles',

    # regular shapefile used for drawing parcels
    'parcels_shapefile': r'C:\Data\ArcGIS\Shapefiles\pennsport_parcels.shp',

    # table resulting from one-to-many spatial join of parcels to sheds
    'parcel_node_join_data': r'P:\02_Projects\SouthPhila\SE_SFR\MasterModels\CommonData\pennsport_sheds_parcels_join.csv',

    'font_file': FONT_PATH,
    'basemap_options': {
    'gdb': r'C:\Data\ArcGIS\GDBs\LocalData.gdb',
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
}

config = _dotdict(_o)
