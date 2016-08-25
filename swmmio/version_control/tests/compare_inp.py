import os


def remove_comments_and_crlf(inp_path, comment_string=';', overwrite=False):
    tmpfilename = os.path.splitext(os.path.basename(inp_path))[0] + '_mod.inp'
    tmpfilepath = os.path.join(os.path.dirname(inp_path), tmpfilename)

    with open (inp_path) as oldf:
        with open(tmpfilepath, 'w') as newf:
            for line in oldf:

                if ';' in line:
                    #remove the comments
                    if line.strip()[0] == comment_string:
                        #skip the whole line
                        pass
                    else:
                        #write the line to the left of the comment
                        non_comment_line = line.split(';')[0]
                        newf.write(non_comment_line + '\n')
                elif line == '\n':
                    pass
                else:
                    newf.write(line)

    if overwrite:
        os.remove(inp_path)
        os.rename(tmpfilepath, inp_path)


def line_by_line(path1, path2, outfile):
    """
    given paths to two INP files, return a text file showing where differences
    occur in line-by-line fashion. If the order of elements do not match, this
    will be recorded as a difference.

    ignores any spaces in a file such that lines with more or less white space
    having the same non-whitespace will be considered equal.

    """

    #outfile =r"P:\06_Tools\v_control\Testing\cleaned\linebyline.txt"
    with open(outfile, 'w') as diff_file:
        with open (path1) as f1:
            with open(path2) as f2:

                line1 = next(f1)
                line2 = next(f2)

                while line1 and line2:
                    #replace all white space to check only actual content

                    if line1.replace(" ", "") != line2.replace(" ", ""):
                        diff_file.write(line1)

                    line1 = next(f1)
                    line2 = next(f2)
