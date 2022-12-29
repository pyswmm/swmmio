import argparse
import os
import tempfile
import unittest
from unittest import mock

import swmmio
from swmmio.examples import philly, jerzey
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

    @mock.patch('argparse.ArgumentParser.parse_args',
                return_value=argparse.Namespace(
                    model_to_run=[jerzey.inp.path]
                ))
    def test_swmmio_run(self, mock_args):
        from swmmio import __main__
        self.assertEqual(__main__.main(), 0)


