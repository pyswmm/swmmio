import os
import pandas as pd

from swmmio.defs import INP_OBJECTS
from swmmio.utils import text as txt
from swmmio.utils import functions as funcs
from swmmio.utils.text import extract_section_of_file


def create_dataframeBI(bi_path, section='[CONDUITS]'):
    """
    given a path to a build instructions file, create a dataframe of data in a
    given section
    """
    headerdefs = funcs.complete_inp_headers(bi_path)
    headerlist = headerdefs[section]['columns'] + [';', 'Comment', 'Origin']
    tempfilepath = txt.extract_section_from_inp(bi_path, section,
                                                headerdefs=headerdefs,
                                                skipheaders=True)
    df = pd.read_csv(tempfilepath, header=None, delim_whitespace=True,
                     skiprows=[0], index_col=0, names=headerlist, comment=None)

    os.remove(tempfilepath)  # clean up

    return df


def create_dataframeINP(inp_path, section='[CONDUITS]', ignore_comments=True,
                        comment_str=';', comment_cols=True, headers=None):
    """
    given a path to an INP file, create a dataframe of data in the given
    section.
    """

    # find all the headers and their defs (section title with cleaned one-liner column headers)
    headerdefs = funcs.complete_inp_headers(inp_path)
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


def create_dataframe_multi_index(inp_path, section='[CURVES]', ignore_comments=True,
                        comment_str=';', comment_cols=True, headers=None):
    # find all the headers and their defs (section title with cleaned one-liner column headers)
    headerdefs = funcs.complete_inp_headers(inp_path)
    # create temp file with section isolated from inp file
    tempfilepath = txt.extract_section_from_inp(inp_path, section,
                                                headerdefs=headerdefs,
                                                ignore_comments=ignore_comments,
                                                skipheaders=True)

    headerlist = HEADERS['inp_sections'][section]

    with open(tempfilepath, 'r') as f:
        data = []
        for line in f.readlines():
            items = line.strip().split()
            if len(items) == 3:
                items = [items[0], None, items[1], items[2]]
            if len(items) == 4:
                data.append(items)

    # df = pd.read_csv(tempfilepath, header=None, delim_whitespace=True, skiprows=[0],
    #                  index_col=[0,1], names=headerlist, comment=comment_str)

    df = pd.DataFrame(data=data, columns=headerlist)
    df = df.set_index(['Name', 'Type'])


    # os.startfile(tempfilepath)
    os.remove(tempfilepath)
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


def create_dataframeRPT(rpt_path, section='Link Flow Summary', element_id=None):
    """
    given a path to an RPT file, create a dataframe of data in the given
    section.
    """

    # find all the headers and their defs (section title with cleaned one-liner column headers)
    headerdefs = funcs.complete_rpt_headers(rpt_path)
    # create temp file with section isolated from rpt file
    tempfilepath = txt.extract_section_from_rpt(rpt_path, section,
                                                headerdefs=headerdefs,
                                                element_id=element_id)

    if not tempfilepath:
        print('header "{}" not found in "{}"'.format(section, rpt_path))
        return None

    if headerdefs['headers'][section] == 'blob':
        # return the whole row, without specifc col headers
        df = pd.read_table(tempfilepath, delim_whitespace=False, comment=";")
    else:
        if element_id:
            # we'retrying to pull a time series, parse the datetimes by
            # concatenating the Date Time columns (cols 1,2)
            df0 = pd.read_csv(tempfilepath, delim_whitespace=True)
            df = df0[df0.columns[2:]]  # the data sans date time columns
            df.index = pd.to_datetime(df0['Date'] + ' ' + df0['Time'])
            df.index.name = "".join(df0.columns[:2])
        else:
            # this section header is recognized, will be organized into known cols
            df = pd.read_csv(tempfilepath, delim_whitespace=True, index_col=0)

    os.remove(tempfilepath)

    return df


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
    from pandas.compat import StringIO
    from swmmio.defs import INP_SECTION_TAGS, INP_OBJECTS
    ops_tag = '[OPTIONS]'
    ops_cols = INP_OBJECTS['OPTIONS']['columns']
    ops_string = extract_section_of_file(inp_path, ops_tag, INP_SECTION_TAGS, comment_str=';')
    ops_df = pd.read_csv(StringIO(ops_string), header=None, delim_whitespace=True, skiprows=[0],
                         index_col=0, names=ops_cols)
    return ops_df
