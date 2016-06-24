import pandas as pd
import shutil
import os
import fileinput
from swmmio.swmmio import Model
from swmmio.utils import functions as funcs
from swmmio.utils.dataframes import create_dataframeINP
from swmmio.utils import swmm_utils as su
#from .utils.text import * #functions for processing inp/rpt/txt files

pd.options.display.max_colwidth = 200


def create_branch(basemodel, branch_name, newdir=None):

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

def combine_models(basemodel, newdir, models):

    #create new branch model based on basemodel
    newname = '_'.join([x.inp.name for x in models])# + "_" + funcs.random_alphanumeric(3)
    new_branch = create_branch(basemodel, branch_name = newname, newdir=newdir)
    print 'Building new model by combining models: {}'.format(', '.join([x.inp.name for x in models]))
    #ignore certain problematic sections and simply copy it from the basemodel
    blindcopies = ['[CURVES]', '[TIMESERIES]', '[RDII]', '[HYDROGRAPHS]']

    with open (new_branch.inp.filePath, 'w') as f:

        #create the MS Excel writer object
        xlpath = os.path.join(new_branch.inp.dir,newname + '.xlsx')
        excelwriter = pd.ExcelWriter(xlpath)

        #compute the changes for each model from the basemodel
        sections = funcs.complete_inp_headers(basemodel.inp.filePath)
        for section in sections['order']:
            #print 'working on {}'.format(section)

            if section not in blindcopies:
                #if this section is not problematic, process as expected
                changes = [Change(basemodel, m, section) for m in models]
                new_section = apply_changes(basemodel, changes, section=section)
            else:
                #blindly copy this section from the base model
                new_section = create_dataframeINP(basemodel.inp, section=section)

            add_str =  ''

            f.write('\n\n' + section + '\n') #add SWMM-friendly header e.g. [DWF]

            if sections['headers'][section] == 'blob' and not new_section.empty:
                #to left justify based on the longest string in the blob column
                formatter = '{{:<{}s}}'.format(new_section[section].str.len().max()).format
                add_str = new_section.fillna('').to_string(
                                                            index_names=False,
                                                            header=False,
                                                            index=False,
                                                            justify='left',
                                                            formatters={section:formatter}
                                                            )
                #write section to excel sheet
                sheetname = section.replace('[', "").replace(']', "")
                new_section.to_excel(excelwriter, sheetname, index=False)

            elif not new_section.empty:
                #naming the columns to the index name so the it prints in-line with col headers

                #new_section.columns.name = ";" + new_section.index.name
                f.write(';')
                #f.seek(-1, 1)
                #to left justify on longest string in the Comment column
                #this is overly annoying, to deal with 'Objects' vs numbers to removed
                #one byte added from the semicolon (to keep things lined up)
                objectformatter =   {hedr:'{{:<{}}}'.format(new_section[hedr].apply(str).str.len().max()).format
                                        for hedr in new_section.columns}
                numformatter =      {hedr:' {{:<{}}}'.format(new_section[hedr].apply(str).str.len().max()).format
                                        for hedr in new_section.columns if new_section[hedr].dtype!="O"}
                objectformatter.update(numformatter)
                add_str = new_section.fillna('').to_string(
                                                            index_names=False,
                                                            header=True,
                                                            justify='left',
                                                            formatters=objectformatter#{'Comment':formatter}
                                                            )

                #write section to excel sheet
                sheetname = section.replace('[', "").replace(']', "")
                new_section.to_excel(excelwriter, sheetname)

            #f.write(';;' + sections['headers'][section] + '\n')
            #write the dataframe as a string
            f.write(add_str)

        excelwriter.save()


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
