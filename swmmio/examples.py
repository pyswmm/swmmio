from swmmio import Model
from swmmio.tests.data import (MODEL_A_PATH, MODEL_EX_1, MODEL_FULL_FEATURES_XY,
                               MODEL_FULL_FEATURES__NET_PATH, MODEL_FULL_FEATURES_XY_B,
                               MODEL_GREEN_AMPT, MODEL_TEST_INLET_DRAINS, MODEL_GROUNDWATER)

# example models
philly = Model(MODEL_A_PATH, crs="+init=EPSG:2817")
jersey = Model(MODEL_FULL_FEATURES_XY)
jerzey = Model(MODEL_FULL_FEATURES_XY_B)
spruce = Model(MODEL_FULL_FEATURES__NET_PATH)
walnut = Model(MODEL_EX_1)
green = Model(MODEL_GREEN_AMPT)
streets = Model(MODEL_TEST_INLET_DRAINS)
groundwater = Model(MODEL_GROUNDWATER)
