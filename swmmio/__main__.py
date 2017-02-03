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
parser.add_argument('-r', '--run', dest='model_to_run', nargs="+")
parser.add_argument('-rhs', '--run_hotstart', dest='hotstart_model_to_run', nargs="+")
parser.add_argument('-sp', '--start_pool', dest='start_pool', nargs="+")
parser.add_argument('-cores_left', '--cores_left', dest='cores_left', default=4, type=int)

args = parser.parse_args()
wd = os.getcwd() #current directory script is being called from

if args.model_to_run is not None:

    models_paths = [os.path.join(wd, f) for f in args.model_to_run]
    print 'Adding models to queue:\n\t{}'.format('\n\t'.join(models_paths))

    #run the models in series (one after the other)
    map(run_simple, models_paths)
    # run_simple(args.model_to_run)

elif args.hotstart_model_to_run is not None:
    models_paths = [os.path.join(wd, f) for f in args.hotstart_model_to_run]
    print 'hotstart_model_to_run the model: {}'.format(args.hotstart_model_to_run)
    # m = Model(args.hotstart_model_to_run)
    # run_hot_start_sequence(m)#args.hotstart_model_to_run)
    map(run_hot_start_sequence, models_paths)

elif args.start_pool is not None:

    models_dirs = [os.path.join(wd, f) for f in args.start_pool]
    print 'LOOKY looking for models to queue in:\n\t{}'.format('\n\t'.join(models_dirs))
    #combine the segments and options (combinations) into one iterable
    inp_paths = []
    for root, dirs, files in chain.from_iterable(os.walk(path) for path in models_dirs):
        for f in files:
            if f.endswith('.inp') and 'bk' not in root:
                #we've found a directory containing an inp
                print f
                inp_paths.append(os.path.join(root, f))


    #call the main() function in start_pool.py
    print inp_paths
    start_pool.main(inp_paths, args.cores_left)

    print "swmmio has completed running {} models".format(len(inp_paths))


else:
    print 'you need to pass in some args'
