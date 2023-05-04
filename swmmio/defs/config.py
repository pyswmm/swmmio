import os

# This is the swmmio project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# path to the Python executable used to run your version of Python
PYTHON_EXE_PATH = "python"#os.path.join(os.__file__.split("lib/")[0],"bin","python")

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

# PySWMM Wrapper Path
PYSWMM_WRAPPER_PATH = os.path.join(ROOT_DIR, 'swmmio', 'wrapper', 'pyswmm_wrapper.py')
