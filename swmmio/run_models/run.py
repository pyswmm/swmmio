import subprocess
import os
import pandas as pd
from swmmio.version_control import version_control as vc
from swmmio.utils import dataframes


#path to the SWMM5 Engine
SWMM_ENGINE_PATH = r'\\PWDHQR\Data\Planning & Research\Flood Risk Management\07_Software\swmm5_22.exe'

def run_models(models, swmm_eng=SWMM_ENGINE_PATH, overwrite=False):
    """
    run a list of swmm models by passing in a list of swmmio Model objects

    """

    log = ''
    for model in models:

        inp_path = model.inp.filePath
        rpt_path = os.path.splitext(inp_path)[0] + '.rpt'

        #run them
        print 'Running model {}'.format(model.inp.name)
        s = subprocess.call([swmm_eng, inp_path, rpt_path])
        log += str(s) + '\n'


    print log

def run_models_parallel(models, swmm_eng=SWMM_ENGINE_PATH, overwrite=False):
    """
    run a list of swmm models by passing in a list of swmmio Model objects

    """

    commands = ['"{}" "{}" "{}.rpt"'.format(swmm_eng, m.inp.filePath,
                                            os.path.splitext(m.inp.filePath)[0])
                                            for m in models]

    processes = [subprocess.Popen(cmd, shell=True) for cmd in commands]

def run_hot_start_sequence(model, swmm_eng=SWMM_ENGINE_PATH):

    inp_path = model.inp.filePath
    rpt_path = os.path.splitext(inp_path)[0] + '.rpt'
    hotstart1 = os.path.join(model.inp.dir, model.inp.name + '_hot1.hsf')
    hotstart2 = os.path.join(model.inp.dir, model.inp.name + '_hot2.hsf')

    #create new model inp with params to save hotstart1
    report = pd.Series(['INPUT NO','CONTROLS NO','SUBCATCHMENTS NONE','NODES NONE', 'LINKS NONE'])
    report_df = pd.DataFrame(report, columns=['[REPORT]'])

    options_df = dataframes.create_dataframeINP(model.inp, '[OPTIONS]')
    options_df.ix['IGNORE_RAINFALL'] = ''
    options_df.set_value('IGNORE_RAINFALL', 'Value', 'YES')

    s = pd.Series(['SAVE HOTSTART "{}"'.format(hotstart1)])
    hot1_df = pd.DataFrame(s, columns=['[FILES]'])

    model1 = vc.create_model(model, model.inp.dir, parent_models=None,
                            overwrite_sections={'[FILES]':hot1_df,
                                                '[REPORT]':report_df,
                                                '[OPTIONS]':options_df})

    subprocess.call([swmm_eng, model1.inp.filePath, rpt_path])

    #create new model inp with params to use hotstart1 and save hotstart2
    s = pd.Series(['USE HOTSTART "{}"'.format(hotstart1), 'SAVE HOTSTART "{}"'.format(hotstart2)])
    hot2_df = pd.DataFrame(s, columns=['[FILES]'])
    model2 = vc.create_model(model1, model.inp.dir, parent_models=None,
                            overwrite_sections={'[FILES]':hot2_df})

    subprocess.call([swmm_eng, model2.inp.filePath, rpt_path])

    #create new model inp with params to use hotstart1 and save hotstart2
    report = pd.Series(['INPUT NO','CONTROLS NO','SUBCATCHMENTS NONE','NODES ALL', 'LINKS ALL'])
    report_df = pd.DataFrame(report, columns=['[REPORT]'])
    options_df.set_value('IGNORE_RAINFALL', 'Value', 'NO')

    s = pd.Series(['USE HOTSTART "{}"'.format(hotstart2)])
    hot3_df = pd.DataFrame(s, columns=['[FILES]'])
    model3 = vc.create_model(model2, model2.inp.dir, parent_models=None,
                            overwrite_sections={'[FILES]':hot3_df,
                                                '[REPORT]':report_df,
                                                '[OPTIONS]':options_df})

    subprocess.call([swmm_eng, model3.inp.filePath, rpt_path])
