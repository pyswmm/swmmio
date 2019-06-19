import os

# This is the swmmio project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# path to the SWMM5 executable used within the run_models module
if os.name == 'posix':
    SWMM_ENGINE_PATH = os.path.join(ROOT_DIR, 'lib', 'linux', 'swmm5')
else:
    SWMM_ENGINE_PATH = os.path.join(ROOT_DIR, 'lib', 'windows', 'swmm5_22.exe')

# feature class name of parcels in geodatabase
PARCEL_FEATURES = r'PWD_PARCELS_SHEDS_PPORT'

# name of the directories in which to store post processing data
REPORT_DIR_NAME = r'Report'

# path to the basemap file used to create custom basemaps
FONT_PATH = os.path.join(ROOT_DIR, 'swmmio', 'graphics', 'fonts', 'Verdana.ttf')

# path to the default geodatabase. used for some arcpy functions and parcel calcs
GEODATABASE = r'C:\Data\ArcGIS\GDBs\LocalData.gdb'

# path to the basemap file used to create custom basemaps
BASEMAP_PATH = os.path.join(ROOT_DIR, 'swmmio', 'reporting', 'basemaps', 'index.html')
BETTER_BASEMAP_PATH = os.path.join(ROOT_DIR, 'swmmio', 'reporting', 'basemaps', 'mapbox_base.html')

