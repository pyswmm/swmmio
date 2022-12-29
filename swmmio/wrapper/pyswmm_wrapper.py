# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2022 Bryant E. McDonnell
#
# Licensed under the terms of the BSD2 License
# See LICENSE.txt for details
# -----------------------------------------------------------------------------
"""
Function developed to execute a PySWMM Simulation on the command line. To run,
execute the following on the command line:

python --help # Produces a list of options

python <path>/pyswmm_wrapper.py <path>/*.inp <path>/*.rpt <path>/*.out # optional args
"""

import argparse
import pathlib
import pyswmm


def run_model():
    """Run Model."""
    # Argument Resolution
    parser = argparse.ArgumentParser()
    parser.add_argument('inp_file', type=pathlib.Path,
                        help='Input File Path')
    parser.add_argument('rpt_file', type=pathlib.Path, nargs='?',
                        help='Report File Path (Optional).')
    parser.add_argument('out_file', type=pathlib.Path, nargs='?',
                        help='Output File Path (Optional).')

    report_prog_help = "--report-progress can be useful for longer model runs. The drawback "\
                       +"is that it slows the simulation down.  Use an integer to specify how "\
                       +"frequent to interrup the simulation. This depends of the number of time "\
                       +"steps"
    parser.add_argument('--report_progress', default=False, type=int,
                        help=report_prog_help)
    args = parser.parse_args()

    # File Naming -> Str Paths
    inp_file = str(args.inp_file)
    if args.rpt_file:
        rpt_file = str(args.rpt_file)
    else:
        rpt_file = args.rpt_file
    out_file = str(args.out_file)
    if args.out_file:
        out_file = str(args.out_file)
    else:
        out_file = args.out_file

    # Running the simulation without and with progress reporting.
    if args.report_progress == False:
        sim = pyswmm.Simulation(inp_file, rpt_file, out_file)
        sim.execute()
    else:
        with pyswmm.Simulation(inp_file, rpt_file, out_file) as sim:
            for ind, step in enumerate(sim):
                if ind % args.report_progress == 0:
                    print(round(sim.percent_complete*1000)/10.0)

    return 0

if __name__ in "__main__":
    run_model()
