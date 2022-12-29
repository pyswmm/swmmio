from swmmio import Model
from swmmio.tests.data import (MODEL_A_PATH, MODEL_EX_1, MODEL_FULL_FEATURES_XY,
                               MODEL_FULL_FEATURES__NET_PATH, MODEL_FULL_FEATURES_XY_B)

# example models
philly = Model(MODEL_A_PATH, crs="+init=EPSG:2817")
jersey = Model(MODEL_FULL_FEATURES_XY)
jerzey = Model(MODEL_FULL_FEATURES_XY_B)
spruce = Model(MODEL_FULL_FEATURES__NET_PATH)
walnut = Model(MODEL_EX_1)
