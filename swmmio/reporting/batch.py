from swmmio.swmmio import Model
from swmmio.reporting import reporting
from swmmio.utils import swmm_utils as su
from datetime import datetime
import os

REPORT_DIR_NAME = 'Report'

def batch_post_process(options_dir, baseline_dir, bbox=None, overwrite=False):
    """
    batch process all models in a given directory, where child directories
    each model (with .inp and .rpt companions). A bbox should be passed to
    control where the grahics are focused. Specify whether reporting content
    should be overwritten if found.
    """
    baseline = Model(baseline_dir)
    folders = os.listdir(options_dir)
    for folder in folders:
        #first check if there is already a Report directory and skip if required
        current_dir = os.path.join(options_dir, folder)
        report_dir = os.path.join(current_dir, REPORT_DIR_NAME)
        if not overwrite and os.path.exists(report_dir):
            print 'skipping {}'.format(folder)
            continue

        else:
            #generate the report
            current_model = Model(current_dir)
            print 'Generating report for {}'.format(current_model.inp.name)
            reporting.generate_figures(baseline, current_model, bbox=bbox, imgDir=report_dir, verbose=True)
