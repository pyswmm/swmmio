from datetime import datetime
import pandas as pd


def write_section(file_object, excelwriter, allheaders, sectionheader, section_data, pad_top=True):

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
        #write section to excel sheet
        sheetname = sectionheader.replace('[', "").replace(']', "")
        section_data.to_excel(excelwriter, sheetname, index=False)

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

        #write section to excel sheet
        sheetname = sectionheader.replace('[', "").replace(']', "")
        section_data.to_excel(excelwriter, sheetname)


    #write the dataframe as a string
    f.write(add_str)

def create_info_sheet(excelwriter, basemodel, parent_models=[]):

    #create an info sheet for the Excel file
    timeofcreation = datetime.now()
    s = pd.Series([datetime.now(), basemodel.inp.filePath] + [x.inp.filePath for x in parent_models] )
    s.index = ['DateCreated', 'Basemodel']+['ParentModel_' + str(i) for i,x in enumerate(parent_models)]
    df = pd.DataFrame(s, columns=['FileInfo'])
    df.to_excel(excelwriter, 'FileInfo')
