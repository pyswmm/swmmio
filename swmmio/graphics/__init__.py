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
    graphics.options.inlcude_parcels = True

    #draws the model with parcels
    sg.drawModel(swmmio.Model(/path/to/model), bbox=su.d68d70)

"""
_o = {
    'include_basemap':False,
    'include_parcels':False,
    'basemap_shapefile_dir':r'C:\Data\ArcGIS\Shapefiles',

    #regular shapefile used for drawing parcels
    'parcels_shapefile':r'C:\Data\ArcGIS\Shapefiles\pennsport_parcels.shp',

    #table resulting from one-to-many spatial join of parcels to sheds
    'parcel_node_join_data':r'P:\02_Projects\SouthPhila\SE_SFR\MasterModels\CommonData\pennsport_sheds_parcels_join.csv',

    'font_file':r'C:\Data\Code\Fonts\Raleway-Regular.ttf',
}

config = _dotdict(_o)
