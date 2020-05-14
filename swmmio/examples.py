from swmmio import Model
from swmmio.tests.data import MODEL_A_PATH
from swmmio.tests.data import MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES__NET_PATH

# example models
philly = Model(MODEL_A_PATH, crs="+init=EPSG:2817")
jersey = Model(MODEL_FULL_FEATURES_XY)
spruce = Model(MODEL_FULL_FEATURES__NET_PATH)
