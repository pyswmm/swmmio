import pandas as pd
import shutil
import os
import fileinput
import swmmio
import swmm_headers_extended as she
import swmm_utils as su

pd.options.display.max_colwidth = 100

def create_dataframe (inp, section='[CONDUITS]'):

    #create dict with headers and col names
    headers = she.complete_inp_headers(inp)['headers']

    with open(inp.filePath) as f:
        startfound = False
        endfound = False
        outFilePath = inp.dir + "\\" + inp.name + "_" + section + ".txt"
        with open(outFilePath, 'w') as newf:

            for line in f:

                if startfound and line.strip() in headers:
                    endfound = True
                    #print 'end found: {}'.format(line.strip())
                    break
                elif not startfound and section in line:
                    startfound = True
                    #replace line with usable headers
                    if headers[section] != 'blob':
                        line = headers[section] + '\n'

                if startfound:
                    newf.write(line)

    # if not endfound:
    #     #found no header section
    #     return None
    if headers[section] == 'blob':
        #return the whole row, without specifc col headers
        df = pd.read_table(outFilePath, delim_whitespace=False, comment=";")
    else:
        df = pd.read_table(outFilePath, header=0, delim_whitespace=True, comment=";", index_col=0)

    os.remove(outFilePath)
    #os.startfile(outFilePath)

    return df

def create_branch(basemodel, branch_name):

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
    # removedIDs = changes.removed
    # changedIDs = changes.changed
    # to_remove = removedIDs.index.union(changedIDs.index)
    # #to_remove
    # v1 = df_base.drop(to_remove)
    # newdf = pd.concat([v1, changes.added])
    new_branch = swmmio.Model(newdir)
    return new_branch

def combine_models(basemodel, *models):

    #create new branch model based on basemodel
    newname = '_'.join([x.inp.name for x in models]) + "_" + su.AlphaNum(3)
    new_branch = create_branch(basemodel, branch_name = newname)


    with open (new_branch.inp.filePath, 'w') as f:

        #compute the changes for each model from the basemodel
        sections = she.complete_inp_headers(basemodel.inp)
        for section in sections['order']:
            print 'working on {}'.format(section)
            changes = [Change(basemodel, m, section) for m in models]
            new_section = apply_changes(basemodel, changes, section=section)
            if sections['headers'][section] == 'blob':
                add_str = new_section.fillna('').to_string(index_names=False, header=False, index=False)
            else:
                add_str = new_section.fillna('').to_string(index_names=False, header=False)
            f.write('\n\n' + section + '\n')
            f.write(add_str)



def apply_changes(model, changes, section='[JUNCTIONS]'):

    df1 = create_dataframe(model.inp, section)
    rmvs = pd.concat([c.removed for c in changes] + [c.altered for c in changes])
    adds = pd.concat([c.added for c in changes] + [c.altered for c in changes])
    ids_to_remove = rmvs.index
    df2 = df1.drop(ids_to_remove)

    newdf = pd.concat([df2, adds])

    return newdf

class Change(object):

    def __init__(self, model1, model2, section='[JUNCTIONS]'):

        df1 = create_dataframe(model1.inp, section)
        df2 = create_dataframe(model2.inp, section)
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
        self.old = df1
        self.new = df2
        self.added = df2.ix[added_ids]
        self.removed = df1.ix[removed_ids]
        self.altered = df2.ix[changed_ids]
