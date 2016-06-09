import pandas as pd
import shutil
import os
import swmmio
import swmm_headers_extended as she



def load_inp(model):
    with open (model.inp.filePath) as f:
        for line in f:
            if '[' and ']' in line:
                print line

def create_dataframe (inp, section='[CONDUITS]'):

    with open(inp.filePath) as f:
        startfound = False
        endfound = False
        outFilePath = inp.dir + "\\" + inp.name + "_" + section + ".txt"
        with open(outFilePath, 'w') as newf:

            for line in f:

                if startfound and line.strip() in she.inp_header_dict:
                    endfound = True
                    #print 'end found: {}'.format(line.strip())
                    break
                elif not startfound and section in line:
                    startfound = True
                    #replace line with usable headers
                    line = she.inp_header_dict[section] + '\n'

                if startfound:
                    newf.write(line)

    df = pd.read_table(outFilePath, header=0, delim_whitespace=True, comment=";", index_col=0)
    os.remove(outFilePath)
    #os.startfile(outFilePath)

    return df

def create_branch(basemodel, changes, branch_name):

    #takes a swmmio model object, create a new inp and commits changes
    #based on the given change object
    #returns a swmmio Model object

    #create new directory and copy base inp
    wd = basemodel.inp.dir
    safename = branch_name.replace(" ", '-')
    newdir = os.path.join(wd, safename)
    if not os.path.exists(newdir):
        os.makedirs(newdir)
    else:
        return "branch or directory already exists"

    shutil.copyfile(basemodel.inp.filePath, os.path.join(newdir, safename + '.inp'))

    #commit changes from change object to the basemodel
    #create DF of section
    #c = vc.Change(wec_01, wec_02)
    removedIDs = changes.removed
    changedIDs = changes.changed
    to_remove = removedIDs.index.union(changedIDs.index)
    #to_remove
    v1 = df_base.drop(to_remove)
    newdf = pd.concat([v1, changes.added]) 

    return swmmio.Model(newdir)

class Change(object):

    def __init__(self, model1, model2):

        df1 = create_dataframe(model1.inp, '[CONDUITS]')
        df2 = create_dataframe(model2.inp, '[CONDUITS]')
        added_ids = df2.index.difference(df1.index)
        removed_ids = df1.index.difference(df2.index)

        #find where elements were changed (but kept with same ID)
        common_ids = df1.index.difference(removed_ids) #original - removed = in common
        #both dfs concatenated, with matched indices for each element
        full_set = pd.concat([df1.ix[common_ids],df2.ix[common_ids]])
        #drop dupes on the set, all things that did not changed should have 1 row
        changes_with_dupes = full_set.drop_duplicates()
        #duplicate indicies are rows that have changes, isolate these
        changed_ids = changes_with_dupes.index.get_duplicates()

        #for

        self.added = df2.ix[added_ids]
        self.removed = df1.ix[removed_ids]
        self.changed = df2.ix[changed_ids]
