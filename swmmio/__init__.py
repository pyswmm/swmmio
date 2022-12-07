from swmmio.core import *
from swmmio.elements import *
from swmmio.version_control import *
from swmmio.utils.dataframes import dataframe_from_bi, dataframe_from_rpt, dataframe_from_inp
from swmmio.graphics.swmm_graphics import create_map

# import swmmio.core as swmmio
'''Python SWMM Input/Output Tools'''


VERSION_INFO = (0, 4, 13)
__version__ = '.'.join(map(str, VERSION_INFO))
__author__ = 'Adam Erispaha'
__copyright__ = 'Copyright (c) 2016'
__licence__ = ''
