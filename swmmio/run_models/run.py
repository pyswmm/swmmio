import subprocess
import os
import pandas as pd
from swmmio.utils.modify_model import replace_inp_section
from swmmio.run_models import defs
from swmmio import Model
from swmmio.defs.config import PYTHON_EXE_PATH, PYSWMM_WRAPPER_PATH


def run_simple(inp_path, py_path=PYTHON_EXE_PATH, pyswmm_wrapper=PYSWMM_WRAPPER_PATH):
    """
    run a model once as is.
    """
    print('running {}'.format(inp_path))
    #inp_path = model.inp.path
    rpt_path = os.path.splitext(inp_path)[0] + '.rpt'
    out_path = os.path.splitext(inp_path)[0] + '.out'

    # Pass Environment Info to Run
    env_definition = os.environ.copy()
    env_definition["PATH"] = "/usr/sbin:/sbin:" + env_definition["PATH"]

    subprocess.call([py_path, pyswmm_wrapper, inp_path, rpt_path, out_path],
                    env=env_definition)
    return 0

def run_hot_start_sequence(inp_path, py_path=PYTHON_EXE_PATH):

    # inp_path = model.inp.path
    model = Model(inp_path)
    rpt_path = os.path.splitext(inp_path)[0] + '.rpt'
    hotstart1 = os.path.join(model.inp.dir, model.inp.name + '_hot1.hsf')
    hotstart2 = os.path.join(model.inp.dir, model.inp.name + '_hot2.hsf')

    # if not os.path.exists(hotstart1) and not os.path.exists(hotstart2):
    #create new model inp with params to save hotstart1
    print('create new model inp with params to save hotstart1')
    s = pd.Series(['SAVE HOTSTART "{}"'.format(hotstart1)])
    hot1_df = pd.DataFrame(s, columns=['[FILES]'])
    model = replace_inp_section(model.inp.path, '[FILES]', hot1_df)
    model = replace_inp_section(model.inp.path, '[REPORT]', defs.REPORT_none)
    model = replace_inp_section(model.inp.path, '[OPTIONS]', defs.OPTIONS_no_rain)
    run_simple(model.inp.path)

    # if os.path.exists(hotstart1) and not os.path.exists(hotstart2):
    #create new model inp with params to use hotstart1 and save hotstart2
    print('with params to use hotstart1 and save hotstart2')
    s = pd.Series(['USE HOTSTART "{}"'.format(hotstart1), 'SAVE HOTSTART "{}"'.format(hotstart2)])
    hot2_df = pd.DataFrame(s, columns=['[FILES]'])
    model = replace_inp_section(model.inp.path, '[FILES]', hot2_df)
    run_simple(model.inp.path)

    # if os.path.exists(hotstart2):
    #create new model inp with params to use hotstart2 and not save anything
    print('params to use hotstart2 and not save anything')
    s = pd.Series(['USE HOTSTART "{}"'.format(hotstart2)])
    hot3_df = pd.DataFrame(s, columns=['[FILES]'])

    model = replace_inp_section(model.inp.path, '[FILES]', hot3_df)
    model = replace_inp_section(model.inp.path, '[REPORT]', defs.REPORT_none)# defs.REPORT_nodes_links)
    model = replace_inp_section(model.inp.path, '[OPTIONS]', defs.OPTIONS_normal)

    run_simple(model.inp.path)
