import os
import tempfile
from io import StringIO

import pandas as pd
import pytest

from swmmio.tests.data import (DATA_PATH, MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES__NET_PATH, MODEL_A_PATH)
import swmmio
from swmmio.graphics import swmm_graphics as sg
from swmmio.utils.spatial import centroid_and_bbox_from_coords, change_crs


def test_draw_model():
    m = swmmio.Model(MODEL_FULL_FEATURES_XY)
    target_img_pth = os.path.join(DATA_PATH, 'test-draw-model.png')
    sg.draw_model(m, file_path=target_img_pth)

    assert os.path.exists(target_img_pth)
    os.remove(target_img_pth)


def test_draw_red_and_grey_nodes():
    m = swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)
    target_img_pth = os.path.join(DATA_PATH, 'test-draw-model.png')
    nodes = m.nodes()
    nodes['draw_color'] = '#787882'
    nodes.loc[['J1', 'J2', 'J3'], 'draw_color'] = '#ff0000'
    nodes['draw_size'] = nodes['InvertElev'] * 3

    sg.draw_model(conduits=m.conduits(), nodes=nodes, file_path=target_img_pth)
    assert os.path.exists(target_img_pth)
    os.remove(target_img_pth)


def test_web_map_01():

    m = swmmio.Model(MODEL_A_PATH,  crs="EPSG:2817")
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
