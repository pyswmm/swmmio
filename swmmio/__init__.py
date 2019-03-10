'''Python SWMM Input/Output Tools'''


VERSION_INFO = (0, 3, 3, 'dev')
__version__ = '.'.join(map(str, VERSION_INFO))
__author__ = 'Adam Erispaha'
__copyright__ = 'Copyright (c) 2016'
__licence__ = ''

from .core import *
from swmmio.utils.dataframes import create_dataframeBI, create_dataframeRPT, create_dataframeINP
