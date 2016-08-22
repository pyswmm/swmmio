import pandas as pd
import shutil
import os
import fileinput
import itertools
from datetime import datetime
from swmmio.swmmio import Model
from swmmio.utils import functions as funcs
from swmmio.utils.dataframes import create_dataframeINP
from swmmio.utils import swmm_utils as su
from swmmio.version_control import utils as vc_utils
from swmmio.version_control import inp

#from .utils.text import * #functions for processing inp/rpt/txt files

pd.options.display.max_colwidth = 200


def copy_model(basemodel, branch_name, newdir=None):

    """
    takes a swmmio model object, create a new inp
    returns a swmmio Model object
    """

    #create new directory and copy base inp
    safename = branch_name.replace(" ", '-')
    if not newdir:
        wd = basemodel.inp.dir
        newdir = os.path.join(wd, safename)
        if not os.path.exists(newdir):
            os.makedirs(newdir)
        else:
            return "branch or directory already exists"

    shutil.copyfile(basemodel.inp.filePath, os.path.join(newdir, safename + '.inp'))
    new_branch = Model(newdir)

    return new_branch

def create_parent_build_instructions(baseline_dir, genres_dir):
    """
    create the build instructions files for each parent (genre) model such that
    they can be used quickly to create new models and model combinatins
    """
    base_inp = Model(baseline_dir).inp
    for root, dirs, files in os.walk(genres_dir):
        for file in files:
            if file.endswith('.inp') and 'bk' not in root:
                genre_inp = os.path.join(root, file)
                #create the build instructions file (and excel companion)
                inp.create_inp_build_instructions(base_inp.filePath, genre_inp)


def create_combinations(baseline_dir, alternatives_dir, combi_dir):

    """
    given a set of main alternatives split into models varying levels of
    implementation, this function combines all implementation levels of all
    alternatives into all logical combinations.
    """

    basemodel = Model(baseline_dir)
    baseinp = basemodel.inp.filePath
    alt_directories = os.listdir(alternatives_dir) #list of dirs holding alt models
    implementation_levels = []
    newmodels = []
    version_id = datetime.now().strftime("%y%m%d%H%M%S")

    for alt in alt_directories:

        #iterate through each implementation level of each alternative
        for imp_level in os.listdir(os.path.join(alternatives_dir, alt)):

            implementation_levels.append(os.path.join(alt, imp_level))

            #create or refresh the build instructions file for the alternatives
            alt_imp_level_dir = os.path.join(alternatives_dir, alt, imp_level)
            alt_imp_inp = Model(alt_imp_level_dir).inp.filePath
            vc_directory = os.path.join(alt_imp_level_dir, 'vc')

            if not os.path.exists(vc_directory):
                print 'creating new build instructions for {}'.format(imp_level)
                inp.create_inp_build_instructions(baseinp, alt_imp_inp, vc_directory, version_id)

            else:
                #check if the alternative model was changed since last run of this tool
                #--> compare the modification date to the BI's modification date meta data
                # alt_date_modified = vc_utils.modification_date(alt_imp_inp)
                # bi_date_modified = vc_utils.bi_latest_parent_date_modified(vc_directory, alt_imp_inp)
                # #print '{} -> {} || {}'.format(imp_level, alt_date_modified, bi_date_modified)
                # if alt_date_modified != bi_date_modified:
                latest_bi = vc_utils.newest_file(vc_directory)
                if not vc_utils.bi_is_current(latest_bi):
                    #revision date of the alt doesn't match the newest build
                    #instructions for this 'imp_level', so we should refresh it
                    print 'updating build instructions for {}'.format(imp_level)
                    inp.create_inp_build_instructions(baseinp, alt_imp_inp, vc_directory, version_id)





    #creat directories for new model combination
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
                #print new_combi_dir
                parent_vc_dirs = [os.path.join(alternatives_dir, f, 'vc') for f in subset]
                latest_parent_bis = [vc_utils.newest_file(d) for d in parent_vc_dirs]
                build_instrcts = [inp.BuildInstructions(bi) for bi in latest_parent_bis]

                if not os.path.exists(new_combi_dir):#and newcombi not in flavors:
                    #check to make sure new model doesn't repeat two or more from
                    #a particular genre.
                    #print new_combi_dir

                    os.mkdir(new_combi_dir)
                    newinppath = os.path.join(new_combi_dir, newcombi + '.inp')


                    #model_objects = [Model(os.path.join(genres_dir, f)) for f in subset]

                    #collect build instructions from each alt's implementation
                    #level for this combination. Select those with the current
                    #version id, or the latest version.
                    # vc_dirs = [os.path.join(alternatives_dir, f, 'vc') for f in subset]
                    # latest_bis = [vc_utils.newest_file(d) for d in vc_dirs]
                    # build_instrcts = [inp.BuildInstructions(bi) for bi in latest_bis]
                    # build_instrcts = [inp.BuildInstructions(os.path.join(alternatives_dir,
                    #                                                      f, 'vc',
                    #                                                      version_id + '.txt')
                    #                                         ) for f in subset]


                    new_build_instructions = sum(build_instrcts)
                    new_build_instructions.save(vc_directory, version_id+'.txt')
                    new_build_instructions.build(baseline_dir, newinppath)
                    # merge_models(basemodel, newdir=new_combi_dir, parent_models=model_objects)
                else:
                    #check if the alternative model was changed since last run of this tool
                    #--> compare the modification date to the BI's modification date meta data
                    latest_bi = vc_utils.newest_file(os.path.join(new_combi_dir,'vc'))
                    if not vc_utils.bi_is_current(latest_bi):
                        #revision date of the alt doesn't match the newest build
                        #instructions for this 'imp_level', so we should refresh it
                        print 'updating child build instructions for {}'.format(newcombi)
                        newinppath = os.path.join(new_combi_dir, newcombi + '.inp')
                        new_build_instructions = sum(build_instrcts)
                        new_build_instructions.save(vc_directory, version_id+'.txt')
                        new_build_instructions.build(baseline_dir, newinppath)
                    # for parent in latest_parent_bis:
                    #     #if any parent model revsion date does not match the revision
                    #     #date in the build instructions, it needs to be replaced
                    #
                    #     print '{} checking -> {}'.format(newcombi, parent[40:])
                    #     if not vc_utils.bi_is_current(parent):
                    #         print '{} not current'.format(parent)
                        # for k,revdate in vc_utils.read_meta_data(parent)['Parent Models'].iteritems():
                        #     print k, revdate
                        #parent_imp_level = os.path.split(subset)[1]
                        #parent_inp_date_modified =
                        #bi_date_modified = vc_utils.bi_latest_parent_date_modified(vc_directory,
                        #                                                           parent_imp_level)




