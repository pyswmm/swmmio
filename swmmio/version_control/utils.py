from datetime import datetime
import pandas as pd
from swmmio.utils import functions


def write_inp_section(file_object, allheaders, sectionheader, section_data, pad_top=True):

    """
    given an open file object, excelwriter object, list of header sections, the curent
    section header, and the section data in a Pandas Dataframe format, this function writes
    the data to the file object and to a companion excel file.
    """

    f = file_object
    add_str =  ''

    if pad_top:
        f.write('\n\n' + sectionheader + '\n') #add SWMM-friendly header e.g. [DWF]
    else:
        f.write(sectionheader + '\n')
    if allheaders['headers'].get(sectionheader, 'blob') == 'blob' and not section_data.empty:
        #to left justify based on the longest string in the blob column
        formatter = '{{:<{}s}}'.format(section_data[sectionheader].str.len().max()).format
        add_str = section_data.fillna('').to_string(
                                                    index_names=False,
                                                    header=False,
                                                    index=False,
                                                    justify='left',
                                                    formatters={sectionheader:formatter}
                                                    )
        # #write section to excel sheet
        # sheetname = sectionheader.replace('[', "").replace(']', "")
        # section_data.to_excel(excelwriter, sheetname, index=False)

    elif not section_data.empty:
        #naming the columns to the index name so the it prints in-line with col headers
        f.write(';')
        #to left justify on longest string in the Comment column
        #this is overly annoying, to deal with 'Objects' vs numbers to removed
        #one byte added from the semicolon (to keep things lined up)
        objectformatter =   {hedr:'{{:<{}}}'.format(section_data[hedr].apply(str).str.len().max()).format
                                for hedr in section_data.columns}
        numformatter =      {hedr:' {{:<{}}}'.format(section_data[hedr].apply(str).str.len().max()).format
                                for hedr in section_data.columns if section_data[hedr].dtype!="O"}
        objectformatter.update(numformatter)
        add_str = section_data.fillna('').to_string(
                                                    index_names=False,
                                                    header=True,
                                                    justify='left',
                                                    formatters=objectformatter#{'Comment':formatter}
                                                    )

        # #write section to excel sheet
        # sheetname = sectionheader.replace('[', "").replace(']', "")
        # section_data.to_excel(excelwriter, sheetname)


    #write the dataframe as a string
    f.write(add_str)

def write_excel_inp_section(excelwriter, sectionheader, allheaders, section_data):

    if not section_data.empty:
        sheetname = sectionheader.replace('[', "").replace(']', "")

        if allheaders['headers'].get(sectionheader, 'blob') == 'blob' and not section_data.empty:
            #write section to excel sheet
            section_data.to_excel(excelwriter, sheetname, index=False)
        else:
            #clean up the format a bit
            # workbook = excelwriter.book
            # elem_fmt = workbook.add_format({'align': 'left'})
            # worksheet = excelwriter.sheets[sheetname]
            # worksheet.set_column('A:A', 20)

            section_data.to_excel(excelwriter, sheetname)

def create_change_info_sheet(excelwriter, model1, model2, name='', message=''):

    ix =  ['Date', 'BaselineModel', 'TargetModel', 'Commit', 'Name', 'Comment']
    vals =  [
            datetime.now().strftime("%y-%m-%d %H:%M"),
            model1.inp.filePath,
            model2.inp.filePath,
            functions.random_alphanumeric(12),
            name,
            message
            ]
    df = pd.DataFrame(data=vals, index=ix,columns=['FileInfo'])
    df.to_excel(excelwriter, 'FileInfo')


def create_info_sheet(excelwriter, basemodel, parent_models=[]):

    #create an info sheet for the Excel file
    timeofcreation = datetime.now()
    s = pd.Series([datetime.now(), basemodel.inp.filePath] + [x.inp.filePath for x in parent_models] )
    s.index = ['DateCreated', 'Basemodel']+['ParentModel_' + str(i) for i,x in enumerate(parent_models)]
    df = pd.DataFrame(s, columns=['FileInfo'])
    df.to_excel(excelwriter, 'FileInfo')
