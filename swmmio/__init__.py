from swmmio import *
from swmmio.utils.dataframes import create_dataframeBI, create_dataframeRPT, create_dataframeINP
from .core import *
import swmmio.core as swmmio
'''Python SWMM Input/Output Tools'''


VERSION_INFO = (0, 3, 4, 'post1') # post release to include json in manifest
__version__ = '.'.join(map(str, VERSION_INFO))
__author__ = 'Adam Erispaha'
__copyright__ = 'Copyright (c) 2016'
__licence__ = ''
