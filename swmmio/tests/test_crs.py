import pytest

from pyproj import CRS
from swmmio import Model
from swmmio.tests.data import (MODEL_FULL_FEATURES_PATH)

def test_crs_initialization_with_epsg():
    model = Model(MODEL_FULL_FEATURES_PATH, crs="EPSG:4326")
    assert isinstance(model.crs, CRS)
    assert model.crs.to_string() == "EPSG:4326"

def test_crs_initialization_with_none():
    model = Model(MODEL_FULL_FEATURES_PATH)
    assert model.crs is None

def test_crs_setter_with_epsg():
    model = Model(MODEL_FULL_FEATURES_PATH)
    model.crs = "EPSG:4326"
    assert isinstance(model.crs, CRS)
    assert model.crs.to_string() == "EPSG:4326"

def test_crs_setter_with_none():
    model = Model(MODEL_FULL_FEATURES_PATH, crs="EPSG:4326")
    model.crs = None
    assert model.crs is None
