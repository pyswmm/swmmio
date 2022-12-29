import os
import tempfile
from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from swmmio.tests.data import (DATA_PATH, MODEL_FULL_FEATURES_XY,
                               MODEL_FULL_FEATURES__NET_PATH, MODEL_A_PATH,
                               MODEL_EX_1_PARALLEL_LOOP)
import swmmio
from swmmio.graphics import swmm_graphics as sg
from swmmio.utils.spatial import centroid_and_bbox_from_coords, change_crs
from swmmio import (find_network_trace, build_profile_plot,
                    add_hgl_plot, add_node_labels_plot, add_link_labels_plot)
import pyswmm


def test_draw_model():
    m = swmmio.Model(MODEL_FULL_FEATURES_XY)
    target_img_pth = os.path.join(DATA_PATH, 'test-draw-model.png')
    sg.draw_model(m, file_path=target_img_pth)

    assert os.path.exists(target_img_pth)
    os.remove(target_img_pth)


def test_draw_red_and_grey_nodes():
    m = swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)
    target_img_pth = os.path.join(DATA_PATH, 'test-draw-model.png')
    nodes = m.nodes.dataframe
    nodes['draw_color'] = '#787882'
    nodes.loc[['J1', 'J2', 'J3'], 'draw_color'] = '#ff0000'
    nodes['draw_size'] = nodes['InvertElev'] * 3

    sg.draw_model(conduits=m.conduits(), nodes=nodes, file_path=target_img_pth)
    assert os.path.exists(target_img_pth)
    os.remove(target_img_pth)


def test_web_map_01():
    m = swmmio.Model(MODEL_A_PATH, crs="EPSG:2817")
    with tempfile.TemporaryDirectory() as tempdir:
        fname = os.path.join(tempdir, 'test-map.html')
        sg.create_map(m, filename=fname)

        assert os.path.exists(fname)


def test_centroid_and_bbox_from_coords():
    m = swmmio.Model(MODEL_A_PATH, crs="EPSG:2817")
    m.to_crs("EPSG:4326")

    c, bbox = centroid_and_bbox_from_coords(m.nodes.dataframe['coords'])
    assert c == pytest.approx((-70.97068, 43.74695), rel=1e-3)
    assert bbox == pytest.approx((-70.97068, 43.74695, -70.97068, 43.74695), rel=1e-3)

    c, bbox = centroid_and_bbox_from_coords([(0, 0), (0, 10), (10, 10), (10, 0)])
    assert c == (5, 5)
    assert bbox == [0, 0, 10, 10]


def test_change_crs():
    m = swmmio.Model(MODEL_A_PATH, crs="EPSG:2817")
    v1 = m.inp.vertices
    v2 = change_crs(m.inp.vertices, m.crs, "WGS84")
    assert v1.shape == v2.shape
    s = """
    Name      X          Y
    J4-001.1 -70.959386  43.732851
    J4-001.1 -70.958415  43.732578
    J4-001.1 -70.959423  43.730452
    J2-095.1 -70.951378  43.767796
    """
    v2_test = pd.read_csv(StringIO(s), index_col=0, delim_whitespace=True, skiprows=[0])
    assert v2['X'].values == pytest.approx(v2_test['X'].values, rel=1e-3)
    assert v2['Y'].values == pytest.approx(v2_test['Y'].values, rel=1e-3)


profile_selection_assert = \
    {
        'nodes':
            [{'id_name': '9', 'rolling_x_pos': 0.0, 'invert_el': 1000.0},
             {'id_name': '10', 'rolling_x_pos': 400.0, 'invert_el': 995.0},
             {'id_name': '21', 'rolling_x_pos': 800.0, 'invert_el': 990.0},
             {'id_name': '24', 'rolling_x_pos': 1300.0, 'invert_el': 984.0},
             {'id_name': '17', 'rolling_x_pos': 1700.0, 'invert_el': 980.0},
             {'id_name': '18', 'rolling_x_pos': 2100.0, 'invert_el': 975.0}],
        'links':
            [{'id_name': '1', 'rolling_x_pos': 200.0, 'midpoint_bottom': 997.5},
             {'id_name': '6', 'rolling_x_pos': 600.0, 'midpoint_bottom': 993.0},
             {'id_name': 'LOOP', 'rolling_x_pos': 1050.0, 'midpoint_bottom': 987.0},
             {'id_name': '16', 'rolling_x_pos': 1500.0, 'midpoint_bottom': 982.0},
             {'id_name': '10', 'rolling_x_pos': 1900.0, 'midpoint_bottom': 977.5}],
        'path_selection':
            [('9', '10', '1'),
             ('10', '21', '6'),
             ('21', '24', 'LOOP'),
             ('24', '17', '16'),
             ('17', '18', '10')]
    }


def test_profile():
    with tempfile.TemporaryDirectory() as tempdir:
        # instantiate a swmmio model object, save copy in temp dir
        temp_model_path = os.path.join(tempdir, 'model.inp')
        temp_pdf_path = os.path.join(tempdir, 'test.pdf')
        mymodel = swmmio.Model(MODEL_EX_1_PARALLEL_LOOP)
        mymodel.inp.save(temp_model_path)

        with pyswmm.Simulation(temp_model_path) as sim:
            for step in sim:
                pass
        # instantiate a swmmio model object
        mymodel = swmmio.Model(temp_model_path)

        depths = mymodel.rpt.node_depth_summary.MaxNodeDepthReported

        fig = plt.figure(figsize=(11, 8))
        fig.suptitle("TEST")
        ax = fig.add_subplot(2, 1, 1)
        path_selection = find_network_trace(mymodel, '9', '18', include_links=["LOOP"])
        profile_config = build_profile_plot(ax, mymodel, path_selection)
        assert (profile_config == profile_selection_assert)
        add_hgl_plot(ax, profile_config, depth=depths, label="Max HGL")
        add_node_labels_plot(ax, mymodel, profile_config)
        add_link_labels_plot(ax, mymodel, profile_config)
        leg = ax.legend()
        ax.grid('xy')

        ax2 = fig.add_subplot(2, 1, 2)
        path_selection = find_network_trace(mymodel, '19', '18', include_nodes=['22'])
        profile_config = build_profile_plot(ax2, mymodel, path_selection)
        add_hgl_plot(ax2, profile_config, depth=depths, label="Max HGL")
        add_node_labels_plot(ax2, mymodel, profile_config)
        add_link_labels_plot(ax2, mymodel, profile_config)
        leg = ax2.legend()
        ax2.grid('xy')

        fig.tight_layout()
        plt.savefig(temp_pdf_path)
        plt.close()
        assert (os.path.exists(temp_pdf_path))
