#UTILITY FUNCTIONS AIMED AT I/O OPERATIONS WITH TEXT FILES
#STANDARD READING AND WRITING OF TEXT FILES (E.G. .INP AND .RPT)

import os

from swmmio.utils.functions import random_alphanumeric, complete_inp_headers, complete_rpt_headers


#default file path suffix
txt = '.txt'

def inline_comments_in_inp(filepath, overwrite=False):

    """
    with an existing INP file, shift any comments that have been placed above the
    element (behavoir from saving in GUI) and place them to the right, inline with
    the element. To improve readability
    """
    newfilename = os.path.splitext(os.path.basename(filepath))[0] + '_unGUI.inp'
    newfilepath = os.path.join(os.path.dirname(filepath), newfilename)
    allheaders = complete_inp_headers(filepath)

    with open(filepath) as oldf:
        with open(newfilepath, 'w') as new:

            comment_concat = [] #to hold list of comments (handles multiline comments)
            current_section = list(allheaders.keys())[0]
            for line in oldf:

                #determine what section we are in by noting when we pass double brackets
                if '[' and ']' in line:
                    current_section = line.strip()


                #if line.count(';') == 1 and line.strip()[0]==';':
                if len(line.strip()) > 1:
                    if line.strip()[0]==';' and ''.join(line.strip()[:2]) != ';;':
                        #print line.strip()[:2]
                        #this is a comment bc first char is ; and there
                        #seconf char is not (which would resember the header section)
                        words = line.split()
                        hdrs = allheaders[current_section]['columns']#headerrow.split()
                        perc_match_to_header = float(len([x for x in words if x in hdrs])) / float(len(hdrs))
                        if perc_match_to_header <= 0.75:
                            comment_concat.append(line.strip())
                    else:
                        #print comment_concat
                        #this row has data, tack any comment to the line end
                        comment_string = ''
                        if len(comment_concat) > 0:
                            comment_string = r' '.join(comment_concat)
                        newlinestring = line.strip() + comment_string + '\n'
                        new.write(newlinestring)
                        comment_concat = []
                else:
                    #write the short line
                    new.write(line)

    #rename files and remove old if we should overwrite
    if overwrite:
        os.remove(filepath)
        os.rename(newfilepath, filepath)


def extract_section_of_file(file_path, start_string, end_string, comment_str=';'):
    """
    Extract a portion of a file found between a start string and a end string/condition
    :param file_path: path to file
    :param start_string: token used to start the extraction (included)
    :param end_string: token used to end the extraction
    :param comment: ignore any text in a line behind a comment char
    :return: string
    >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY
    >>> s = extract_section_of_file(MODEL_FULL_FEATURES_XY, '[EVAPORATI', '[', comment_str=None)
    >>> print(s.strip())
    [EVAPORATION]
    ;;Data Source    Parameters
    ;;-------------- ----------------
    CONSTANT         0.0
    DRY_ONLY         NO
    """

    if isinstance(end_string, str):
        end_string = [end_string]

    start_found = False
    out_string = ''
    with open(file_path, 'r') as f:

        for line in f:

            if start_found and any(es in line for es in end_string):
                # print('end found: {}'.format(line))
                break
            elif not start_found and start_string in line:
                start_found = True

            if start_found:
                if comment_str is not None:
                    # ignore anything after a comment
                    if comment_str in line:
                        s = line.split(comment_str)[0] + '\n'
                        out_string += s
                    else:
                        out_string += line
                else:
                    out_string += line

    return out_string


def extract_section_from_inp(filepath, sectionheader, cleanheaders=True,
                            startfile=False, headerdefs=None, ignore_comments=False,
                            return_string=False, skiprows=0, skipheaders=False):
    """
    INPUT path to text file (inp, rpt, etc) and a text string
    matching the section header of the to be extracted

    creates a new text file in the same directory as the filepath
    and returns the path to the new file.

    optionally inserts row at begining of file with one-line headers that are
    defined in swmmio.defs.sectionheaders (useful for creating dataframes)
    """

    #headers = she.complete_inp_headers(inp)['headers']
    if not headerdefs:
        allheaders = complete_inp_headers(filepath)
    else:
        allheaders = headerdefs

    with open(filepath) as f:
        startfound = False
        wd = os.path.dirname(filepath)
        newfname = sectionheader + '_' + random_alphanumeric(6)
        outfilepath = os.path.join(wd, newfname + txt)
        out_string = '' #populate if we only want a string returned
        line_count = 0
        with open(outfilepath, 'w') as newf:

            for line in f:

                if startfound and line.strip() in allheaders:
                    #print 'end found: {}'.format(line.strip())
                    break
                elif not startfound and sectionheader in line:
                    startfound = True
                    #replace line with usable headers
                    if cleanheaders:
                        if allheaders[sectionheader]['columns'][0] != 'blob':
                            line = ' '.join(allheaders[sectionheader]['columns']) + '\n'
                        else:
                            line = sectionheader + '\n'

                if startfound:
                    if ignore_comments:
                        #ignore anything after a comment
                        if ';' in line:
                            s = line.split(';')[0] + '\n'
                            out_string += s #build the overall out string (optional use)
                            newf.write(s)
                        else:
                            newf.write(line)
                            out_string += line
                    elif skipheaders:
                        #check if we're at a inp header row with ';;' or the section
                        #header e.g. [XSECTIONS]. If so, skip the row bc skipheader = True
                        if line.strip()[:2] != ";;" and line.strip() != sectionheader:
                            newf.write(line)
                            out_string += line
                    elif line_count >= skiprows:
                        newf.write(line)
                        out_string += line

                    line_count += 1

    if not startfound:
        #input section header was not found in the file
        os.remove(outfilepath)
        return None
    if return_string:
        #return a string rep of the extracted section
        os.remove(outfilepath) #not needed so delete (maybe wasteful to make in 1st place)
        return out_string

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
                    #print '{} section found'.format(sectionheader)
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
                        print('element_id found: {}'.format(line))
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