def merge_models(basemodel, newdir, parent_models):

    """
    create new model based on a given basemodel and a list of parent models
    (models to inherit changes from with resprect to the base model).
    """

    newname = '_'.join([x.inp.name for x in parent_models])# + "_" + funcs.random_alphanumeric(3)
    print 'Building new model by combining models: {}'.format(', '.join([x.inp.name for x in parent_models]))

    #new_branch = copy_model(basemodel, branch_name = newname, newdir=newdir)
    newinpfile = os.path.join(newdir, newname +'.inp')

    #ignore certain sections in the INP files that are known
    #to be difficlt to parse and simply copy it from the basemodel
    problem_sections = ['[CURVES]', '[TIMESERIES]', '[RDII]', '[HYDROGRAPHS]']

    with open (newinpfile, 'w') as f:

        #create the MS Excel writer object
        xlpath = os.path.join(newdir, newname + '.xlsx')
        excelwriter = pd.ExcelWriter(xlpath)
        vc_utils.create_info_sheet(excelwriter, basemodel, parent_models)

        #compute the changes for each model from the basemodel
        allheaders = funcs.complete_inp_headers(basemodel.inp.filePath)
        for section in allheaders['order']:

            if section not in problem_sections:
                #check if a build instructions file exists, and use this
                #information if available to create the changes array
                changes = [inp.Change(basemodel, m, section) for m in parent_models]
                new_section = apply_changes(basemodel, changes, section=section)

            else:
                #blindly copy this section from the base model
                new_section = create_dataframeINP(basemodel.inp, section=section)

            #write the section into the inp file and the excel file
            vc_utils.write_inp_section(f, allheaders, section, new_section)
            vc_utils.write_excel_inp_section(excelwriter, allheaders, section, new_section)


        excelwriter.save()

    return Model(newinpfile)



def apply_changes(model, changes, section='[JUNCTIONS]'):

    df1 = create_dataframeINP(model.inp, section)
    #rmvs = pd.concat([c.removed for c in changes] + [c.altered for c in changes])

    #df of elements to be commented out in new inp,
    #(those altered [to be replaceed by new row] or those deleted)
    tobecommented = pd.concat([c.removed for c in changes])
    tobealtered = pd.concat([c.altered for c in changes])
    ids_to_remove_from_df1 = tobecommented.index | tobealtered.index #union of altered and removed indices
    tobecommented.index = ["; " + str(x) for x in tobecommented.index] #add comment character

    #add rows for new elements and altered element
    adds = pd.concat([c.added for c in changes] + [c.altered for c in changes])
    df2 = df1.drop(ids_to_remove_from_df1)

    newdf = pd.concat([df2, tobecommented, adds])

    return newdf
