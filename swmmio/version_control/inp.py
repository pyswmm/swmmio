from swmmio.utils import functions as funcs
from swmmio import swmmio
from swmmio.version_control import utils as vc_utils
from swmmio.utils.dataframes import create_dataframeINP, create_dataframeBI
from swmmio.utils import text
import pandas as pd
from datetime import datetime
import os
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
problem_sections = ['[CURVES]', '[TIMESERIES]', '[RDII]', '[HYDROGRAPHS]']


class BuildInstructions(object):
    """
    similar to the Change object, this object contains information used to
    generate an inp based on 'serialized' (though human readable, inp-esque)
    build instructions files. This object is meant to neatly encapsulate things.

    self.instructions attribute contains a dictionary with keys of the headers
    that have changes i.e. build instructions w.r.t baseline model
    """

    def __init__(self, build_instr_file=None):

        #create a change object for each section that is different from baseline
        self.instructions = {}
        self.metadata = {}
        if build_instr_file:
            #read the instructions and create a dictionary of Change objects
            allheaders = funcs.complete_inp_headers(build_instr_file)
            instructions = {}
            for section in allheaders['order']:
                change = Change(build_instr_file=build_instr_file, section=section)
                instructions.update({section:change})

            self.instructions = instructions

            #read the meta data
            self.metadata = vc_utils.read_meta_data(build_instr_file)

    def __add__(self, other):
        bi = BuildInstructions()
        for section, change_obj in self.instructions.iteritems():
            if section in other.instructions:
                new_change = change_obj + other.instructions[section]
                bi.instructions[section] = new_change
            else:
                #section doesn't exist in other, maintain current instructions
                bi.instructions[section] = change_obj

        for section, change_obj in other.instructions.iteritems():
            if section not in self.instructions:
                bi.instructions[section] = change_obj


        #combine the metadata
        bi.metadata = self.metadata
        bi.metadata['Parent Models'].update(other.metadata['Parent Models'])
        bi.metadata['Comments'] += ' | {}'.format(other.metadata['Comments'])

        return bi

    def __radd__(self, other):
        #this is so we can call sum() on a list of build_instructions
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def save(self, dir, filename):
        """
        save the current BuildInstructions instance to file (human readable)
        """
        if not os.path.exists(dir):
            os.makedirs(dir)
        filepath = os.path.join(dir, filename)
        with open (filepath, 'w') as f:
            vc_utils.write_meta_data(f, self.metadata)
            for section, change_obj in self.instructions.iteritems():
                section_df = pd.concat([change_obj.removed, change_obj.altered, change_obj.added])
                vc_utils.write_inp_section(f, allheaders=None, sectionheader=section,
                                           section_data=section_df, pad_top=False, na_fill='NaN')

    def build(self, baseline_dir, target_path):
        """
        build a complete INP file with the build instructions committed to a
        baseline model.
        """
        basemodel = swmmio.Model(baseline_dir)
        allheaders = funcs.complete_inp_headers(basemodel.inp.filePath)
        #new_inp = os.path.join(target_dir, 'model.inp')
        with open (target_path, 'w') as f:
            for section in allheaders['order']:

                #check if the section is not in problem_sections and there are changes
                #in self.instructions and commit changes to it from baseline accordingly
                if (section not in problem_sections
                    and allheaders['headers'][section] != 'blob'
                    and section in self.instructions):

                    #df of baseline model section
                    basedf = create_dataframeINP(basemodel.inp, section)

                    #grab the changes to
                    changes = self.instructions[section]

                    #remove elements that have alterations and or tagged for removal
                    remove_ids = changes.removed.index | changes.altered.index
                    new_section = basedf.drop(remove_ids)

                    #add elements
                    new_section = pd.concat([new_section, changes.altered, changes.added])
                else:
                    #section is not well understood or is problematic, just blindly copy
                    new_section = create_dataframeINP(basemodel.inp, section=section)

                #write the section
                vc_utils.write_inp_section(f, allheaders, section, new_section)

