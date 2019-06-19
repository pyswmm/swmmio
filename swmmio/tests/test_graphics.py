from swmmio.tests.data import (DATA_PATH, MODEL_FULL_FEATURES_XY)
import swmmio
from swmmio.graphics import swmm_graphics as sg
import os


def test_draw_model():
    m = swmmio.Model(MODEL_FULL_FEATURES_XY)
    target_img_pth = os.path.join(DATA_PATH, 'test-draw-model.png')
    sg.draw_model(m, file_path=target_img_pth)

    assert os.path.exists(target_img_pth)
    os.remove(target_img_pth)

