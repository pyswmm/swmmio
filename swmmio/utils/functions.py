from swmmio.defs.inpheaders import inp_header_dict, rpt_header_dict
from collections import deque

def random_alphanumeric(n=6):
	import random
	chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
	return ''.join(random.choice(chars) for i in range(n))


def complete_inp_headers (inpfilepath, inp_header_dict=inp_header_dict):
    """
    creates a dictionary with all the headers found in an INP file
    (which varies based on what the user has defined in a given model)
    and updates them based on the definitions in inp_header_dict
    this ensures the list is comprehensive

    RETURNS:
        a dictionary including
            'headers'->
                    header section keys and their respective cleaned column headers
            'order' ->
                    an array of section headers found in the INP file
                    that perserves the original order
    """
    foundheaders= {}
    order = []
    #print inp_header_dict
    with open(inpfilepath) as f:
        for line in f:
            if '[' and ']' in line:
                h = line.strip()
                order.append(h)
                if h in inp_header_dict:
                    foundheaders.update({h:inp_header_dict[h]})
                else:
                    foundheaders.update({h:'blob'})

    return {'headers':foundheaders, 'order':order}

def complete_rpt_headers (rptfilepath, rpt_header_dict=rpt_header_dict):
    """
    creates a dictionary with all the headers found in an RPT file
    (which varies based on what the user has defined in a given model)
    and updates them based on the definitions in rpt_header_dict
    this ensures the list is comprehensive

    RETURNS:
        a dictionary including
            'headers'->
                    header section keys and their respective cleaned column headers
            'order' ->
                    an array of section headers found in the RPT file
                    that perserves the original order
    """
    foundheaders= {}
    order = []
    with open(rptfilepath) as f:
        buff3line = deque()
        for line in f:


            #maintains a 3 line buffer and looks for instances where
            #a top and bottom line have '*****' and records the middle line
            #typical of section headers in RPT files
            buff3line.append(line)
            if len(buff3line) > 3:
                buff3line.popleft()

            if ('***********'in buff3line[0] and
				'***********'in buff3line[2] and
				len(buff3line[1].strip()) > 0):
                h = buff3line[1].strip()
                order.append(h)
                if h in rpt_header_dict:
                    foundheaders.update({h:rpt_header_dict[h]})
                else:
                    foundheaders.update({h:'blob'})

    return {'headers':foundheaders, 'order':order}
