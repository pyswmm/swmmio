import pandas as pd
import shutil
import os
import fileinput
import itertools
from datetime import datetime
from swmmio.swmmio import Model
from swmmio.utils import functions as funcs
from swmmio.utils.dataframes import create_dataframeINP
# from swmmio.utils import swmm_utils as su
from swmmio.version_control import utils as vc_utils
from swmmio.version_control import inp

#from .utils.text import * #functions for processing inp/rpt/txt files

pd.options.display.max_colwidth = 200


def propagate_changes_from_baseline(baseline_dir, alternatives_dir, combi_dir,
                                    version_id='', comments=''):

    #stuff
    """
    if the baseline model has changes that need to be propogated to all models,
    iterate through each model and rebuild the INPs with the new baseline and
    existing build instructions. update the build instructions to reflect the
    revision date of the baseline.
    """
    version_id += '_' + datetime.now().strftime("%y%m%d%H%M%S")

    #collect the directories of all models
    model_dirs = []
    for alt in os.listdir(alternatives_dir):
        #print alt
        #iterate through each implementation level of each alternative
        for imp_level in os.listdir(os.path.join(alternatives_dir, alt)):
            #create or refresh the build instructions file for the alternatives
            model_dirs.append(os.path.join(alternatives_dir, alt, imp_level))

    model_dirs += [os.path.join(combi_dir, x) for x in os.listdir(combi_dir)]
    #print model_dirs
    baseline = Model(baseline_dir)
    baseinp = baseline.inp.path

    for model_dir in model_dirs:
        model = Model(model_dir)
        vc_directory = os.path.join(model_dir, 'vc')
        latest_bi = vc_utils.newest_file(vc_directory)

        #update build instructions metdata and build the new inp
        bi = inp.BuildInstructions(latest_bi)
        bi.metadata['Parent Models']['Baseline'] = {baseinp:vc_utils.modification_date(baseinp)}
        bi.metadata['Log'].update({version_id:comments})
        bi.save(vc_directory, version_id+'.txt')
        print 'rebuilding {} with changes to baseline'.format(model.name)
        bi.build(baseline_dir, model.inp.path) #overwrite old inp




def create_combinations(baseline_dir, alternatives_dir, combi_dir, version_id='',
                        comments=''):

    """
    given a set of main alternatives split into models varying levels of
    implementation, this function combines all implementation levels of all
    alternatives into all logical combinations.
    """

    basemodel = Model(baseline_dir)
    baseinp = basemodel.inp.path
    alt_directories = os.listdir(alternatives_dir) #list of dirs holding alt models
    implementation_levels = []
    newmodels = []
    version_id += '_' + datetime.now().strftime("%y%m%d%H%M%S")

    for alt in alt_directories:

        #iterate through each implementation level of each alternative
        for imp_level in os.listdir(os.path.join(alternatives_dir, alt)):

            implementation_levels.append(os.path.join(alt, imp_level))

            #create or refresh the build instructions file for the alternatives
            alt_imp_level_dir = os.path.join(alternatives_dir, alt, imp_level)
            alt_imp_inp = Model(alt_imp_level_dir).inp.path
            vc_directory = os.path.join(alt_imp_level_dir, 'vc')

            if not os.path.exists(vc_directory):
                print 'creating new build instructions for {}'.format(imp_level)
                inp.create_inp_build_instructions(baseinp, alt_imp_inp, vc_directory,
                                                  version_id, comments)

            else:
                #check if the alternative model was changed since last run of this tool
                #--> compare the modification date to the BI's modification date meta data
                latest_bi = vc_utils.newest_file(vc_directory)
                if not vc_utils.bi_is_current(latest_bi):
                    #revision date of the alt doesn't match the newest build
                    #instructions for this 'imp_level', so we should refresh it
                    print 'updating build instructions for {}'.format(imp_level)
                    inp.create_inp_build_instructions(baseinp, alt_imp_inp,
                                                      vc_directory, version_id,
                                                      comments)


    #creat directories for new model combinations
    for L in range(1, len(implementation_levels)+1):

        #break
        for subset in itertools.combinations(implementation_levels, L):
            #subset e.g. = 'A\A01'

            #newcombi = '_'.join(subset)
            newcombi = '_'.join([os.path.split(s)[1] for s in subset])
            new_combi_dir = os.path.join(combi_dir, newcombi)
            vc_directory = os.path.join(new_combi_dir, 'vc')

            #create a list of the parent directories, use that to prevent
            #two or more from same alternative
            alternative_dirs = [os.path.split(s)[0] for s in subset]

            if len(alternative_dirs) == len(set(alternative_dirs)) and len(subset) > 1:
                #confirming the list length is equal to the set length (hashable)
                #confirms that there are not duplicates in the items list
                parent_vc_dirs = [os.path.join(alternatives_dir, f, 'vc') for f in subset]
                latest_parent_bis = [vc_utils.newest_file(d) for d in parent_vc_dirs]
                build_instrcts = [inp.BuildInstructions(bi) for bi in latest_parent_bis]

                if not os.path.exists(new_combi_dir):#and newcombi not in flavors:
                    #check to make sure new model doesn't repeat two or more from
                    #a particular genre.
                    #print new_combi_dir

                    os.mkdir(new_combi_dir)
                    newinppath = os.path.join(new_combi_dir, newcombi + '.inp')

                    #collect build instructions from each alt's implementation
                    #level for this combination. Select those with the current
                    #version id, or the latest version.
                    print 'creating new child model: {}'.format(newcombi)
                    new_build_instructions = sum(build_instrcts)
                    new_build_instructions.save(vc_directory, version_id+'.txt')
                    new_build_instructions.build(baseline_dir, newinppath)

                else:
                    #check if the alternative model was changed since last run
                    #of this tool --> compare the modification date to the BI's
                    #modification date meta data
                    latest_bi = vc_utils.newest_file(os.path.join(new_combi_dir,'vc'))
                    if not vc_utils.bi_is_current(latest_bi):
                        #revision date of the alt doesn't match the newest build
                        #instructions for this 'imp_level', so we should refresh it
                        print 'updating child build instructions for {}'.format(newcombi)
                        newinppath = os.path.join(new_combi_dir, newcombi + '.inp')
                        new_build_instructions = sum(build_instrcts)
                        new_build_instructions.save(vc_directory, version_id+'.txt')
                        new_build_instructions.build(baseline_dir, newinppath)
