from swmmio.core import *
from swmmio.elements import *
from swmmio.version_control import *
from swmmio.utils.dataframes import dataframe_from_bi, dataframe_from_rpt, dataframe_from_inp
from swmmio.utils.functions import find_network_trace
from swmmio.graphics.swmm_graphics import create_map
from swmmio.graphics.profiler import (build_profile_plot, add_hgl_plot,
                                      add_node_labels_plot, add_link_labels_plot)

# import swmmio.core as swmmio
'''Python SWMM Input/Output Tools'''


VERSION_INFO = (0, 6, 0)
__version__ = '.'.join(map(str, VERSION_INFO))
__author__ = 'Adam Erispaha'
__copyright__ = 'Copyright (c) 2022'
__licence__ = ''
