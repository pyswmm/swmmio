from swmmio.utils import functions as funcs
from swmmio import swmmio
from swmmio.version_control import utils as vc_utils
from swmmio.utils.dataframes import create_dataframeINP
import pandas as pd
from datetime import datetime
import os

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
        added['Comment'] = 'Added from model {}'.format(model2.inp.filePath)

        altered = df2.ix[changed_ids]
        altered['Comment'] = 'Altered in model {}'.format(model2.inp.filePath)

        removed = df1.ix[removed_ids]
        #comment out the removed elements
        #removed.index = ["; " + str(x) for x in removed.index]
        removed['Comment'] = 'Removed in model {}'.format(model2.inp.filePath)

        self.old = df1
        self.new = df2
        self.added = added
        self.removed = removed
        self.altered = altered


def generate_inp_from_diffs(basemodel, inpdiffs):
    """
    create a new inp with respect to a baseline inp and changes instructed
    with a list of inp diff files (build instructions). This saves having to
    recalculate the differences of each model from the baseline whenever we want
    to combine versions.
    """

    #step 1 --> combine the diff/build instructions



def inp_diff(inpA, inpB):

    """
    pass in two inp file paths and produce a spreadsheet showing the differences
    found in each of the INP sections. These differences should then be used
    whenever we need to rebuild this model from the baseline reference model.
    """

    allsections_a = funcs.complete_inp_headers(inpA)
    modela = swmmio.Model(inpA)
    modelb = swmmio.Model(inpB)

    #create the MS Excel writer object and start with an info sheet
    xlpath = os.path.join(os.path.dirname(inpB), 'build_instructions' + '.xlsx')
    filepath = os.path.join(os.path.dirname(inpB), 'build_instructions.txt')
    excelwriter = pd.ExcelWriter(xlpath)
    vc_utils.create_change_info_sheet(excelwriter, modela, modelb)

    problem_sections = ['[CURVES]', '[TIMESERIES]', '[RDII]', '[HYDROGRAPHS]']
    with open (filepath, 'w') as newf:
        for section in allsections_a['order']:
            if section not in problem_sections:
                #calculate the changes in the current section
                changes = Change(modela, modelb, section)
                data = pd.concat([changes.removed, changes.added, changes.altered])
                vc_utils.write_excel_inp_section(excelwriter, allsections_a, section, data)
                vc_utils.write_inp_section(newf, allsections_a, section, data, pad_top=False)

    excelwriter.save()