class Change(object):
    """
    This object represents the 'changes' of a given section of a INP file
    with respect to another INP. Three main dataframes are attributes:
        added   --> includes elements that are new in model2 (compare to model1)
        removed --> elements that do not exist in model2, that were found to model1
        altered --> elements whose attributes have changes from model1 to model2

    This object can be applied via the vc.apply_changes() method
    """
    def __init__(self, model1=None, model2=None, section='[JUNCTIONS]', build_instr_file=None):

        if model1 and model2:
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
            added['Comment'] = 'Added'# from model {}'.format(model2.inp.filePath)
            added['Origin'] = model2.inp.filePath

            altered = df2.ix[changed_ids]
            altered['Comment'] = 'Altered'# in model {}'.format(model2.inp.filePath)
            altered['Origin'] = model2.inp.filePath

            removed = df1.ix[removed_ids]
            #comment out the removed elements
            #removed.index = ["; " + str(x) for x in removed.index]
            removed['Comment'] = 'Removed'# in model {}'.format(model2.inp.filePath)
            removed['Origin'] = model2.inp.filePath

            self.old = df1
            self.new = df2
            self.added = added
            self.removed = removed
            self.altered = altered

        if build_instr_file:
            #if generating from a build instructions file, do this (more efficient)

            #extract the section from file as a string

            # s = text.extract_section_from_inp(build_instr_file, sectionheader=section,
            #                                     return_string=True, skipheaders=True,
            #                                     cleanheaders=False)
            #
            # #stringIO thing so pandas can deal
            # stringIO = StringIO(s)

            #populate the column names
            # allheaders = funcs.complete_inp_headers(build_instr_file)
            # names = allheaders['headers'][section].split() + [";", 'Comment', 'Origin']
            # if allheaders['headers'][section] == 'blob':
            #     df = pd.read_table(stringIO, delim_whitespace=False, comment=';')
            # else:
            #     df = pd.read_table(stringIO, names=names, delim_whitespace=True, index_col=0)
            df = create_dataframeBI(build_instr_file, section = section)

            self.added = df.loc[df['Comment'] == 'Added']
            self.removed = df.loc[df['Comment'] == 'Removed']
            self.altered = df.loc[df['Comment'] == 'Altered']

    def __add__(self, other):

        # this should be made more robust to catch conflicts
        change = Change()
        change.added = self.added.append(other.added)
        change.removed = self.removed.append(other.removed)
        change.altered = self.altered.append(other.altered)

        return change

def generate_inp_from_diffs(basemodel, inpdiffs, target_dir):
    """
    create a new inp with respect to a baseline inp and changes instructed
    with a list of inp diff files (build instructions). This saves having to
    recalculate the differences of each model from the baseline whenever we want
    to combine versions.
    """

    #step 1 --> combine the diff/build instructions
    allheaders = funcs.complete_inp_headers(basemodel.inp.filePath)
    combi_build_instr_file = os.path.join(target_dir, 'build_instructions.txt')
    newinp = os.path.join(target_dir, 'new.inp')
    with open (combi_build_instr_file, 'w') as f:
        for header in allheaders['order']:
            s = ''
            section_header_written = False
            for inp in inpdiffs:
                sect_s = None
                if not section_header_written:
                    sect_s = text.extract_section_from_inp(inp, header,
                                                           cleanheaders=False,
                                                           return_string=True,
                                                           skipheaders=False)
                    section_header_written = True

                else:
                    sect_s = text.extract_section_from_inp(inp, header,
                                                           cleanheaders=False,
                                                           return_string=True,
                                                           skipheaders=True)

                if sect_s:
                    #remove the extra space between data in the same table
                    #coming from diffrent models.
                    if sect_s[-2:] == '\n\n':
                        s += sect_s[:-1]
                    else:
                        s += sect_s

            f.write(s + '\n')

    #step 2 --> clean up the new combined diff instructions
    df_dict = clean_inp_diff_formatting(combi_build_instr_file) #makes more human readable

    #step 3 --> create a new inp based on the baseline, with the inp_diff
    #instructions applied
    with open (newinp, 'w') as f:
        for section in allheaders['order']:
            print section
            if section not in problem_sections and allheaders['headers'][section] != 'blob':
                #check if a changes from baseline spreadheet exists, and use this
                #information if available to create the changes array
                df = create_dataframeINP(basemodel.inp, section)
                df['Origin'] = '' #add the origin column if not there
                if section in df_dict:
                    df_change = df_dict[section]
                    ids_to_drop = df_change.loc[df_change['Comment'].isin(['Removed', 'Altered'])].index
                    df = df.drop(ids_to_drop)
                    df = df.append(df_change.loc[df_change['Comment'].isin(['Added', 'Altered'])])
                new_section = df
            else:
                #blindly copy this section from the base model
                new_section = create_dataframeINP(basemodel.inp, section=section)

            #write the section into the inp file and the excel file
            vc_utils.write_inp_section(f, allheaders, section, new_section)




