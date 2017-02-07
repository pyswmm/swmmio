from swmmio.defs.sectionheaders import inp_header_dict, rpt_header_dict
from collections import deque

def random_alphanumeric(n=6):
	import random
	chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
	return ''.join(random.choice(chars) for i in range(n))


def complete_inp_headers (inpfilepath):
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

def complete_rpt_headers (rptfilepath):
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

def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
		if dictionary:
			result.update(dictionary)
    return result

def trace_from_node(conduits, startnode, mode='up', stopnode=None):

	"""
	trace up and down a SWMM model given a start node and optionally an
	stop node.
	"""

	traced_nodes = [startnode] #include the starting node
	traced_conduits = []

	def trace(node_id):
		for conduit, data in conduits.iterrows():
			if mode == 'up' and data.OutletNode == node_id and conduit not in traced_conduits:

				traced_nodes.append(data.InletNode)
				traced_conduits.append(conduit)

				if stopnode and data.InletNode == stopnode:
					break
				trace(data.InletNode)

			if mode == 'down' and data.InletNode == node_id and conduit not in traced_conduits:
				traced_nodes.append(data.OutletNode)
				traced_conduits.append(conduit)

				if stopnode and data.OutletNode == stopnode:
					break
				trace(data.OutletNode)

	#kickoff the trace
	print "Starting trace {} from {}".format(mode, startnode)
	trace(startnode)
	print "Traced {0} nodes from {1}".format(len(traced_nodes), startnode)
	return {'nodes':traced_nodes, 'conduits':traced_conduits}
