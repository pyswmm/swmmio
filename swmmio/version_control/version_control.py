import pandas as pd
import os
import itertools
from datetime import datetime
from swmmio import Model
from swmmio.version_control import utils as vc_utils
from swmmio.version_control import inp

pd.options.display.max_colwidth = 200


def propagate_changes_from_baseline(baseline_dir, alternatives_dir, combi_dir,
                                    version_id='', comments=''):
    """
    if the baseline model has changes that need to be propagated to all models,
    iterate through each model and rebuild the INPs with the new baseline and
    existing build instructions. update the build instructions to reflect the
    revision date of the baseline.
    """
    version_id += '_' + datetime.now().strftime("%y%m%d%H%M%S")

    # collect the directories of all models
    model_dirs = []
    for alt in os.listdir(alternatives_dir):
        # print alt
        # iterate through each implementation level of each alternative
        for imp_level in os.listdir(os.path.join(alternatives_dir, alt)):
            # create or refresh the build instructions file for the alternatives
            model_dirs.append(os.path.join(alternatives_dir, alt, imp_level))

    model_dirs += [os.path.join(combi_dir, x) for x in os.listdir(combi_dir)]
    # print model_dirs
    baseline = Model(baseline_dir)
    base_inp_path = baseline.inp.path

    for model_dir in model_dirs:
        model = Model(model_dir)
        vc_directory = os.path.join(model_dir, 'vc')
        latest_bi = vc_utils.newest_file(vc_directory)

        # update build instructions metadata and build the new inp
        bi = inp.BuildInstructions(latest_bi)
        bi.metadata['Parent Models']['Baseline'] = {base_inp_path: vc_utils.modification_date(base_inp_path)}
        bi.metadata['Log'].update({version_id: comments})
        bi.save(vc_directory, version_id + '.txt')
        print('rebuilding {} with changes to baseline'.format(model.name))
        bi.build(baseline_dir, model.inp.path)  # overwrite old inp


def create_combinations(baseline_dir, rsn_dir, combi_dir, version_id='',
                        comments=''):
    """
    Generate SWMM5 models of each logical combination of all implementation
    phases (IP) across all relief sewer networks (RSN).

    Inputs:
        baseline_dir -> path to directory containing the baseline SWMM5 model
        rsn_dir ->      path to directory containing subdirectories for each RSN
                        containing directories for each IP within the network
        combi_dir ->    target directory in which child models will be created
        version_id ->   identifier for a given version (optional)
        comments ->     comments tracked within build instructions log for
                        each model scenario (optional)

    Calling create_combinations will update child models if parent models have
    been changed.

    """

    base_inp_path = Model(baseline_dir).inp.path
    version_id += '_' + datetime.now().strftime("%y%m%d%H%M%S")

    # create a list of directories pointing to each IP in each RSN
    RSN_dirs = [os.path.join(rsn_dir, rsn) for rsn in os.listdir(rsn_dir)]
    IP_dirs = [os.path.join(d, ip) for d in RSN_dirs for ip in os.listdir(d)]

    # list of lists of each IP within each RSN, including a 'None' phase.
    IPs = [[None] + os.listdir(d) for d in RSN_dirs]

    # identify all scenarios (cartesian product of sets of IPs between each RSN)
    # then isolate child scenarios with atleast 2 parents (sets with one parent
    # are already modeled as IPs within the RSNs)
    all_scenarios = [[_f for _f in s if _f] for s in itertools.product(*IPs)]
    child_scenarios = [s for s in all_scenarios if len(s) > 1]

    # notify user of what was initially found
    str_IPs = '\n'.join([', '.join([_f for _f in i if _f]) for i in IPs])
    print(('Found {} implementation phases among {} networks:\n{}\n'
           'This yields {} combined scenarios ({} total)'.format(len(IP_dirs),
                                                                 len(RSN_dirs), str_IPs, len(child_scenarios),
                                                                 len(all_scenarios) - 1)))

    # ==========================================================================
    # UPDATE/CREATE THE PARENT MODEL BUILD INSTRUCTIONS
    # ==========================================================================
    for ip_dir in IP_dirs:
        ip_model = Model(ip_dir)
        vc_dir = os.path.join(ip_dir, 'vc')

        if not os.path.exists(vc_dir):
            print('creating new build instructions for {}'.format(ip_model.name))
            inp.create_inp_build_instructions(base_inp_path, ip_model.inp.path,
                                              vc_dir,
                                              version_id, comments)
        else:
            # check if the alternative model was changed since last run of this tool
            # --> compare the modification date to the BI's modification date metadata
            latest_bi = vc_utils.newest_file(vc_dir)
            if not vc_utils.bi_is_current(latest_bi):
                # revision date of the alt doesn't match the newest build
                # instructions for this 'imp_level', so we should refresh it
                print('updating build instructions for {}'.format(ip_model.name))
                inp.create_inp_build_instructions(base_inp_path, ip_model.inp.path,
                                                  vc_dir, version_id,
                                                  comments)

    # ==========================================================================
    # UPDATE/CREATE THE CHILD MODELS AND CHILD BUILD INSTRUCTIONS
    # ==========================================================================
    for scen in child_scenarios:
        newcombi = '_'.join(sorted(scen))
        new_dir = os.path.join(combi_dir, newcombi)
        vc_dir = os.path.join(combi_dir, newcombi, 'vc')

        # parent model build instr files
        # BUG (this breaks with model IDs with more than 1 char)
        parent_vc_dirs = [os.path.join(rsn_dir, f[0], f, 'vc') for f in scen]
        latest_parent_bis = [vc_utils.newest_file(d) for d in parent_vc_dirs]
        build_instrcts = [inp.BuildInstructions(bi) for bi in latest_parent_bis]

        if not os.path.exists(new_dir):

            os.mkdir(new_dir)
            newinppath = os.path.join(new_dir, newcombi + '.inp')

            print('creating new child model: {}'.format(newcombi))
            new_build_instructions = sum(build_instrcts)
            new_build_instructions.save(vc_dir, version_id + '.txt')
            new_build_instructions.build(baseline_dir, newinppath)

        else:
            # check if the alternative model was changed since last run
            # of this tool --> compare the modification date to the BI's
            # modification date meta data
            latest_bi = vc_utils.newest_file(os.path.join(new_dir, 'vc'))
            if not vc_utils.bi_is_current(latest_bi):
                # revision date of the alt doesn't match the newest build
                # instructions for this 'imp_level', so we should refresh it
                print('updating child build instructions for {}'.format(newcombi))
                newinppath = os.path.join(new_dir, newcombi + '.inp')
                new_build_instructions = sum(build_instrcts)
                new_build_instructions.save(vc_dir, version_id + '.txt')
                new_build_instructions.build(baseline_dir, newinppath)