def clean_inp_diff_formatting(inpdiff, overwrite=True):
    """
    takes a inp diff file and aligns the columns for friendlier reading.
    This FAILS on regular inp files, which is okay for now.
    """

    allheaders = funcs.complete_inp_headers(inpdiff)
    cleanedf = os.path.splitext(inpdiff)[0] + '_cleanessssd.txt'
    df_dict = {}
    with open (cleanedf, 'w') as f:
        for header in allheaders['order']:

            if allheaders['headers'][header] != 'blob':
                s = text.extract_section_from_inp(inpdiff, header, cleanheaders=True,
                                                  return_string=True, skipheaders=False, skiprows=1)
                sio = StringIO(s)
                df = pd.read_table(sio, delim_whitespace=True, index_col=0)
            else:
                s = text.extract_section_from_inp(inpdiff, header, cleanheaders=True,
                                                  return_string=True, skipheaders=False)
                sio = StringIO(s)
                df = pd.read_table(sio)
            df_dict.update({header:df})
            vc_utils.write_inp_section(f, allheaders, header, df, pad_top=False)

    #replace original
    if overwrite:
        os.remove(inpdiff)
        os.rename(cleanedf, inpdiff)
    return df_dict

def create_inp_build_instructions(inpA, inpB, path, filename):

    """
    pass in two inp file paths and produce a spreadsheet showing the differences
    found in each of the INP sections. These differences should then be used
    whenever we need to rebuild this model from the baseline reference model.
    """

    allsections_a = funcs.complete_inp_headers(inpA)
    modela = swmmio.Model(inpA)
    modelb = swmmio.Model(inpB)

    #create build insructions folder
    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path, filename) + '.txt'
    # xlpath = os.path.join(path, filename) + '.xlsx'
    # excelwriter = pd.ExcelWriter(xlpath)
    # vc_utils.create_change_info_sheet(excelwriter, modela, modelb)

    problem_sections = ['[TITLE]', '[CURVES]', '[TIMESERIES]', '[RDII]', '[HYDROGRAPHS]']
    with open (filepath, 'w') as newf:

        #write meta data
        metadata = {
            'Baseline Model':modela.inp.filePath,
            'ID':filename,
            'Parent Models':{inpB:vc_utils.modification_date(inpB)},
            'Comments':'cool comments in here'
            }
        #print metadata
        vc_utils.write_meta_data(newf, metadata)
        for section in allsections_a['order']:
            if section not in problem_sections:
                #calculate the changes in the current section
                changes = Change(modela, modelb, section)
                data = pd.concat([changes.removed, changes.added, changes.altered])
                #vc_utils.write_excel_inp_section(excelwriter, allsections_a, section, data)
                vc_utils.write_inp_section(newf, allsections_a, section, data, pad_top=False, na_fill='NaN') #na fill fixes SNOWPACK blanks spaces issue


    # excelwriter.save()
