# UTILITY FUNCTIONS AIMED AT I/O OPERATIONS WITH TEXT FILES
# STANDARD READING AND WRITING OF TEXT FILES (E.G. .INP AND .RPT)

import os
import re
from io import StringIO
from collections import OrderedDict, deque

from swmmio.defs import INFILTRATION_COLS, INP_SECTION_TAGS, SWMM5_VERSION
from swmmio.utils.functions import format_inp_section_header
from swmmio.defs.sectionheaders import normalize_inp_config


def inline_comments_in_inp(filepath, overwrite=False):
    """
    with an existing INP file, shift any comments that have been placed above the
    element (behavoir from saving in GUI) and place them to the right, inline with
    the element. To improve readability
    """
    newfilename = os.path.splitext(os.path.basename(filepath))[0] + '_unGUI.inp'
    newfilepath = os.path.join(os.path.dirname(filepath), newfilename)
    allheaders = get_inp_sections_details(filepath)

    with open(filepath) as oldf:
        with open(newfilepath, 'w') as new:

            # to hold list of comments (handles multiline comments)
            comment_concat = []
            current_section = list(allheaders.keys())[0]
            for line in oldf:

                # determine what section we are in by noting when we pass double brackets
                if '[' and ']' in line:
                    current_section = line.strip()

                if len(line.strip()) > 1:
                    if line.strip()[0] == ';' and ''.join(line.strip()[:2]) != ';;':
                        # this is a comment bc first char is ; and the
                        # second char is not (which would resemble the header section)
                        words = line.split()
                        hdrs = allheaders[current_section]['columns']
                        perc_match_to_header = float(len([x for x in words if x in hdrs])) / float(len(hdrs))
                        if perc_match_to_header <= 0.75:
                            comment_concat.append(line.strip())
                    else:
                        # this row has data, tack any comment to the line end
                        comment_string = ''
                        if len(comment_concat) > 0:
                            comment_string = r' '.join(comment_concat)
                        newlinestring = line.strip() + comment_string + '\n'
                        new.write(newlinestring)
                        comment_concat = []
                else:
                    # write the short line
                    new.write(line)

    # rename files and remove old if we should overwrite
    if overwrite:
        os.remove(filepath)
        os.rename(newfilepath, filepath)


def extract_section_of_file(file_path, start_strings, end_strings, comment=';', **kwargs):
    """
    Extract a portion of a file found between one or more start strings and the first
    encountered end string.
    :param file_path: path to the source file
    :param start_strings: string or list of strings from which to start extracting
    :param end_strings: string or list of strings at which to stop extracting
    :param comment: comment string used to ignore parts of source file
    :return: string extracted from source file
    >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY
    >>> s = extract_section_of_file(MODEL_FULL_FEATURES_XY, '[EVAPORATI', '[', comment=None)
    >>> print(s.strip())
    [EVAPORATION]
    ;;Data Source    Parameters
    ;;-------------- ----------------
    CONSTANT         0.0
    DRY_ONLY         NO
    """

    if isinstance(end_strings, str):
        end_strings = [end_strings]

    if isinstance(start_strings, str):
        start_strings = [start_strings]

    starts_ix = 0
    starts_len = len(start_strings)
    start_found = False
    out_string = ''
    with open(file_path, 'r') as f:

        for line in f:

            # the current string we are searching for
            if starts_ix < starts_len:
                search_str = start_strings[starts_ix]

            if start_found and any(es.upper() in line.upper() for es in end_strings):
                # if we found the start and the line contains any of
                # the end strings, break out
                break
            elif not start_found and search_str.upper() in line.upper():
                # increment the index of the start strings that have been found
                starts_ix += 1
            if starts_ix == starts_len:
                # we found each of the start strings
                start_found = True

            if start_found:
                if comment is not None:
                    # ignore anything after a comment
                    if comment in line:
                        s = line.split(comment)[0] + '\n'
                        out_string += s
                    else:
                        out_string += line
                else:
                    out_string += line

    return out_string


def get_rpt_metadata(file_path):
    """
    Scan rpt file and extract meta data

    :param file_path: path to rpt file
    :return: dict of metadata
    """

    with open(file_path) as f:
        for line in f:
            if "Starting Date" in line:
                simulation_start = line.split(".. ")[1].replace("\n", "")
            if "Ending Date" in line:
                simulation_end = line.split(".. ")[1].replace("\n", "")
            if "STORM WATER MANAGEMENT MODEL - VERSION" in line:
                version = re.search(r"\d+.\d+.\d+", line)
                if version is not None:
                    version = version.group(0).split('.')
                    swmm_version = {
                        'major': int(version[0]),
                        'minor': int(version[1]),
                        'patch': int(version[2])
                    }
            if "Report Time Step ........." in line:
                time_step_min = int(line.split(":")[1].replace("\n", ""))
                break

    # grab the date of analysis from end of file
    with open(file_path) as f:
        f.seek(os.path.getsize(file_path) - 500)  # jump to 500 bytes before the end of file
        for line in f:
            if "Analysis begun on" in line:
                analysis_date = line.split("Analysis begun on:  ")[1].replace("\n", "")

    meta_data = dict(
        swmm_version=swmm_version,
        simulation_start=simulation_start,
        simulation_end=simulation_end,
        time_step_min=time_step_min,
        analysis_date=analysis_date,
    )
    return meta_data


