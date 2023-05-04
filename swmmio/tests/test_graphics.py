import os
import tempfile
from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from collections.abc import Mapping
from _pytest.python_api import ApproxMapping

from swmmio.tests.data import (DATA_PATH, MODEL_FULL_FEATURES_XY,
                               MODEL_FULL_FEATURES__NET_PATH, MODEL_A_PATH,
                               MODEL_EX_1_PARALLEL_LOOP,
                               MODEL_EXAMPLE6, MODEL_EXTCNTRLMODEL)
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


##########################
# PROFILE TESTING ########
##########################

def my_approx(expected, rel=0.005, abs=0.005, nan_ok=False):
    if isinstance(expected, Mapping):
        return ApproxNestedMapping(expected, rel, abs, nan_ok)
    return pytest.approx(expected, rel, abs, nan_ok)


class ApproxNestedMapping(ApproxMapping):
    def _yield_comparisons(self, actual):
        for k in self.expected.keys():
            if isinstance(actual[k], type(self.expected)):
                gen = ApproxNestedMapping(
                    self.expected[k], rel=self.rel, abs=self.abs, nan_ok=self.nan_ok
                )._yield_comparisons(actual[k])
                for el in gen:
                    yield el
            else:
                yield actual[k], self.expected[k]

    def _check_type(self):
        for key, value in self.expected.items():
            if not isinstance(value, type(self.expected)):
                super()._check_type()


