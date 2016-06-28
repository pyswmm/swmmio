from swmmio.version_control import version_control as vc
from swmmio.version_control import utils as vc_utils
from swmmio.utils.functions import complete_inp_headers
from swmmio import swmmio
import pandas as pd
import os

def modify_model(inp_path, modified_section_header, new_data, overwrite=True):

    """
    modify an existing model by passing in new data (Pandas Dataframe)
    and the section header that should be modified. This funciton will overwrite
    all data in the old section with the passed data
    """

    tmpfilename = os.path.splitext(os.path.basename(inp_path))[0] + '_mod.inp'
    wd = os.path.dirname(inp_path)
    tmpfilepath = os.path.join(os.path.dirname(inp_path), tmpfilename)
    allheaders = complete_inp_headers(inp_path)
    basemodel = swmmio.Model(inp_path)

    with open(inp_path) as oldf:
        with open(tmpfilepath, 'w') as new:
            #create the companion excel file
            #create the MS Excel writer object
            xlpath = os.path.join(wd, basemodel.inp.name + '_modified.xlsx')
            excelwriter = pd.ExcelWriter(xlpath)
            vc_utils.create_info_sheet(excelwriter, basemodel)

            #write each line as is from the original model until we find the
            #header of the section we wish to overwrite
            found_section = False
            found_next_section = False
            for line in oldf:
                if modified_section_header in line:
                    #write the replacement data in the new file now
                    vc_utils.write_section(new, excelwriter, allheaders,
                                            modified_section_header, new_data, pad_top=False)

                    found_section = True

                if (
                    found_section and not found_next_section
                    and line.strip() in allheaders['headers']
                    and modified_section_header != line.strip()
                    ):

                    found_next_section = True
                    new.write('\n\n') #add some space before the next section

                if found_next_section or not found_section:
                    #write the lines from the original file
                    #if we haven't found the section to modify.
                    #if we have found the section and we've found the NEXT section
                    #continue writing original file's lines

                    new.write(line)

            if not found_section:
                #the header doesn't exist in the old model
                #so we should append it to the bottom of file
                vc_utils.write_section(new, excelwriter, allheaders,
                                        modified_section_header, new_data)

    excelwriter.save()
    #rename files and remove old if we should overwrite
    if overwrite:
        os.remove(inp_path)
        os.rename(tmpfilepath, inp_path)

    return swmmio.Model(inp_path)