def find_byte_range_of_section(path, start_string):
    '''
    returns the start and end "byte" location of substrings in a text file
    '''

    with open(path) as f:
        start = None
        end = None
        l = 0  # line bytes index
        for line in f:

            if start and line.strip() == "" and (l - start) > 100:
                # LOGIC: if start exists (was found) and the current line
                # length is 3 or less (length of /n ) and we're more than
                # 100 bytes from the start location then we are at the first
                # "blank" line after our start section (aka the end of the
                # section)
                end = l
                break

            if (start_string in line) and (not start):
                start = l

            # increment length (bytes?) of current position
            l += len(line) + len("\n")

    return [start, end]


def get_inp_sections_details(inp_path, include_brackets=False):
    """
    creates a dictionary with all the headers found in an INP file
    (which varies based on what the user has defined in a given model)
    and updates them based on the definitions in inp_header_dict
    this ensures the list is comprehensive
    :param inp_path:
    :param include_brackets: whether to parse sections including the []
    :return: OrderedDict
    >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY
    >>> headers = get_inp_sections_details(MODEL_FULL_FEATURES_XY)
    >>> [header for header, cols in headers.items()][:4]
    ['TITLE', 'OPTIONS', 'EVAPORATION', 'RAINGAGES']
    >>> headers['SUBCATCHMENTS']['columns']
    ['Name', 'Raingage', 'Outlet', 'Area', 'PercImperv', 'Width', 'PercSlope', 'CurbLength', 'SnowPack']
    """
    from swmmio.defs import INP_OBJECTS
    import pandas as pd
    found_sects = OrderedDict()

    with open(inp_path) as f:
        txt = f.read()
        section_dict = {
            key: txt.find("[{}]".format(key)) for key in INP_OBJECTS.keys() 
            if txt.find("[{}]".format(key)) >= 0
        }
        section_dict = sorted(section_dict, key=section_dict.get)
        bracketed_words = re.findall(r"\[([A-Za-z0-9_]+)\]", txt)

        for sect in bracketed_words:
            sect_id = f'[{sect.upper()}]' if include_brackets else sect.upper()
            if sect not in section_dict:
                found_sects[sect_id] = OrderedDict(columns=['blob'])
            else:
                found_sects[sect_id] = INP_OBJECTS[sect]

    # make necessary adjustments to columns that change based on options
    ops_cols = INP_OBJECTS['OPTIONS']['columns']
    ops_string = extract_section_of_file(inp_path, '[OPTIONS]', INP_SECTION_TAGS, )
    options = pd.read_csv(StringIO(ops_string), header=None,
                          delim_whitespace=True, skiprows=[0], index_col=0,
                          names=ops_cols)

    if 'INFILTRATION' in found_sects:
        # select the correct infiltration column names
        # fall back to HORTON if invalid/unset infil type
        infil_type = options['Value'].get('INFILTRATION', None)
        if pd.isna(infil_type):
            infil_type = 'HORTON'
        infil_cols = INFILTRATION_COLS[infil_type.upper()]

        inf_id = 'INFILTRATION'
        if include_brackets:
            inf_id = '[{}]'.format('INFILTRATION')

        # overwrite the dynamic sections with proper header cols
        found_sects[inf_id]['columns'] = list(infil_cols)
    return found_sects


def get_rpt_sections_details(rpt_path):
    """

    :param rpt_path:
    :param include_brackets:
    :return:
    # >>> MODEL_FULL_FEATURES__NET_PATH

    """
    from swmmio.defs import RPT_OBJECTS
    found_sects = OrderedDict()
    rpt_headers = RPT_OBJECTS.copy()

    # get rpt file metadata
    meta_data = get_rpt_metadata(rpt_path)
    swmm_version = meta_data['swmm_version']

    # make necessary adjustments to columns that change based on swmm version
    for version in SWMM5_VERSION:
        version_value = float(version)
        rpt_version = float(f"{swmm_version['minor']}.{swmm_version['patch']}")
        if rpt_version >= version_value:
            update_rpt = normalize_inp_config(SWMM5_VERSION[version]['rpt_sections'])
            rpt_headers.update(update_rpt)

    with open(rpt_path) as f:
        buff3line = deque()
        for line in f:
            # maintains a 3 line buffer and looks for instances where
            # a top and bottom line have '*****' and records the middle line
            # typical of section headers in RPT files
            buff3line.append(line)
            if len(buff3line) > 3:
                buff3line.popleft()

            # search for section header between two rows of *'s
            if ('***********' in buff3line[0] and
                    '***********' in buff3line[2] and
                    len(buff3line[1].strip()) > 0):
                header = buff3line[1].strip()

                if header in rpt_headers:
                    found_sects[header] = rpt_headers[header]
                else:
                    # unrecognized section
                    found_sects[header] = OrderedDict(columns=['blob'])

    return found_sects