profile_normal_assert1 = \
    {
        'nodes':
            [{'id_name': '9', 'rolling_x_pos': 0.0, 'invert_el': 1000.0},
             {'id_name': '10', 'rolling_x_pos': 400.0, 'invert_el': 995.0},
             {'id_name': '21', 'rolling_x_pos': 800.0, 'invert_el': 990.0},
             {'id_name': '24', 'rolling_x_pos': 1300.0, 'invert_el': 984.0},
             {'id_name': '17', 'rolling_x_pos': 1700.0, 'invert_el': 980.0},
             {'id_name': '18', 'rolling_x_pos': 2100.0, 'invert_el': 975.0}],
        'links':
            [{'id_name': '1', 'rolling_x_pos': 200.0, 'midpoint_bottom': 997.5,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': '6', 'rolling_x_pos': 600.0, 'midpoint_bottom': 993.0,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'LOOP', 'rolling_x_pos': 1050.0, 'midpoint_bottom': 987.0,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': '16', 'rolling_x_pos': 1500.0, 'midpoint_bottom': 982.0,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': '10', 'rolling_x_pos': 1900.0, 'midpoint_bottom': 977.5,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []}],
        'path_selection':
            [('9', '10', '1'),
             ('10', '21', '6'),
             ('21', '24', 'LOOP'),
             ('24', '17', '16'),
             ('17', '18', '10')]
    }

profile_normal_assert2 = \
    {'nodes':
         [{'id_name': '19', 'rolling_x_pos': 0.0, 'invert_el': 1010.0},
          {'id_name': '20', 'rolling_x_pos': 200.0, 'invert_el': 1005.0},
          {'id_name': '21', 'rolling_x_pos': 400.0, 'invert_el': 990.0},
          {'id_name': '22', 'rolling_x_pos': 700.0, 'invert_el': 987.0},
          {'id_name': '16', 'rolling_x_pos': 1000.0, 'invert_el': 985.0},
          {'id_name': '24', 'rolling_x_pos': 1100.0, 'invert_el': 984.0},
          {'id_name': '17', 'rolling_x_pos': 1500.0, 'invert_el': 980.0},
          {'id_name': '18', 'rolling_x_pos': 1900.0, 'invert_el': 975.0}],
     'links':
         [{'id_name': '4', 'rolling_x_pos': 100.0, 'midpoint_bottom': 1007.5,
           'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
          {'id_name': '5', 'rolling_x_pos': 300.0, 'midpoint_bottom': 997.5,
           'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
          {'id_name': '7', 'rolling_x_pos': 550.0, 'midpoint_bottom': 989.5,
           'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
          {'id_name': '8', 'rolling_x_pos': 850.0, 'midpoint_bottom': 986.0,
           'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
          {'id_name': '15', 'rolling_x_pos': 1050.0, 'midpoint_bottom': 984.5,
           'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
          {'id_name': '16', 'rolling_x_pos': 1300.0, 'midpoint_bottom': 982.0,
           'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
          {'id_name': '10', 'rolling_x_pos': 1700.0, 'midpoint_bottom': 977.5,
           'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []}],
     'path_selection':
         [('19', '20', '4'),
          ('20', '21', '5'),
          ('21', '22', '7'),
          ('22', '16', '8'),
          ('16', '24', '15'),
          ('24', '17', '16'),
          ('17', '18', '10')]
     }


def test_profile_normal():
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
        assert (profile_config == profile_normal_assert1)
        add_hgl_plot(ax, profile_config, depth=depths, label="Max HGL")
        add_node_labels_plot(ax, mymodel, profile_config)
        add_link_labels_plot(ax, mymodel, profile_config)
        leg = ax.legend()
        ax.grid('xy')

        ax2 = fig.add_subplot(2, 1, 2)
        path_selection = find_network_trace(mymodel, '19', '18', include_nodes=['22'])
        profile_config = build_profile_plot(ax2, mymodel, path_selection)
        assert (profile_config == profile_normal_assert2)
        add_hgl_plot(ax2, profile_config, depth=depths, label="Max HGL")
        add_node_labels_plot(ax2, mymodel, profile_config)
        add_link_labels_plot(ax2, mymodel, profile_config)
        leg = ax2.legend()
        ax2.grid('xy')

        fig.tight_layout()
        plt.savefig(temp_pdf_path)
        plt.close()
        assert (os.path.exists(temp_pdf_path))


profile_weir_assert = \
    {
        'nodes':
            [{'id_name': 'Inlet', 'rolling_x_pos': 0.0, 'invert_el': 878.0},
             {'id_name': 'Outlet', 'rolling_x_pos': 50.0, 'invert_el': 868.0},
             {'id_name': 'TailWater', 'rolling_x_pos': 250.0, 'invert_el': 858.0}],
        'links':
            [{'id_name': 'Roadway', 'rolling_x_pos': 25.0, 'midpoint_bottom': 875.5,
              'link_type': 'WEIR', 'mid_x': [25.0, 25.0], 'mid_y': [883.0, 868.0]},
             {'id_name': 'Channel', 'rolling_x_pos': 150.0, 'midpoint_bottom': 863.0,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []}],
        'path_selection':
            [('Inlet', 'Outlet', 'Roadway'),
             ('Outlet', 'TailWater', 'Channel')]
    }


def test_profile_weir():
    with tempfile.TemporaryDirectory() as tempdir:
        # instantiate a swmmio model object, save copy in temp dir
        temp_model_path = os.path.join(tempdir, 'model.inp')
        temp_pdf_path = os.path.join(tempdir, 'test.pdf')
        mymodel = swmmio.Model(MODEL_EXAMPLE6)
        mymodel.inp.save(temp_model_path)

        with pyswmm.Simulation(temp_model_path) as sim:
            for step in sim:
                pass
        # instantiate a swmmio model object
        mymodel = swmmio.Model(temp_model_path)

        depths = mymodel.rpt.node_depth_summary.MaxNodeDepthReported
        fig = plt.figure(figsize=(11, 8))
        fig.suptitle("Weir")
        ax = fig.add_subplot(1, 1, 1)
        path_selection = find_network_trace(mymodel, 'Inlet', 'TailWater', include_links=["Roadway"])
        profile_config = build_profile_plot(ax, mymodel, path_selection)
        assert (profile_config == profile_weir_assert)
        add_hgl_plot(ax, profile_config, depth=depths, label="Max HGL")
        add_node_labels_plot(ax, mymodel, profile_config)
        add_link_labels_plot(ax, mymodel, profile_config)
        leg = ax.legend()
        ax.grid('xy')

        fig.tight_layout()
        plt.savefig(temp_pdf_path)
        plt.close()
        assert (os.path.exists(temp_pdf_path))


profile_orifice_assert = \
    {
        'nodes':
            [{'id_name': 'J28', 'rolling_x_pos': 0.0, 'invert_el': 39.0},
             {'id_name': 'J27', 'rolling_x_pos': 285.79, 'invert_el': 38.143},
             {'id_name': 'J26', 'rolling_x_pos': 739.29, 'invert_el': 36.783},
             {'id_name': 'J25', 'rolling_x_pos': 1137.17, 'invert_el': 35.588},
             {'id_name': 'J24', 'rolling_x_pos': 1476.62, 'invert_el': 34.57},
             {'id_name': 'J23', 'rolling_x_pos': 1833.5, 'invert_el': 33.499},
             {'id_name': 'J22', 'rolling_x_pos': 2202.31, 'invert_el': 32.392},
             {'id_name': 'J21', 'rolling_x_pos': 2511.89, 'invert_el': 31.464},
             {'id_name': 'J20', 'rolling_x_pos': 2854.1, 'invert_el': 30.436},
             {'id_name': 'J19', 'rolling_x_pos': 2999.48, 'invert_el': 30.0},
             {'id_name': 'SU2', 'rolling_x_pos': 3169.65, 'invert_el': 10.0},
             {'id_name': 'J1', 'rolling_x_pos': 3219.65, 'invert_el': 2.816},
             {'id_name': 'J2', 'rolling_x_pos': 3415.59, 'invert_el': 2.424},
             {'id_name': 'J3', 'rolling_x_pos': 3624.97, 'invert_el': 2.005},
             {'id_name': 'J4', 'rolling_x_pos': 3816.39, 'invert_el': 1.622},
             {'id_name': 'J5', 'rolling_x_pos': 3980.03, 'invert_el': 1.295},
             {'id_name': 'J6', 'rolling_x_pos': 4201.45, 'invert_el': 0.852},
             {'id_name': 'J7', 'rolling_x_pos': 4408.13, 'invert_el': 0.439},
             {'id_name': 'J8', 'rolling_x_pos': 4627.5, 'invert_el': 0.0}],
        'links':
            [{'id_name': 'C11', 'rolling_x_pos': 142.895, 'midpoint_bottom': 38.5715,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C12', 'rolling_x_pos': 512.54, 'midpoint_bottom': 37.463,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C13', 'rolling_x_pos': 938.23, 'midpoint_bottom': 36.1855,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C14', 'rolling_x_pos': 1306.895, 'midpoint_bottom': 35.079,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C15', 'rolling_x_pos': 1655.06, 'midpoint_bottom': 34.0345,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C16', 'rolling_x_pos': 2017.905, 'midpoint_bottom': 32.9455,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C17', 'rolling_x_pos': 2357.1, 'midpoint_bottom': 31.928,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C18', 'rolling_x_pos': 2682.995, 'midpoint_bottom': 30.95,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C19', 'rolling_x_pos': 2926.79, 'midpoint_bottom': 30.218,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C20', 'rolling_x_pos': 3084.565, 'midpoint_bottom': 26.0,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'OR3', 'rolling_x_pos': 3194.65, 'midpoint_bottom': 10.0,
              'link_type': 'ORIFICE', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C1', 'rolling_x_pos': 3317.62, 'midpoint_bottom': 2.62,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C2', 'rolling_x_pos': 3520.28, 'midpoint_bottom': 2.2145,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C3', 'rolling_x_pos': 3720.68, 'midpoint_bottom': 1.8135,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C4', 'rolling_x_pos': 3898.21, 'midpoint_bottom': 1.4585,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C5', 'rolling_x_pos': 4090.74, 'midpoint_bottom': 1.0735,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C6', 'rolling_x_pos': 4304.79, 'midpoint_bottom': 0.6455,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []},
             {'id_name': 'C7', 'rolling_x_pos': 4517.815, 'midpoint_bottom': 0.2195,
              'link_type': 'CONDUIT', 'mid_x': [], 'mid_y': []}],
        'path_selection':
            [('J28', 'J27', 'C11'),
             ('J27', 'J26', 'C12'),
             ('J26', 'J25', 'C13'),
             ('J25', 'J24', 'C14'),
             ('J24', 'J23', 'C15'),
             ('J23', 'J22', 'C16'),
             ('J22', 'J21', 'C17'),
             ('J21', 'J20', 'C18'),
             ('J20', 'J19', 'C19'),
             ('J19', 'SU2', 'C20'),
             ('SU2', 'J1', 'OR3'),
             ('J1', 'J2', 'C1'),
             ('J2', 'J3', 'C2'),
             ('J3', 'J4', 'C3'),
             ('J4', 'J5', 'C4'),
             ('J5', 'J6', 'C5'),
             ('J6', 'J7', 'C6'),
             ('J7', 'J8', 'C7')]
    }


def test_profile_orifice():
    with tempfile.TemporaryDirectory() as tempdir:
        # instantiate a swmmio model object, save copy in temp dir
        temp_model_path = os.path.join(tempdir, 'model.inp')
        temp_pdf_path = os.path.join(tempdir, 'test.pdf')
        mymodel = swmmio.Model(MODEL_EXTCNTRLMODEL)
        mymodel.inp.save(temp_model_path)

        with pyswmm.Simulation(temp_model_path) as sim:
            for step in sim:
                pass
        # instantiate a swmmio model object
        mymodel = swmmio.Model(temp_model_path)

        depths = mymodel.rpt.node_depth_summary.MaxNodeDepthReported
        fig = plt.figure(figsize=(11, 8))
        fig.suptitle("Orifice")
        ax = fig.add_subplot(1, 1, 1)
        path_selection = find_network_trace(mymodel, 'J28', 'J8')
        profile_config = build_profile_plot(ax, mymodel, path_selection)

        for ind, node in enumerate(profile_config['nodes']):
            test_node = profile_orifice_assert['nodes'][ind]
            assert (node == my_approx(test_node))
        for ind, link in enumerate(profile_config['links']):
            test_link = profile_orifice_assert['links'][ind]
            assert (link == my_approx(test_link))

        add_hgl_plot(ax, profile_config, depth=depths, label="Max HGL")
        add_node_labels_plot(ax, mymodel, profile_config)
        add_link_labels_plot(ax, mymodel, profile_config)
        leg = ax.legend()

        fig.tight_layout()
        plt.savefig(temp_pdf_path)
        plt.close()
        assert (os.path.exists(temp_pdf_path))
