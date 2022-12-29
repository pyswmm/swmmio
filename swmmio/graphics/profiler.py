import numpy as np
import pandas as pd
from swmmio.utils import error

MH_WIDTH=10
DEFAULT_ORIFICE_LENGTH = 50
DEFAULT_PUMP_LENGTH = 50
DEFAULT_WEIR_LENGTH = 50
DEFAULT_OUTLET_LENGTH = 50

def build_profile_plot(ax, model, path_selection):
    """
    This function builds the static network information for the profile. The
    function accepts the swmmio model object and the network trace information
    returned from calling `swmmio.find_network_trace()` function. The function
    returns the relevant information adding data for HGL and labels.

    :param model: swmmio.Model() object
    :param path_selection: list of tuples [(<us_node>, <ds_node>, <link_name>),...]
    :return: profile configuration information used for additional functions.
    """
    nodes = model.nodes.dataframe
    links = model.links.dataframe

    profile_config = {"nodes":[],"links":[],
                      "path_selection":path_selection}
    ground_levels = {'x':[],'level':[]}
    rolling_x_pos = 0.0

    for ind, link_set in enumerate(path_selection):
        us_node, ds_node, link_id = link_set
        # Plot first Node
        if ind == 0:
            invert_el = float(nodes.loc[[us_node]].InvertElev)
            profile_config['nodes'].append({"id_name":us_node,\
                                            "rolling_x_pos":rolling_x_pos,\
                                            "invert_el":invert_el})
            ret=_add_node_plot(ax, rolling_x_pos, model, us_node, link_set)
            ground_levels['x'].extend(ret['x'])
            ground_levels['level'].extend(ret['level'])

        # Add next link length to offset
        old_rolling_x_pos = rolling_x_pos
        # check link type
        if links.loc[[link_id]].Type[0] == "CONDUIT":
            rolling_x_pos += float(links.loc[[link_id]].Length)
        elif links.loc[[link_id]].Type[0] == "WEIR":
            rolling_x_pos += DEFAULT_WEIR_LENGTH
        elif links.loc[[link_id]].Type[0] == "ORIFICE":
            rolling_x_pos += DEFAULT_ORIFICE_LENGTH
        elif links.loc[[link_id]].Type[0] == "PUMP":
            rolling_x_pos += DEFAULT_PUMP_LENGTH
        elif links.loc[[link_id]].Type[0] == "OUTLET":
            rolling_x_pos += DEFAULT_OUTLET_LENGTH
        # Plot DS node
        invert_el = float(nodes.loc[[ds_node]].InvertElev)
        profile_config['nodes'].append({"id_name":ds_node,\
                                        "rolling_x_pos":rolling_x_pos,\
                                        "invert_el":invert_el})
        # Check which plot to build
        ret=_add_node_plot(ax, rolling_x_pos, model, ds_node, link_set)
        ground_levels['x'].extend(ret['x'])
        ground_levels['level'].extend(ret['level'])

        ret=_add_link_plot(ax, old_rolling_x_pos, rolling_x_pos, model, link_set)
        link_mid_x, link_mid_y = sum(ret['x'])/2.0, sum(ret['bottom'])/2.0
        profile_config["links"].append({"id_name":link_id,
                                        "rolling_x_pos":link_mid_x,
                                        "midpoint_bottom": link_mid_y})

    _add_ground_plot(ax, ground_levels)

    return profile_config


def _add_node_plot(ax, x, model, node_name, link_set, surcharge_depth=0, width=MH_WIDTH,
                      gradient=True):
    """
    Adds a single manhole to the plot.  Called by `build_profile_plot()`.
    """
    us_node, ds_node, link_id = link_set

    nodes = model.nodes.dataframe
    links = model.links.dataframe

    invert_el = float(nodes.loc[[node_name]].InvertElev)
    # Node Type checker
    if hasattr(model.inp, "junctions"):
        if node_name in model.inp.junctions.index:
            depth = float(nodes.loc[[node_name]].MaxDepth)
    if hasattr(model.inp, "outfalls"):
        if node_name in model.inp.outfalls.index:
            depth = float(links.loc[[link_id]].Geom1)
    if hasattr(model.inp, "storage"):
        if node_name in model.inp.storage.index:
            depth = float(nodes.loc[[node_name]].MaxD)

    # Plotting Configuration
    ll_x, ll_y = x-width, invert_el
    lr_x, lr_y = x+width, invert_el
    ur_x, ur_y = x+width, invert_el + depth
    ul_x, ul_y = x-width, invert_el + depth

    ax.plot([ll_x, lr_x, ur_x, ul_x, ll_x],
            [ll_y, lr_y, ur_y, ul_y, ll_y], "-", color='black',lw=0.75)

    if gradient:
        ax.fill_between([ul_x, ul_x+0.1], [lr_y, lr_y], [ur_y, ur_y],
                        zorder=1, color="gray")
        ax.fill_between([ul_x+0.1, ul_x+0.2], [lr_y, lr_y], [ur_y, ur_y],
                        zorder=0, color="silver")
        ax.fill_between([ul_x+0.2, ul_x+0.3], [lr_y, lr_y], [ur_y, ur_y],
                        zorder=0, color="whitesmoke")
        ax.fill_between([ur_x-0.1, ur_x], [lr_y, lr_y], [ur_y, ur_y],
                        zorder=1, color="gray")
        ax.fill_between([ur_x-0.2, ur_x-0.1], [lr_y, lr_y], [ur_y, ur_y],
                        zorder=0, color="silver")
        ax.fill_between([ur_x-0.3, ur_x-0.2], [lr_y, lr_y], [ur_y, ur_y],
                        zorder=0, color="whitesmoke")
    return {'x': [ul_x, ur_x], 'level': [ul_y, ur_y]}


