import math

from swmmio.utils.functions import format_inp_section_header, remove_braces
from swmmio.utils.text import (extract_section_of_file, get_inp_sections_details,
                               get_rpt_sections_details)
from io import StringIO
import warnings
import pandas as pd
import re


def dataframe_from_bi(bi_path, section='[CONDUITS]'):
    """
    given a path to a build instructions file, create a dataframe of data in a
    given section
    """

    df = dataframe_from_inp(bi_path, section,
                            additional_cols=[';', 'Comment', 'Origin'],
                            comment=';;')
    return df


def create_dataframe_multi_index(inp_path, section='CURVES'):

    # format the section header for look up in headers OrderedDict
    sect = remove_braces(section).upper()

    # get list of all section headers in inp to use as section ending flags
    headers = get_inp_sections_details(inp_path, include_brackets=False)

    if sect not in headers:
        warnings.warn(f'{sect} section not found in {inp_path}')
        return pd.DataFrame()

    # extract the string and read into a dataframe
    start_string = format_inp_section_header(section)
    end_strings = [format_inp_section_header(h) for h in headers.keys()]
    s = extract_section_of_file(inp_path, start_string, end_strings)
    cols = headers[sect]['columns']

    f = StringIO(s)
    data = []
    for line in f.readlines():
        if "FILE" in line:
            filename = re.findall(r'"([^"]*)"', line)[0]
            items = line.strip().split()[:2]
            items = [items[0], items[1], None, '"{}"'.format(filename)]
        else:
            items = line.strip().split()
            if len(items) == 3:
                items = [items[0], None, items[1], items[2]]
        if len(items) == 4:
            data.append(items)


    df = pd.DataFrame(data=data, columns=cols)
    if sect == 'CURVES':
        df = df.set_index(['Name', 'Type'])
    elif sect == 'TIMESERIES':
        df = df.set_index(['Name'])

    return df


def dataframe_from_rpt(rpt_path, section, element_id=None):
    """
    create a dataframe from a section of an RPT file

    :param rpt_path: path to rep file
    :param section: title of section to extract
    :param element_id: type of element when extracting time series data
    :return: pd.DataFrame
    """

    # get list of all section headers in rpt to use as section ending flags
    headers = get_rpt_sections_details(rpt_path)

    if section not in headers:
        warnings.warn(f'{section} section not found in {rpt_path}')
        return pd.DataFrame()

    # handle case for extracting timeseries results
    if element_id is not None:
        end_strings = ['<<< ']
        start_strings = [
            section,
            f"<<< {section.replace(' Results', '')} {element_id} >>>",
            '-' * 20, '-' * 20
        ]
    else:
        # and get the list of columns to use for parsing this section
        end_strings = list(headers.keys())
        end_strings.append('***********')
        start_strings = [section, '-'*20, '-'*20]
    cols = headers[section]['columns']

    # check for no Node Flooding Summary Edge case "No nodes were flooded."
    if section == 'Node Flooding Summary':
        s = extract_section_of_file(rpt_path, [section, 'No nodes were flooded.'], end_strings)
        if 'No nodes were flooded' in s:
            return pd.DataFrame(columns=cols)

    # extract the string and read into a dataframe
    s = extract_section_of_file(rpt_path, start_strings, end_strings)
    df = pd.read_csv(StringIO(s), header=None, delim_whitespace=True, skiprows=[0],
                     index_col=0, names=cols)

    # confirm index name is string
    df = df.rename(index=str)

    return df


