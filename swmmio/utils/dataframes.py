from swmmio.utils import text as txt
from swmmio.utils import functions as funcs
from swmmio.swmmio import rpt, inp
import pandas as pd
import os

def create_dataframeBI(bi_path, section='[CONDUITS]'):
    """
    given a path to a biuld instructions file, create a dataframe of data in a
    given section
    """
    headerdefs = funcs.complete_inp_headers(bi_path)
    headerlist = headerdefs['headers'][section].split() + [';', 'Comment', 'Origin']
    tempfilepath = txt.extract_section_from_inp(bi_path, section,
                                                headerdefs=headerdefs,
                                                skipheaders=True)
    df = pd.read_table(tempfilepath, header=None, delim_whitespace=True,
                       skiprows=[0], index_col=0, names = headerlist, comment=None)

    os.remove(tempfilepath) #clean up

    return df

def create_dataframeINP (inp, section='[CONDUITS]', ignore_comments=True, comment_str=';'):
    """
    given an inp object, create a dataframe of data in a given section
    """

    #handle an inp object or a path to an INP file
    if type(inp) is not str:
        inp_path = inp.filePath
    else:
        inp_path = inp

    #find all the headers and their defs (section title with cleaned one-liner column headers)
    headerdefs = funcs.complete_inp_headers(inp_path)
    #create temp file with section isolated from inp file
    tempfilepath = txt.extract_section_from_inp(inp_path, section,
                                                headerdefs=headerdefs,
                                                ignore_comments=ignore_comments)
    if ignore_comments:
        comment_str = None
    if not tempfilepath:
        #if this head (section) was not found in the textfile, return a
        #blank dataframe with the appropriate schema
        print 'header "{}" not found in "{}"'.format(section, inp_path)
        print 'returning empty dataframe'
        headerlist = headerdefs['headers'].get(section, 'blob').split() + [';', 'Comment', 'Origin']
        blank_df = pd.DataFrame(data=None, columns=headerlist).set_index(headerlist[0])
        return blank_df

    if headerdefs['headers'][section] == 'blob':
        #return the whole row, without specifc col headers
        df = pd.read_table(tempfilepath, delim_whitespace=False, comment=comment_str)
    elif section == '[CURVES]' or section =='[TIMESERIES]':
        #return the whole row, without specifc col headers
        df = pd.read_table(tempfilepath, delim_whitespace=False)#, index_col=0)#, skiprows=[0])
    else:
        #this section header is recognized and will be organized into known columns
        headerlist = headerdefs['headers'][section].split() + [';', 'Comment', 'Origin']
        df = pd.read_table(tempfilepath, header=None, delim_whitespace=True, skiprows=[0],
                             index_col=0, names = headerlist, comment=comment_str)
        df[';'] = ';'
        #df.columns.names=[headerlist]
    os.remove(tempfilepath)

    #add new blank comment column after a semicolon column
    # df[';'] = ';'
    # df['Comment'] = ''


    return df

def create_dataframeRPT(rpt, section='Link Flow Summary', element_id=None):
    """
    given an rpt object, create a dataframe of data in a given section
    """

    #find all the headers and their defs (section title with cleaned one-liner column headers)
    headerdefs = funcs.complete_rpt_headers(rpt.filePath)
    #create temp file with section isolated from rpt file
    tempfilepath = txt.extract_section_from_rpt(rpt.filePath, section, headerdefs=headerdefs, element_id=element_id)

    if not tempfilepath:
        print 'header "{}" not found in "{}"'.format(section, rpt.filePath)
        return None

    if headerdefs['headers'][section] == 'blob':
        #return the whole row, without specifc col headers
        df = pd.read_table(tempfilepath, delim_whitespace=False, comment=";")
    else:
        if element_id:
            #we'retrying to pull a time series, parse the datetimes by
            #concatenating the Date Time columns (cols 1,2)
            df0 = pd.read_table(tempfilepath, delim_whitespace=True)
            df = df0[df0.columns[2:]] #the data sans date time columns
            df.index=pd.to_datetime(df0['Date'] + ' ' + df0['Time'])
            df.index.name = "".join(df0.columns[:2])
        else:
            #this section header is recognized and will be organized into known columns
            #headerlist = headerdefs['headers'][section].split()
            df = pd.read_table(tempfilepath, delim_whitespace=True, index_col=0)
        #df.columns.names=[headerlist]
    os.remove(tempfilepath)

    #add new blank comment column
    #df['Comment'] = ''


    return df
