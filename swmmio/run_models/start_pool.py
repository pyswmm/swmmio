from swmmio.run_models import run
from swmmio.swmmio import Model
from swmmio.reporting import reporting
from swmmio.utils import swmm_utils as su
from swmmio.reporting import batch
from multiprocessing import Pool, cpu_count
from datetime import datetime
import os
import sys
wd = os.getcwd()

log_start_time = datetime.now().strftime("%y%m%d_%H%M")
def run_swmm_engine(inp_folder):

    logfile = os.path.join(wd, 'log_'+log_start_time+'.txt')

    m = Model(inp_folder)
    print 'inp_folder = {}'.format(inp_folder)
    if not m.rpt:
        # print 'completed {} at {}'.format(m.inp.name, datetime.now())
        with open (logfile, 'a') as f:
            now = datetime.now().strftime("%y-%m-%d %H:%M")
            f.write('{} -- {} started... '.format(now, m.inp.name))
            print 'running {}\n'.format(m.inp.name)
            run.run_hot_start_sequence(m.inp.path)
            now = datetime.now().strftime("%y-%m-%d %H:%M")
            f.write('completed at {}\n'.format(now))
    else:
        with open (logfile, 'a') as f:
            f.write('RPT already exist: {}\n'.format(m.rpt.path))

def main(inp_paths, cores_left):

    """
    called from the cli:
    swmmio -sp DIR1, DIR2, ... -cores_left=4
    """

    # create multiprocessing Pool object using all cores less the -cores_left
    #beware of setting -cores_left=0, CPU usage will max the F out
    pool = Pool(cpu_count() - cores_left)

    #create a process pool with the run_swmm_engine() func on each directory
    res = pool.map(run_swmm_engine, inp_paths)


if __name__ == '__main__':
    """
    the old way
    """
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

        print 'dirs_containing_inps = {}'.format(dirs_containing_inps)

        pool = Pool(cpu_count() - 6) # use all but 6 available cores
        # proces data_inputs iterable with pool
        res = pool.map(run_swmm_engine, dirs_containing_inps)

        print "hi im done running"
        baseline_dir = r'F:\models\SPhila\MasterModels_170104\Baseline' #r'P:\06_Tools\v_control\BIG\Baseline'
        log_dir = r'F:\models\SPhila\MasterModels_170104\ProjectAdmin'
        # batch.batch_post_process(combi_folder, baseline_dir, log_dir, bbox=su.d68d70)
