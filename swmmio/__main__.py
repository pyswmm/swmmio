from .run_models.run import run_simple, run_hot_start_sequence
from .run_models import start_pool
from swmmio import Model
from itertools import chain
import os
import argparse
from multiprocessing import Pool, cpu_count
from datetime import datetime

#parse the arguments
parser = argparse.ArgumentParser(description='Process some stuff')
parser.add_argument('-r', '--run', dest='model_to_run')
parser.add_argument('-rhs', '--run_hotstart', dest='hotstart_model_to_run')
parser.add_argument('-sp', '--start_pool', dest='start_pool', nargs="+")
parser.add_argument('-cores_left', '--cores_left', dest='cores_left', default=4, type=int)

args = parser.parse_args()
wd = os.getcwd() #current directory script is being called from




if args.model_to_run is not None:
    print 'run the model: {}'.format(args.model_to_run)
    run_simple(args.model_to_run)

elif args.hotstart_model_to_run is not None:
    print 'hotstart_model_to_run the model: {}'.format(args.hotstart_model_to_run)
    m = Model(args.hotstart_model_to_run)
    run_hot_start_sequence(m)#args.hotstart_model_to_run)

elif args.start_pool is not None:

    models_dirs = [os.path.join(wd, f) for f in args.start_pool]
    print 'looking for models to queue in:\n\t{}'.format('\n\t'.join(models_dirs))
    #combine the segments and options (combinations) into one iterable
    # paths = (segments_dir, options_dir)
    # baseline = Model(baseline_dir)
    dirs_containing_inps = []
    for root, dirs, files in chain.from_iterable(os.walk(path) for path in models_dirs):
        for file in files:
            if file.endswith('.inp') and 'bk' not in root:
                #we've found a directory containing an inp
                print file
                dirs_containing_inps.append(root)


    start_pool.main(dirs_containing_inps, args.cores_left)
    # pool = Pool(cpu_count() - args.cores_left) # use all but 6 available cores
    # proces data_inputs iterable with pool
    # print pool
    # res = pool.map(run_swmm_engine, dirs_containing_inps)
    # map(run_swmm_engine, dirs_containing_inps[0:2])
    print "hi im done running"
    # baseline_dir = r'F:\models\SPhila\MasterModels_170104\Baseline' #r'P:\06_Tools\v_control\BIG\Baseline'
    # log_dir = r'F:\models\SPhila\MasterModels_170104\ProjectAdmin'
    # batch.batch_post_process(combi_folder, baseline_dir, log_dir, bbox=su.d68d70)


    print 'start_pool: {}\n{} cores left'.format(args.start_pool,
                                                 args.cores_left)


else:
    print 'you need to pass in some args'
