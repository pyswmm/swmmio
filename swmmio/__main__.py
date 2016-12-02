from .run_models.run import run_simple, run_hot_start_sequence

import argparse

#parse the arguments
parser = argparse.ArgumentParser(description='Process some stuff')
parser.add_argument('-r', '--run', dest='model_to_run')
parser.add_argument('-rhs', '--run_hotstart', dest='hotstart_model_to_run')

args = parser.parse_args()

if args.model_to_run is not None:
    print 'run the model: {}'.format(args.model_to_run)
    run_simple(args.model_to_run)

elif args.hotstart_model_to_run is not None:
    print 'hotstart_model_to_run the model: {}'.format(args.hotstart_model_to_run)
    run_hot_start_sequence(args.hotstart_model_to_run)

else:
    print 'nah'
