import subprocess
import os
import pandas as pd
from swmmio.utils.modify_model import replace_inp_section
from swmmio.run_models import defs
from swmmio import Model
from swmmio.defs.config import SWMM_ENGINE_PATH


def run_simple(inp_path, swmm_eng=SWMM_ENGINE_PATH):
    """
    run a model once as is.
    """
    print('running {} with {}'.format(inp_path, swmm_eng))
    #inp_path = model.inp.path
    rpt_path = os.path.splitext(inp_path)[0] + '.rpt'

    subprocess.call([swmm_eng, inp_path, rpt_path])

def run_hot_start_sequence(inp_path, swmm_eng=SWMM_ENGINE_PATH):

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
    subprocess.call([swmm_eng, model.inp.path, rpt_path])

    # if os.path.exists(hotstart1) and not os.path.exists(hotstart2):
    #create new model inp with params to use hotstart1 and save hotstart2
    print('with params to use hotstart1 and save hotstart2')
    s = pd.Series(['USE HOTSTART "{}"'.format(hotstart1), 'SAVE HOTSTART "{}"'.format(hotstart2)])
    hot2_df = pd.DataFrame(s, columns=['[FILES]'])
    model = replace_inp_section(model.inp.path, '[FILES]', hot2_df)
    subprocess.call([swmm_eng, model.inp.path, rpt_path])

    # if os.path.exists(hotstart2):
    #create new model inp with params to use hotstart2 and not save anything
    print('params to use hotstart2 and not save anything')
    s = pd.Series(['USE HOTSTART "{}"'.format(hotstart2)])
    hot3_df = pd.DataFrame(s, columns=['[FILES]'])

    model = replace_inp_section(model.inp.path, '[FILES]', hot3_df)
    model = replace_inp_section(model.inp.path, '[REPORT]', defs.REPORT_none)# defs.REPORT_nodes_links)
    model = replace_inp_section(model.inp.path, '[OPTIONS]', defs.OPTIONS_normal)

    subprocess.call([swmm_eng, model.inp.path, rpt_path])
