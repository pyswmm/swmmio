import unittest
import tempfile
import os

from swmmio.examples import philly


class TestSpatialFunctions(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.gettempdir()

    def test_write_shapefile(self):
        with tempfile.TemporaryDirectory() as tmp_dir:

            philly.export_to_shapefile(tmp_dir)
            nodes_path = os.path.join(tmp_dir, f'{philly.name}_nodes.shp')
            links_path = os.path.join(tmp_dir, f'{philly.name}_conduits.shp')

            self.assertTrue(os.path.exists(nodes_path))
            self.assertTrue(os.path.exists(links_path))
