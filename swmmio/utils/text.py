#UTILITY FUNCTIONS AIMED AT I/O OPERATIONS WITH TEXT FILES
#STANDARD READING AND WRITING OF TEXT FILES (E.G. .INP AND .RPT)

import os
from swmmio.utils.functions import random_alphanumeric, complete_inp_headers


#default file path suffix
txt = '.txt'

def extract_section_from_file(filepath, sectionheader, cleanheaders=False, startfile=False):
    """
    INPUT path to text file (inp, rpt, etc) and a text string
    matchig the section header of the to be extracted

    creates a new text file in the same directory as the filepath
    and returns the path to the new file.

    optionally inserts row at begining of file with one-line headers that are
    defined in swmmio.defs.inpheaders (useful for creating dataframes)
    """

    #headers = she.complete_inp_headers(inp)['headers']

    allheaders = complete_inp_headers(filepath)['headers']
    with open(filepath) as f:
        startfound = False
        endfound = False
        #outFilePath = inp.dir + "\\" + inp.name + "_" + section + ".txt"
        wd = os.path.dirname(filepath)
        newfname = sectionheader + '_' + random_alphanumeric(6)
        outfilepath = os.path.join(wd, newfname + txt)
        with open(outfilepath, 'w') as newf:

            for line in f:

                if startfound and line.strip() in allheaders:
                    endfound = True
                    #print 'end found: {}'.format(line.strip())
                    break
                elif not startfound and sectionheader in line:
                    startfound = True
                    #replace line with usable headers
                    if cleanheaders and [sectionheader] != 'blob':
                        line = allheaders[sectionheader] + '\n'

                if startfound:
                    newf.write(line)

    if startfile:
        os.startfile(outfilepath)

    return outfilepath