def dataframe_from_inp(inp_path, section, additional_cols=None, quote_replace=' ', **kwargs):

    """
    create a dataframe from a section of an INP file
    :param inp_path:
    :param section:
    :param additional_cols:
    :param skip_headers:
    :param quote_replace:
    :return:
    """

    # format the section header for look up in headers OrderedDict
    sect = remove_braces(section).upper()

    # get list of all section headers in inp to use as section ending flags
    headers = get_inp_sections_details(inp_path, include_brackets=False)

    if sect not in headers:
        warnings.warn(f'{sect} section not found in {inp_path}')
        return pd.DataFrame()

    # extract the string and read into a dataframe
    start_string = format_inp_section_header(section)
    end_strings = [format_inp_section_header(h) for h in headers.keys()]
    s = extract_section_of_file(inp_path, start_string, end_strings, **kwargs)

    # replace occurrences of double quotes ""
    s = s.replace('""', quote_replace)

    # count tokens in first non-empty line, after the header, ignoring comments
    # if zero tokens counted (i.e. empty line), fall back to headers dict
    n_tokens = len(re.sub(r"(\n)\1+", r"\1", s).split('\n')[1].split(';')[0].split())
    n_tokens = len(headers[sect]['columns']) if n_tokens == 0 else n_tokens

    # and get the list of columns to use for parsing this section
    # add any additional columns needed for special cases (build instructions)
    additional_cols = [] if additional_cols is None else additional_cols
    cols = headers[sect]['columns'][:n_tokens] + additional_cols

    if headers[sect]['columns'][0] == 'blob':
        # return the whole row, without specific col headers
        return pd.read_csv(StringIO(s), delim_whitespace=False)
    else:
        try:
            df = pd.read_csv(StringIO(s), header=None, delim_whitespace=True,
                             skiprows=[0], index_col=0, names=cols)
        except:
            raise IndexError(f'failed to parse {section} with cols: {cols}. head:\n{s[:500]}')

    # confirm index name is string
    df = df.rename(index=str)
    return df


def get_link_coords(row, nodexys, verticies):
    """for use in an df.apply, to get coordinates of a conduit/link """

    # cast IDs to string
    inlet_id = str(row.InletNode)
    outlet_id = str(row.OutletNode)
    xys_str = nodexys.rename(index=str)

    x1 = xys_str.at[inlet_id, 'X']
    y1 = xys_str.at[inlet_id, 'Y']
    x2 = xys_str.at[outlet_id, 'X']
    y2 = xys_str.at[outlet_id, 'Y']

    if None in [x1, x2, y1, y2]:
        print(row.name, 'problem, no coords')
    # grab any extra verts, place in between up/dwn nodes
    res = [(x1, y1)]
    if row.name in verticies.index:
        xs = verticies.loc[row.name, 'X'].tolist()
        ys = verticies.loc[row.name, 'Y'].tolist()
        if isinstance(xs, list) and isinstance(ys, list):
            # if more than one vert for this link exists, arrays are returned
            # from verticies.get_value(). it then needs to be zipped up
            res = res + list(zip(xs, ys))
        else:
            res = res + [(xs, ys)]

    res = res + [(x2, y2)]

    return [res]  # nest in a list to force a series to be returned in a df.apply


def get_inp_options_df(inp_path):
    """
    Parse ONLY the OPTIONS section of the inp file into a dataframe
    :param inp_path: path to inp file
    :return: pandas.DataFrame
    >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY
    >>> ops = get_inp_options_df(MODEL_FULL_FEATURES_XY)
    >>> ops[:3]
                    Value
    Key
    FLOW_UNITS        CFS
    INFILTRATION   HORTON
    FLOW_ROUTING  DYNWAVE
    """
    from io import StringIO
    from swmmio.defs import INP_SECTION_TAGS, INP_OBJECTS
    ops_tag = '[OPTIONS]'
    ops_cols = INP_OBJECTS['OPTIONS']['columns']
    ops_string = extract_section_of_file(inp_path, ops_tag, INP_SECTION_TAGS, comment=';')
    ops_df = pd.read_csv(StringIO(ops_string), header=None, delim_whitespace=True, skiprows=[0],
                         index_col=0, names=ops_cols)
    return ops_df


def nodexy(row):
    if math.isnan(row.X) or math.isnan(row.Y):
        return None
    else:
        return [(row.X, row.Y)]
