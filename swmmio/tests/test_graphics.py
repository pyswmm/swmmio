from swmmio.tests.data import (DATA_PATH, MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES__NET_PATH)
import swmmio
from swmmio.graphics import swmm_graphics as sg
import os


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
