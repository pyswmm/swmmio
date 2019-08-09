import pandas as pd
import os
from os.path import join as j
from swmmio.defs.sectionheaders import inp_header_dict

current_dir = os.path.dirname(__file__)
sets = j(current_dir, 'inp_settings')


OPTIONS_no_rain = pd.read_csv(
                                j(sets, 'OPTIONS_no_rain.txt'),
                                delim_whitespace=True,
                                names=inp_header_dict['[OPTIONS]'].split(),
                                skiprows=1,
                                )

OPTIONS_normal = pd.read_csv(
                                j(sets, 'OPTIONS_normal.txt'),
                                delim_whitespace=True,
                                names=inp_header_dict['[OPTIONS]'].split(),
                                skiprows=1,
                                )
REPORT_nodes_links = pd.read_csv(
                                j(sets, 'REPORT_nodes_links.txt'),
                                delim_whitespace=True,
                                names=inp_header_dict['[REPORT]'].split(),
                                skiprows=1,
                                )
REPORT_none = pd.read_csv(
                                j(sets, 'REPORT_none.txt'),
                                delim_whitespace=True,
                                names=inp_header_dict['[REPORT]'].split(),
                                skiprows=1,
                            )
