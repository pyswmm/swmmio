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

def create_combinations(baseline_dir, genres_dir, combi_dir):
    genres = os.listdir(genres_dir)
    flavors = []
    for gen in genres:
        for flav in os.listdir(os.path.join(genres_dir, gen)):
            #print os.path.join(gen, flav)
            flavors.append(os.path.join(gen, flav))

    newmodels = []
    basemodel = Model(baseline_dir)
    #creat directories for new model combinations
    for L in range(1, len(flavors)+1):
      for subset in itertools.combinations(flavors, L):


        #newcombi = '_'.join(subset)
        newcombi = '_'.join([os.path.split(s)[1] for s in subset])
        new_combi_dir = os.path.join(combi_dir, newcombi)

        #create a list of the parent directories, use that to prevent
        #two or more from same genre
        genredirs = [os.path.split(s)[0] for s in subset]
        if len(genredirs) == len(set(genredirs)) and len(subset) > 1:
                #confirming the list length is equal to the set length (hashable)
                #confirms that there are not duplicates in the items list

            if not os.path.exists(new_combi_dir):#and newcombi not in flavors:
                #check to make sure new model doesn't repeat two or more from
                #a particular genre.
                print new_combi_dir
                os.mkdir(new_combi_dir)
                newmodels.append(new_combi_dir)

                #create the new model
                model_objects = [Model(os.path.join(genres_dir, f)) for f in subset]
                create_model(basemodel, newdir=new_combi_dir, parent_models=model_objects)

def create_model(basemodel, newdir, parent_models=None, overwrite_sections=None):

    """
    create new model based on a given basemodel and optionally a list of
    parent models (models to inherit changes from with resprect to the base model).

    overwrite_sections is an option dictionary with keys matching seciton headers and
    values being a dataframe with data to be substituted into the new model. If the
    overwrite section is not found in the original model, it is inserted at the end.
    """

    if parent_models:
        newname = '_'.join([x.inp.name for x in parent_models])# + "_" + funcs.random_alphanumeric(3)
        print 'Building new model by combining models: {}'.format(', '.join([x.inp.name for x in parent_models]))
    else:
        newname = basemodel.inp.name
        parent_models = []
        print 'copying {}'.format(basemodel.inp.name)

    #new_branch = copy_model(basemodel, branch_name = newname, newdir=newdir)
    new_branch_temp = os.path.join(newdir, newname +'.tmp.inp')


    #ignore certain problematic sections and simply copy it from the basemodel
    blindcopies = ['[CURVES]', '[TIMESERIES]', '[RDII]', '[HYDROGRAPHS]']

    #with open (new_branch.inp.filePath, 'w') as f:
    with open (new_branch_temp, 'w') as f:

        #create the MS Excel writer object
        xlpath = os.path.join(newdir, newname + '.xlsx')
        excelwriter = pd.ExcelWriter(xlpath)

        #create an info sheet for the Excel file
        timeofcreation = datetime.now()
        s = pd.Series([datetime.now(), basemodel.inp.filePath] + [x.inp.filePath for x in parent_models] )
        s.index = ['DateCreated', 'Basemodel']+['ParentModel_' + str(i) for i,x in enumerate(parent_models)]
        df = pd.DataFrame(s, columns=['FileInfo'])
        df.to_excel(excelwriter, 'FileInfo')

        #compute the changes for each model from the basemodel
        sections = funcs.complete_inp_headers(basemodel.inp.filePath)
        for section in sections['order']:

            if parent_models and (section not in blindcopies):
                #if parent models were provided and this section
                #is not a known problematic section, process as normal
                changes = [Change(basemodel, m, section) for m in parent_models]
                new_section = apply_changes(basemodel, changes, section=section)

            elif overwrite_sections and section in overwrite_sections:
                #if we've passed in optional data to overwrite certain sections,
                #overwrite the current section if found in that dictionary
                new_section = overwrite_sections[section]

            else:
                #blindly copy this section from the base model
                new_section = create_dataframeINP(basemodel.inp, section=section)

            write_section(f, excelwriter, sections, section, new_section)


        if overwrite_sections:
            #check if we've passed in overwrite_sections that were not found in the
            #original file. if thats the case, append them to the end of the file
            for sect in [s for s in overwrite_sections if s not in sections['headers']]:
                write_section(f, excelwriter, sections, sect, overwrite_sections[sect])

        excelwriter.save()

    #delete old file and rename temp file
    os.remove(basemodel.inp.filePath)
    newfile = os.path.join(newdir, newname + '.inp')
    os.rename(new_branch_temp, newfile)

    return Model(newfile)

