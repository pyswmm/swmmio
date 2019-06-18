from swmmio.run_models import run
from swmmio import Model
from multiprocessing import Pool, cpu_count
from datetime import datetime
import os

wd = os.getcwd()
log_start_time = datetime.now().strftime("%y%m%d_%H%M")


def run_swmm_engine(inp_folder):

    logfile = os.path.join(wd, 'log_'+log_start_time+'.txt')

    m = Model(inp_folder)
    if not m.rpt_is_valid():
        # if the rpt is not valid i.e. not having current, usable data: run
        with open (logfile, 'a') as f:
            now = datetime.now().strftime("%y-%m-%d %H:%M")
            f.write('{}: started at {} '.format(m.inp.name, now))
            # print 'running {}\n'.format(m.inp.name)
            run.run_hot_start_sequence(m.inp.path)
            now = datetime.now().strftime("%y-%m-%d %H:%M")
            f.write(', completed at {}\n'.format(now))
    else:
        with open (logfile, 'a') as f:
            f.write('{}: skipped (up-to-date)\n'.format(m.inp.name))


def main(inp_paths, cores_left):

    """
    called from the cli:
    swmmio -sp DIR1, DIR2, ... -cores_left=4
    """

    # create multiprocessing Pool object using all cores less the -cores_left
    # beware of setting -cores_left=0, CPU usage will max the F out
    pool = Pool(cpu_count() - cores_left)

    # create a process pool with the run_swmm_engine() func on each directory
    res = pool.map(run_swmm_engine, inp_paths)

