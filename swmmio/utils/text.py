#UTILITY FUNCTIONS AIMED AT I/O OPERATIONS WITH TEXT FILES
#STANDARD READING AND WRITING OF TEXT FILES (E.G. .INP AND .RPT)

import os
from swmmio.utils.functions import random_alphanumeric, complete_inp_headers, complete_rpt_headers


#default file path suffix
txt = '.txt'

def extract_section_from_file(filepath, sectionheader, element_id=None, cleanheaders=True, startfile=False, headerdefs=None):
    f_extension = os.path.splitext(filepath)[1]
    if f_extension == '.inp':
        return extract_section_from_inp(filepath, sectionheader, cleanheaders, startfile, headerdefs)
    if f_extension == '.rpt':
        return extract_section_from_rpt(filepath, sectionheader, element_id, cleanheaders, startfile, headerdefs)

def extract_section_from_inp(filepath, sectionheader, cleanheaders=True, startfile=False, headerdefs=None):
    """
    INPUT path to text file (inp, rpt, etc) and a text string
    matchig the section header of the to be extracted

    creates a new text file in the same directory as the filepath
    and returns the path to the new file.

    optionally inserts row at begining of file with one-line headers that are
    defined in swmmio.defs.sectionheaders (useful for creating dataframes)
    """

    #headers = she.complete_inp_headers(inp)['headers']
    if not headerdefs:
        allheaders = complete_inp_headers(filepath)['headers']
    else:
        allheaders = headerdefs['headers']

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
                    if cleanheaders:
                        if allheaders[sectionheader] != 'blob':
                            line = allheaders[sectionheader] + '\n'
                        else:
                            line = sectionheader + '\n'

                if startfound:
                    newf.write(line)
    if not startfound:
        #input section header was not found in the file
        return None
    if startfile:
        os.startfile(outfilepath)

    return outfilepath


def extract_section_from_rpt(filepath, sectionheader, element_id=None, cleanheaders=True, startfile=False, headerdefs=None):
    """
    INPUT path to rpt file and a text string
    matchig the section header of the to be extracted

    creates a new text file in the same directory as the filepath
    and returns the path to the new file.

    optionally inserts row at begining of file with one-line headers that are
    defined in swmmio.defs.sectionheaders (useful for creating dataframes)
    dede
    """
    if not headerdefs:
        allheaders = complete_rpt_headers(filepath)['headers']
    else:
        allheaders = headerdefs['headers']

    with open(filepath) as f:


        wd = os.path.dirname(filepath)
        newfname = sectionheader + '_' + random_alphanumeric(6)
        outfilepath = os.path.join(wd, newfname + txt)

        sectionstartfound = False #where we see the section header name
        elementstartfound = False #where we see the element time series
        datastartfound = False #where we see actual data after the header text
        endfound = False
        hyphencount = 0 #count how many hyphen rows we pass after sectionstartfound

        with open(outfilepath, 'w') as newf:

            for line in f:

                if sectionstartfound and line.strip() in allheaders:
                    #if we've found the begining of the section and we run
                    #into another known header, we're at the end
                    endfound = True
                    break

                elif not sectionstartfound and sectionheader in line:
                    #if we haven't found the start of the section yet, the
                    #sectionheader is in the current line,
                    #then we've found the begining of the section of interest
                    print 'sectionstartfound found'
                    sectionstartfound = True

                    #replace line with usable headers
                    if cleanheaders and [sectionheader] != 'blob':
                        headerrow = allheaders[sectionheader] + '\n'
                        newf.write(headerrow)

                if sectionstartfound and element_id:
                    #keep searching for the start of actual good data
                    #string starting an element time series e.g. <<< Node D68_1_4 >>>
                    elem_start_string = ' '.join(["<<<", sectionheader.split()[0], element_id, ">>>"])

                    if element_id and elem_start_string in line:
                        print 'element_id found: {}'.format(line)
                        #if we should look for an element_id and it
                        #is in the current line
                        elementstartfound = True
                        #datastartfound = True
                    if elementstartfound:
                        if hyphencount == 2:
                            datastartfound = True
                            newf.write(line) #write the first line
                            if len(line.strip()) == 0:
                                #if line is blank after we've found the data,
                                #we can be confident that we've found the end
                                break
                        if '------------' in line:
                            #track how many rows with hyphens are passed
                            #two rows should occur before actual data is written
                            hyphencount += 1
                elif sectionstartfound and not element_id:

                    if hyphencount == 2:
                        datastartfound = True
                        newf.write(line) #write the first line
                        if len(line.strip()) == 0:
                            #if line is blank after we've found the data,
                            #we can be confident that we've found the end
                            break
                    if '------------' in line:
                        #track how many rows with hyphens are passed
                        #two rows should occur before actual data is written
                        hyphencount += 1

    if not sectionstartfound:
        #input section header was not found in the file
        return None
    if startfile:
        os.startfile(outfilepath)

    return outfilepath
    #pass