def _add_link_plot(ax, us_x_position, ds_x_position, model, link_set, width=0, gradient=True):
    """
    Adds a single conduit to the plot.  Called by `build_profile_plot()`.
    """
    us_node, ds_node, link_id = link_set

    nodes = model.nodes.dataframe
    links = model.links.dataframe

    us_node_el = float(nodes.loc[[us_node]].InvertElev)
    ds_node_el = float(nodes.loc[[ds_node]].InvertElev)

    link_type = links.loc[[link_id]].Type[0]
    mid_x = []
    mid_y = []
    # check link type
    if link_type == "CONDUIT":
        depth = float(links.loc[[link_id]].Geom1)
        us_link_offset = float(links.loc[[link_id]].InOffset)
        ds_link_offset = float(links.loc[[link_id]].OutOffset)
        #
        us_bot_x, us_bot_y = us_x_position+width, us_node_el + us_link_offset
        ds_bot_x, ds_bot_y = ds_x_position-width, ds_node_el + ds_link_offset
        ds_top_x, ds_top_y = ds_x_position-width, ds_node_el + ds_link_offset + depth
        us_top_x, us_top_y = us_x_position+width, us_node_el + us_link_offset + depth

        ax.plot([us_bot_x, ds_bot_x, ds_top_x, us_top_x, us_bot_x],
                [us_bot_y, ds_bot_y, ds_top_y, us_top_y, us_bot_y], "-k",
                lw=0.75, zorder=0)

    elif link_type == "ORIFICE":
        depth = float(links.loc[[link_id]].Geom1)
        us_link_offset = float(links.loc[[link_id]].CrestHeight)
        ds_node_el = float(nodes.loc[[us_node]].InvertElev) # Plot it flat
        ds_link_offset = float(links.loc[[link_id]].CrestHeight)

        us_bot_x, us_bot_y = us_x_position+width, us_node_el + us_link_offset
        ds_bot_x, ds_bot_y = ds_x_position-width, ds_node_el + ds_link_offset
        ds_top_x, ds_top_y = ds_x_position-width, ds_node_el + ds_link_offset + depth
        us_top_x, us_top_y = us_x_position+width, us_node_el + us_link_offset + depth

        ax.plot([us_bot_x, ds_bot_x, ds_top_x, us_top_x, us_bot_x],
                [us_bot_y, ds_bot_y, ds_top_y, us_top_y, us_bot_y], "-k",
                lw=0.75, zorder=0)
    elif link_type in ["PUMP", "OUTLET"]:
        depth = 1.0
        us_link_offset = 0.0
        ds_link_offset = 0.0

        us_bot_x, us_bot_y = us_x_position+width, us_node_el + us_link_offset
        ds_bot_x, ds_bot_y = ds_x_position-width, ds_node_el + ds_link_offset
        ds_top_x, ds_top_y = ds_x_position-width, ds_node_el + ds_link_offset + depth
        us_top_x, us_top_y = us_x_position+width, us_node_el + us_link_offset + depth

        ax.plot([us_bot_x, ds_bot_x, ds_top_x, us_top_x, us_bot_x],
                [us_bot_y, ds_bot_y, ds_top_y, us_top_y, us_bot_y], "-k",
                lw=0.75, zorder=0)

    elif link_type == "WEIR":
        depth = float(links.loc[[link_id]].Geom1)
        us_link_offset = float(links.loc[[link_id]].CrestHeight)
        ds_link_offset = 0.0

        us_bot_x, us_bot_y = us_x_position+width, us_node_el + us_link_offset
        ds_bot_x, ds_bot_y = ds_x_position-width, ds_node_el + ds_link_offset
        ds_top_x, ds_top_y = ds_x_position-width, ds_node_el + ds_link_offset + depth
        us_top_x, us_top_y = us_x_position+width, us_node_el + us_link_offset + depth
        md_bot_x1, md_bot_y1 = (us_bot_x + ds_bot_x)/2.0, us_bot_y
        md_bot_x2, md_bot_y2 = md_bot_x1, ds_bot_y

        ax.plot([us_bot_x, md_bot_x1, md_bot_x2, ds_bot_x],
                [us_bot_y, md_bot_y1, md_bot_y2, ds_bot_y], "-k",
                lw=0.75, zorder=0)

        mid_x = [md_bot_x1, md_bot_x2]
        mid_y = [md_bot_y1, md_bot_y2]



    return {'x':[us_bot_x, ds_bot_x], 'bottom':[us_bot_y, ds_bot_y],
            "link_type":link_type, 'mid_x':mid_x, 'mid_y':mid_y}

