import unittest
import tempfile
import os

import swmmio
from swmmio.examples import philly
from swmmio.run_models.run import run_simple, run_hot_start_sequence


class TestRunModels(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_run_simple(self):
        with tempfile.TemporaryDirectory() as tmp_dir:

            # create copy of model in temp dir
            inp_path = os.path.join(tmp_dir, 'philly-example.inp')
            philly.inp.save(inp_path)

            # run the model
            return_code = run_simple(inp_path)
            self.assertEqual(return_code, 0)

            m = swmmio.Model(inp_path)
            self.assertTrue(m.rpt_is_valid())

    def test_run_hot_start_sequence(self):
        with tempfile.TemporaryDirectory() as tmp_dir:

            # create copy of model in temp dir
            inp_path = os.path.join(tmp_dir, 'philly-example.inp')
            philly.inp.save(inp_path)

            # run the model
            return_code = run_hot_start_sequence(inp_path)
            self.assertEqual(return_code, 0)

            m = swmmio.Model(inp_path)
            self.assertTrue(m.rpt_is_valid())


