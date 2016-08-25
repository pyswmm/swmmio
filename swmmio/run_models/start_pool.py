from swmmio.run_models import run
from swmmio.swmmio import Model
from swmmio.reporting import reporting
from swmmio.utils import swmm_utils as su
from swmmio.reporting import batch
from multiprocessing import Pool, cpu_count
from datetime import datetime
import os
import sys

#combi_folder = r'P:\06_Tools\v_control\vctest\Combinations'
#combi_folder = r'P:\06_Tools\v_control\Models\COMbis_sansC'
#combi_folder = r'P:\02_Projects\SouthPhila\SE_SFR\Models - ASE\ModelCombinations\Combinations'
#combi_folder =  r'P:\02_Projects\SouthPhila\SE_SFR\Models - ASE\ModelCombinations\Segments\M'
#logfile = r'P:\06_Tools\v_control\vctest\log.txt'
#logfile = r'P:\06_Tools\v_control\Models\log.txt'

#CREATE LOG FILE
now = datetime.now().strftime("%y%m%d_%H%M")
logfile = os.path.join(r'P:\06_Tools\v_control\Testing\cleaned\run', 'log_'+now+'.txt')
#logfile = r'P:\02_Projects\SouthPhila\SE_SFR\Models - ASE\ModelCombinations\log.txt'
#folders = os.listdir(combi_folder)

def run_swmm_engine(inp_folder):



    try:
        wd = os.path.join(combi_folder, inp_folder)
        m = Model(inp_folder)
    # run.run_simple(inp_folder)
        if not m.rpt:

            # print 'completed {} at {}'.format(m.inp.name, datetime.now())
            with open (logfile, 'a') as f:
                f.write('{} -- {} started... '.format(datetime.now().strftime("%y-%m-%d %H:%M"), m.inp.name))
                run.run_hot_start_sequence(m)
                f.write('completed at {}\n'.format(datetime.now().strftime("%y-%m-%d %H:%M")))


        else:
            # print '{} -- RPT already exist: {}'.format(datetime.now(), m.rpt.filePath)
            with open (logfile, 'a') as f:
                f.write('RPT already exist: {}\n'.format(m.rpt.filePath))


    except:

        with open (logfile, 'a') as f:
            f.write(' FAILED at  {}\n'.format(datetime.now().strftime("%y-%m-%d %H:%M")))

if __name__ == '__main__':

    for arg in sys.argv[1:]:
        print arg
    args = sys.argv[1:]
    if len(args) > 0:
        combi_folder = args[0]
        folders = os.listdir(combi_folder)
        dirs_containing_inps = []
        for root, dirs, files in os.walk(combi_folder):
            for file in files:
                if file.endswith('.inp') and 'bk' not in root:
                    #we've found a directory containing an inp
                    print file
                    dirs_containing_inps.append(root)
                    #dirs_containing_inps.append(os.path.join(root, file))


        pool = Pool(cpu_count() - 1) # use all but 1 available cores
        # proces data_inputs iterable with pool
        res = pool.map(run_swmm_engine, dirs_containing_inps)

        print "hi im done running"
        baseline_dir = r'P:\06_Tools\v_control\BIG\Baseline'
        log_dir = r'P:\06_Tools\v_control\Testing\cleaned\run'
        batch.batch_post_process(combi_folder, baseline_dir, log_dir, bbox=su.d68d70)
