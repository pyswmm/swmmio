import subprocess
import os

import pandas as pd

from swmmio import Model
from swmmio.defs.config import PYTHON_EXE_PATH, PYSWMM_WRAPPER_PATH


def run_simple(inp_path, py_path=PYTHON_EXE_PATH, pyswmm_wrapper=PYSWMM_WRAPPER_PATH):
    """
    run a model once as is.
    """
    print('running {}'.format(inp_path))
    # inp_path = model.inp.path
    rpt_path = os.path.splitext(inp_path)[0] + '.rpt'
    out_path = os.path.splitext(inp_path)[0] + '.out'

    # Pass Environment Info to Run
    env_definition = os.environ.copy()
    env_definition["PATH"] = "/usr/sbin:/sbin:" + env_definition["PATH"]

    subprocess.call([py_path, pyswmm_wrapper, inp_path, rpt_path, out_path],
                    env=env_definition)
    return 0


def run_hot_start_sequence(inp_path, py_path=PYTHON_EXE_PATH, pyswmm_wrapper=PYSWMM_WRAPPER_PATH):

    model = Model(inp_path)
    hotstart1 = os.path.join(model.inp.dir, model.inp.name + '_hot1.hsf')
    hotstart2 = os.path.join(model.inp.dir, model.inp.name + '_hot2.hsf')

    # create new model inp with params to save hotstart1
    print('create new model inp with params to save hotstart1')

    model.inp.report.loc[:, 'Status'] = 'NONE'
    model.inp.report.loc[['INPUT', 'CONTROLS'], 'Status'] = 'NO'
    model.inp.files = pd.DataFrame([f'SAVE HOTSTART "{hotstart1}"'], columns=['[FILES]'])
    model.inp.options.loc['IGNORE_RAINFALL', 'Value'] = 'YES'
    model.inp.save()

    run_simple(model.inp.path, py_path=py_path, pyswmm_wrapper=pyswmm_wrapper)

    # create new model inp with params to use hotstart1 and save hotstart2
    print('with params to use hotstart1 and save hotstart2')
    model.inp.files = pd.DataFrame([f'USE HOTSTART "{hotstart1}"', f'SAVE HOTSTART "{hotstart2}"'], columns=['[FILES]'])
    model.inp.save()

    run_simple(model.inp.path, py_path=py_path, pyswmm_wrapper=pyswmm_wrapper)

    # create new model inp with params to use hotstart2 and not save anything
    print('params to use hotstart2 and not save anything')

    model.inp.files = pd.DataFrame([f'USE HOTSTART "{hotstart2}"'], columns=['[FILES]'])
    model.inp.options.loc['IGNORE_RAINFALL', 'Value'] = 'NO'
    model.inp.save()

    return run_simple(model.inp.path, py_path=py_path, pyswmm_wrapper=pyswmm_wrapper)