def _add_ground_plot(ax, ground_levels):
    """
    Adds the grond level to the profile plot. Called by `build_profile_plot()`.
    """
    ax.plot(ground_levels['x'], ground_levels['level'], '--', color='brown', lw=.5)

def add_hgl_plot(ax, profile_config, hgl=None, depth=None, color = 'b', label="HGL"):
    if isinstance(hgl, pd.core.series.Series) == True \
      or isinstance(hgl, dict) == True:
        hgl_calc = [hgl[val["id_name"]] for val in profile_config['nodes']]
    elif isinstance(depth, pd.core.series.Series) == True \
      or isinstance(depth, dict) == True:
        hgl_calc = [val["invert_el"]+float(depth[val["id_name"]]) for val in profile_config['nodes']]
    else:
        raise(error.InvalidDataTypes)

    x = [float(val["rolling_x_pos"]) for val in profile_config['nodes']]

    ax.plot(x, hgl_calc, '-', color=color, label=label)


def add_node_labels_plot(ax, model, profile_config, font_size=8,
                         label_offset=5, stagger=True):
    """
    This function adds the node labels to the plot axis handle.

    :param ax: matplotlib.plot.axis() Axis handle
    :param model: swmmio.Model object
    :param profile_config: dict dictionary returned from the `build_profile_plot()`.
    :param font_size: font size
    :param label_offset: int just provides some clean separation from the
    assets and the labels
    :param stagger: True/False staggers the labels to prevent them from stacking
    onto one another.
    """
    nodes = model.nodes.dataframe

    label_y_max = 0
    for val in profile_config['nodes']:
        name = val['id_name']
        invert_el = float(nodes.loc[[name]].InvertElev)
        # Node Type checker
        if hasattr(model.inp, "junctions"):
            if name in model.inp.junctions.index:
                depth = float(nodes.loc[[name]].MaxDepth)
        if hasattr(model.inp, "outfalls"):
            if name in model.inp.outfalls.index:
                depth = 0
        if hasattr(model.inp, "storage"):
            if name in model.inp.storage.index:
                depth = float(nodes.loc[[name]].MaxD)

        calc = invert_el+depth
        if calc > label_y_max:
            label_y_max = calc

    mx_y_annotation = 0
    for ind, val in enumerate(profile_config['nodes']):
        stagger_value = 0
        if stagger:
            if ind % 2 ==0:
                stagger_value = 4
        name = val['id_name']
        x_offset = val['rolling_x_pos']
        invert_el = float(nodes.loc[[name]].InvertElev)
        # Node Type checker
        if hasattr(model.inp, "junctions"):
            if name in model.inp.junctions.index:
                depth = float(nodes.loc[[name]].MaxDepth)
        if hasattr(model.inp, "outfalls"):
            if name in model.inp.outfalls.index:
                depth = 0
        if hasattr(model.inp, "storage"):
            if name in model.inp.storage.index:
                depth = float(nodes.loc[[name]].MaxD)
        pos_y = invert_el+depth
        label=ax.annotate(name, xy=(x_offset, pos_y),
            xytext=(x_offset, label_y_max+label_offset+stagger_value),
            arrowprops=dict(arrowstyle="->", alpha=0.5), va='top', ha='center',
                            alpha=0.75, fontsize=font_size)
        mx_y = label.xyann[1]
        if mx_y > mx_y_annotation:
            mx_y_annotation = mx_y

    ax.set_ylim([None, mx_y_annotation])


def add_link_labels_plot(ax, model, profile_config, font_size=8,
                         label_offset=9, stagger=True):
    """
    This function adds the link labels to the plot axis handle.

    :param ax: matplotlib.plot.axis() Axis handle
    :param model: swmmio.Model object
    :param profile_config: dict dictionary returned from the `build_profile_plot()`.
    :param font_size: font size
    :param label_offset: int just provides some clean separation from the
    assets and the labels
    :param stagger: True/False staggers the labels to prevent them from stacking
    onto one another.
    """
    label_y_min = 1e9
    for val in profile_config['links']:
        y_midpoint_bottom = val["midpoint_bottom"]
        if y_midpoint_bottom < label_y_min:
            label_y_min = y_midpoint_bottom

    min_y_annotation = 1e9
    for ind, val in enumerate(profile_config['links']):
        stagger_value = 0
        if stagger:
            if ind % 2 != 0:
                stagger_value = 4
        name = val['id_name']
        x_offset = val['rolling_x_pos']
        y_midpoint_bottom = val["midpoint_bottom"]

        label=ax.annotate(name, xy=(x_offset, y_midpoint_bottom),
            xytext=(x_offset, label_y_min-label_offset+stagger_value),
            arrowprops=dict(arrowstyle="->", alpha=0.5), va='bottom',
                            ha='center', alpha=0.75, fontsize=font_size)
        mx_y = label.xyann[1]
        if mx_y < min_y_annotation:
            min_y_annotation = mx_y

    ax.set_ylim([min_y_annotation, None])
