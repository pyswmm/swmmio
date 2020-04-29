import pandas as pd
import os
from os.path import join as j
from swmmio.defs.sectionheaders import inp_header_dict

current_dir = os.path.dirname(__file__)
sets = j(current_dir, 'inp_settings')

# TODO: do something about his silly file
OPTIONS_no_rain = pd.read_table(
                                j(sets, 'OPTIONS_no_rain.txt'),
                                delim_whitespace=True,
                                names=inp_header_dict['[OPTIONS]'].split(),
                                skiprows=1,
                                index_col=0
                                )

OPTIONS_normal = pd.read_table(
                                j(sets, 'OPTIONS_normal.txt'),
                                delim_whitespace=True,
                                names=inp_header_dict['[OPTIONS]'].split(),
                                skiprows=1,
                                index_col=0
                                )
REPORT_nodes_links = pd.read_table(
                                j(sets, 'REPORT_nodes_links.txt'),
                                delim_whitespace=True,
                                names=inp_header_dict['[REPORT]'].split(),
                                skiprows=1,
                                index_col=0
                                )
REPORT_none = pd.read_table(
                                j(sets, 'REPORT_none.txt'),
                                delim_whitespace=True,
                                names=inp_header_dict['[REPORT]'].split(),
                                skiprows=1,
                                index_col=0
                            )