def write_section(file_object, excelwriter, sections, sectionheader, section_data):

    f = file_object
    add_str =  ''

    f.write('\n\n' + sectionheader + '\n') #add SWMM-friendly header e.g. [DWF]

    if sections['headers'].get(sectionheader, 'blob') == 'blob' and not section_data.empty:
        #to left justify based on the longest string in the blob column
        formatter = '{{:<{}s}}'.format(section_data[sectionheader].str.len().max()).format
        add_str = section_data.fillna('').to_string(
                                                    index_names=False,
                                                    header=False,
                                                    index=False,
                                                    justify='left',
                                                    formatters={sectionheader:formatter}
                                                    )
        #write section to excel sheet
        sheetname = sectionheader.replace('[', "").replace(']', "")
        section_data.to_excel(excelwriter, sheetname, index=False)

    elif not section_data.empty:
        #naming the columns to the index name so the it prints in-line with col headers
        f.write(';')
        #to left justify on longest string in the Comment column
        #this is overly annoying, to deal with 'Objects' vs numbers to removed
        #one byte added from the semicolon (to keep things lined up)
        objectformatter =   {hedr:'{{:<{}}}'.format(section_data[hedr].apply(str).str.len().max()).format
                                for hedr in section_data.columns}
        numformatter =      {hedr:' {{:<{}}}'.format(section_data[hedr].apply(str).str.len().max()).format
                                for hedr in section_data.columns if section_data[hedr].dtype!="O"}
        objectformatter.update(numformatter)
        add_str = section_data.fillna('').to_string(
                                                    index_names=False,
                                                    header=True,
                                                    justify='left',
                                                    formatters=objectformatter#{'Comment':formatter}
                                                    )

        #write section to excel sheet
        sheetname = sectionheader.replace('[', "").replace(']', "")
        section_data.to_excel(excelwriter, sheetname)


    #write the dataframe as a string
    f.write(add_str)

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

class Change(object):

    def __init__(self, model1, model2, section='[JUNCTIONS]'):

        df1 = create_dataframeINP(model1.inp, section)
        df2 = create_dataframeINP(model2.inp, section)
        added_ids = df2.index.difference(df1.index)
        removed_ids = df1.index.difference(df2.index)

        #find where elements were changed (but kept with same ID)
        common_ids = df1.index.difference(removed_ids) #original - removed = in common
        #both dfs concatenated, with matched indices for each element
        full_set = pd.concat([df1.ix[common_ids], df2.ix[common_ids]])
        #drop dupes on the set, all things that did not changed should have 1 row
        changes_with_dupes = full_set.drop_duplicates()
        #duplicate indicies are rows that have changes, isolate these
        changed_ids = changes_with_dupes.index.get_duplicates()

        added = df2.ix[added_ids]
        added['Comment'] = '; Added from model {}'.format(model2.inp.filePath)

        altered = df2.ix[changed_ids]
        altered['Comment'] = '; Altered in model {}'.format(model2.inp.filePath)

        removed = df1.ix[removed_ids]
        #comment out the removed elements
        #removed.index = ["; " + str(x) for x in removed.index]
        removed['Comment'] = '; Removed in model {}'.format(model2.inp.filePath)

        self.old = df1
        self.new = df2
        self.added = added
        self.removed = removed
        self.altered = altered
        #self.altered['Comments'] == 'Items changed from model {}'.format(model2.inp.filePath)
