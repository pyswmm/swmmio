from swmmio.run_models import run
from swmmio.swmmio import Model
from swmmio.reporting import reporting
from swmmio.utils import swmm_utils as su
from multiprocessing import Pool
from datetime import datetime
import os

#combi_folder = r'P:\06_Tools\v_control\vctest\Combinations'
#combi_folder = r'P:\06_Tools\v_control\Models\COMbis_sansC'
combi_folder = r'P:\02_Projects\SouthPhila\SE_SFR\Models - ASE\ModelCombinations\Combinations'
baseline_model = Model(r'P:\02_Projects\SouthPhila\SE_SFR\Models - ASE\ModelCombinations\BaselineModel')
#baseline_model  = Model(r'P:\06_Tools\v_control\Models\Baseline')
#logfile = r'P:\06_Tools\v_control\vctest\log.txt'
#logfile = r'P:\06_Tools\v_control\Models\log.txt'
logfile = r'P:\02_Projects\SouthPhila\SE_SFR\Models - ASE\ModelCombinations\log.txt'
folders = os.listdir(combi_folder)

def run_swmm_engine(inp_folder):



    try:
        wd = os.path.join(combi_folder, inp_folder)
        m = Model(wd)
        if not m.rpt:

            # print 'completed {} at {}'.format(m.inp.name, datetime.now())
            with open (logfile, 'a') as f:
                f.write('{} -- {} started... '.format(datetime.now(), m.inp.name))
                run.run_hot_start_sequence(m)
                f.write('completed at {}\n'.format(datetime.now()))


        else:
            # print '{} -- RPT already exist: {}'.format(datetime.now(), m.rpt.filePath)
            with open (logfile, 'a') as f:
                f.write('RPT already exist: {}\n'.format(m.rpt.filePath))


    except:

        with open (logfile, 'a') as f:
            f.write(' FAILED at  {}\n'.format(datetime.now()))

if __name__ == '__main__':
    pool = Pool()              # process per core
    res = pool.map(run_swmm_engine, folders)  # proces data_inputs iterable with pool
