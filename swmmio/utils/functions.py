import pandas as pd
import networkx as nx
import warnings
# from swmmio import get_inp_options_df, INFILTRATION_COLS


def random_alphanumeric(n=6):
    import random
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(chars) for i in range(n))


def model_to_networkx(model, drop_cycles=True):
    from swmmio.utils.dataframes import dataframe_from_rpt
    '''
    Networkx MultiDiGraph representation of the model
    '''
    from geojson import Point, LineString

    def multidigraph_from_edges(edges, source, target):
        '''
        create a MultiDiGraph from a dataframe of edges, using the row index
        as the key in the MultiDiGraph
        '''
        us = edges[source]
        vs = edges[target]
        keys = edges.index
        data = edges.drop([source, target], axis=1)
        d_dicts = data.to_dict(orient='records')

        G = nx.MultiDiGraph()

        G.add_edges_from(zip(us, vs, keys, d_dicts))

        return G

    # parse swmm model results with swmmio, concat all links into one dataframe
    nodes = model.nodes()
    links = model.links()
    links['facilityid'] = links.index

    # create a nx.MultiDiGraph from the combined model links, add node data, set CRS
    G = multidigraph_from_edges(links, 'InletNode', target='OutletNode')
    G.add_nodes_from(zip(nodes.index, nodes.to_dict(orient='records')))

    # create geojson geometry objects for each graph element
    for u, v, k, coords in G.edges(data='coords', keys=True):
        if coords:
            G[u][v][k]['geometry'] = LineString(coords)
    for n, coords in G.nodes(data='coords'):
        if coords:
            G.nodes[n]['geometry'] = Point(coords[0])

    if drop_cycles:
        # remove cycles
        cycles = list(nx.simple_cycles(G))
        if len(cycles) > 0:
            warnings.warn(f'cycles detected and removed: {cycles}')
            G.remove_edges_from(cycles)

    G.graph['crs'] = model.crs
    return G


def find_invalid_links(inp, node_ids=None, link_type='conduits', drop=False):
    elems = getattr(inp, link_type)
    invalids = elems.index[~(elems.InletNode.isin(node_ids) & elems.OutletNode.isin(node_ids))]
    if drop:
        df = elems.loc[elems.InletNode.isin(node_ids) & elems.OutletNode.isin(node_ids)]
        setattr(inp, link_type, df)
    return invalids.tolist()


def trim_section_to_nodes(inp, node_ids=None, node_type='junctions', drop=True):
    elems = getattr(inp, node_type)
    invalids = elems.index[~(elems.index.isin(node_ids))]
    if drop:
        df = elems.loc[elems.index.isin(node_ids)]
        setattr(inp, node_type, df)
    return invalids.tolist()


# def drop_invalid_model_elements(inp):
#     """
#     Identify references to elements in the model that are undefined and remove them from the
#     model. These should coincide with warnings/errors produced by SWMM5 when undefined elements
#     are referenced in links, subcatchments, and controls.
#     :param model: swmmio.Model
#     :return:
#     >>> import swmmio
#     >>> m = swmmio.Model(MODEL_FULL_FEATURES_INVALID)
#     >>> drop_invalid_model_elements(m.inp)
#     ['InvalidLink2', 'InvalidLink1']
#     >>> m.inp.conduits.index
#     Index(['C1:C2', 'C2.1', '1', '2', '4', '5'], dtype='object', name='Name')
#     """
#     from swmmio.utils.dataframes import create_dataframeINP
#     juncs = create_dataframeINP(inp.path, "[JUNCTIONS]").index.tolist()
#     outfs = create_dataframeINP(inp.path, "[OUTFALLS]").index.tolist()
#     stors = create_dataframeINP(inp.path, "[STORAGE]").index.tolist()
#     nids = juncs + outfs + stors
#
#     # drop links with bad refs to inlet/outlet nodes
#     inv_conds = find_invalid_links(inp, nids, 'conduits', drop=True)
#     inv_pumps = find_invalid_links(inp, nids, 'pumps', drop=True)
#     inv_orifs = find_invalid_links(inp, nids, 'orifices', drop=True)
#     inv_weirs = find_invalid_links(inp, nids, 'weirs', drop=True)
#
#     # drop other parts of bad links
#     invalid_links = inv_conds + inv_pumps + inv_orifs + inv_weirs
#     inp.xsections = inp.xsections.loc[~inp.xsections.index.isin(invalid_links)]
#
#     # drop invalid subcats and their related components
#     invalid_subcats = inp.subcatchments.index[~inp.subcatchments['Outlet'].isin(nids)]
#     inp.subcatchments = inp.subcatchments.loc[~inp.subcatchments.index.isin(invalid_subcats)]
#     inp.subareas = inp.subareas.loc[~inp.subareas.index.isin(invalid_subcats)]
#     inp.infiltration= inp.infiltration.loc[~inp.infiltration.index.isin(invalid_subcats)]
#
#     return invalid_links + invalid_subcats


def rotate_model(m, rads=0.5, origin=None):
    """
    rotate a model (its coordinates)
    >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY_B
    >>> import swmmio
    >>> mb = swmmio.Model(MODEL_FULL_FEATURES_XY_B)
    >>> mc = rotate_model(mb, rads=0.75, origin=(2748515.571, 1117763.466))
    >>> mc.inp.coordinates
    """
    from swmmio.graphics.utils import rotate_coord_about_point

    origin = (0, 0) if not origin else origin
    rotate_lambda = lambda xy: rotate_coord_about_point(xy, rads, origin)
    coord = m.inp.coordinates.apply(rotate_lambda, axis=1)
    verts = m.inp.vertices.apply(rotate_lambda, axis=1)
    pgons = m.inp.polygons.apply(rotate_lambda, axis=1)

    # retain column names / convert to df
    m.inp.coordinates = pd.DataFrame(data=coord.to_list(),
                                     columns=m.inp.coordinates.columns,
                                     index=m.inp.coordinates.index)
    m.inp.vertices = pd.DataFrame(data=verts.to_list(),
                                  columns=m.inp.vertices.columns,
                                  index=m.inp.vertices.index)
    m.inp.polygons = pd.DataFrame(data=pgons.to_list(),
                                  columns=m.inp.polygons.columns,
                                  index=m.inp.polygons.index)

    return m


def remove_braces(string):
    return string.replace('[', '').replace(']', '')


def format_inp_section_header(string):
    """
    Ensure a string is in the inp section header format: [UPPERCASE],
    except in the case of the [Polygons] section with is capitalized case
    :param string:
    :return: string
    """
    s = string.strip().upper()
    if s[0] != '[':
        s = f'[{s}'
    if s[-1] != ']':
        s = f'{s}]'

    return s


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
    trace up and down a SWMM model given a start node and optionally a
    stop node.
    """

    traced_nodes = [startnode]  # include the starting node
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

    # kickoff the trace
    print("Starting trace {} from {}".format(mode, startnode))
    trace(startnode)
    print("Traced {0} nodes from {1}".format(len(traced_nodes), startnode))
    return {'nodes': traced_nodes, 'conduits': traced_conduits}


