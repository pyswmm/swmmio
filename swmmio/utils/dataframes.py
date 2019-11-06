import os
from io import StringIO

import pandas as pd

from swmmio.defs import INP_OBJECTS, HEADERS_YML
from swmmio.utils import text as txt
from swmmio.utils.functions import format_inp_section_header, remove_braces
from swmmio.utils.text import extract_section_of_file, get_inp_sections_details, get_rpt_sections_details
import warnings


def dataframe_from_bi(bi_path, section='[CONDUITS]'):
    """
    given a path to a build instructions file, create a dataframe of data in a
    given section
    """

    df = dataframe_from_inp(bi_path, section,
                            additional_cols=[';', 'Comment', 'Origin'],
                            comment=';;')


    # headerdefs = get_inp_sections_details(bi_path)
    # headerlist = headerdefs[section]['columns'] + [';', 'Comment', 'Origin']
    # tempfilepath = txt.extract_section_from_inp(bi_path, section,
    #                                             headerdefs=headerdefs,
    #                                             skipheaders=True)
    # df = pd.read_csv(tempfilepath, header=None, delim_whitespace=True,
    #                  skiprows=[0], index_col=0, names=headerlist, comment=None)
    #
    # os.remove(tempfilepath)  # clean up

    # s = extract_section_of_file(inp_path, start_string, end_strings,
    #                             skip_headers=skip_headers, **kwargs)
    # df = pd.read_csv(StringIO(s), header=None, delim_whitespace=True, skiprows=[0],
    #                  index_col=0, names=cols, **kwargs)

    return df


def create_dataframeINP(inp_path, section='[CONDUITS]', ignore_comments=True,
                        comment_str=';', comment_cols=True, headers=None):
    """

    given a path to an INP file, create a dataframe of data in the given
    section.

    :param inp_path:
    :param section:
    :param ignore_comments:
    :param comment_str:
    :param comment_cols:
    :param headers:
    :return:
    >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY
    >>> df = create_dataframeINP(MODEL_FULL_FEATURES_XY, '[CONDUITS]')
    >>> df
    """

    # find all the headers and their defs (section title with cleaned one-liner column headers)
    headerdefs = get_inp_sections_details(inp_path)
    # print(f'headerdefs[{section}]: {headerdefs[section]}')
    # create temp file with section isolated from inp file
    tempfilepath = txt.extract_section_from_inp(inp_path, section,
                                                headerdefs=headerdefs,
                                                ignore_comments=ignore_comments)

    if ignore_comments:
        comment_str = None
    if not tempfilepath:
        # if this head (section) was not found in the textfile, return a
        # blank dataframe with the appropriate schema
        print('header {} not found in {}\nReturning empty DataFrame.'.format(section, inp_path))
        # headerlist = headerdefs['headers'].get(section, 'blob').split() + [';', 'Comment', 'Origin']

        headerlist = INP_OBJECTS[section.replace('[', '').replace(']', '')]['columns']
        if headers is not None:
            headerlist = headers[section]

        if comment_cols:
            headerlist = headerlist + [';', 'Comment', 'Origin']

        blank_df = pd.DataFrame(data=None, columns=headerlist).set_index(headerlist[0])
        return blank_df

    if headerdefs[section]['columns'][0] == 'blob':
        # return the whole row, without specifc col headers
        df = pd.read_csv(tempfilepath, delim_whitespace=False, comment=comment_str)
    elif section == '[CURVES]' or section == '[TIMESERIES]':
        # return the whole row, without specifc col headers
        df = pd.read_csv(tempfilepath, delim_whitespace=False)  # , index_col=0)#, skiprows=[0])
    else:
        # this section header is recognized and will be organized into known columns
        headerlist = headerdefs[section]['columns']
        if headers is not None:
            headerlist = headers[section]
        if comment_cols:
            headerlist = headerlist + [';', 'Comment', 'Origin']
        dtypes = {'InletNode': str, 'OutletNode': str}
        df = pd.read_csv(tempfilepath, header=None, delim_whitespace=True, skiprows=[0],
                           index_col=0, names=headerlist, comment=comment_str, dtype=dtypes)# , encoding='latin1')

        if comment_cols:
            # add new blank comment column after a semicolon column
            df[';'] = ';'

    os.remove(tempfilepath)

    return df.rename(index=str)


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
        items = line.strip().split()
        if len(items) == 3:
            items = [items[0], None, items[1], items[2]]
        if len(items) == 4:
            data.append(items)

    df = pd.DataFrame(data=data, columns=cols)
    df = df.set_index(['Name', 'Type'])

    return df


def dataframe_from_rpt(rpt_path, section):

    # get list of all section headers in rpt to use as section ending flags
    headers = get_rpt_sections_details(rpt_path)

    if section not in headers:
        warnings.warn(f'{section} section not found in {rpt_path}')
        return pd.DataFrame()

    # and get the list of columns to use for parsing this section
    end_strings = list(headers.keys())
    end_strings.append('***********')
    start_strings = [section, '-'*20, '-'*20]
    cols = headers[section]['columns']

    # extract the string and read into a dataframe
    s = extract_section_of_file(rpt_path, start_strings, end_strings)
    df = pd.read_csv(StringIO(s), header=None, delim_whitespace=True, skiprows=[0],
                     index_col=0, names=cols)

    return df


def dataframe_from_inp(inp_path, section, additional_cols=None, quote_replace=' ', **kwargs):

    """
    :param inp_path:
    :param section:
    :param additional_cols:
    :param skip_headers:
    :param quote_replace:
    :return:
    >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY
    >>> dataframe_from_inp(MODEL_FULL_FEATURES_XY, 'conduits')
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

    # and get the list of columns to use for parsing this section
    # add any additional columns needed for special cases (build instructions)
    additional_cols = [] if additional_cols is None else additional_cols
    cols = headers[sect]['columns'] + additional_cols

    if headers[sect]['columns'][0] == 'blob':
        # return the whole row, without specific col headers
        return pd.read_csv(StringIO(s), delim_whitespace=False)
    else:
        return pd.read_csv(StringIO(s), header=None, delim_whitespace=True,
                           skiprows=[0], index_col=0, names=cols)

    # return df


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