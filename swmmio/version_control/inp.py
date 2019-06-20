from collections import OrderedDict

from swmmio.utils import functions as funcs
from swmmio import swmmio, get_inp_sections_details
from swmmio.version_control import utils as vc_utils
from swmmio.utils.dataframes import create_dataframeINP, create_dataframeBI
from swmmio.utils import text
import pandas as pd
import os
from copy import deepcopy
pd.options.display.max_colwidth = 200

problem_sections = ['[CURVES]', '[TIMESERIES]', '[RDII]', '[HYDROGRAPHS]']


class BuildInstructions(object):
    """
    similar to the INPSectionDiff object, this object contains information used to
    generate an inp based on 'serialized' (though human readable, inp-esque)
    build instructions files. This object is meant to neatly encapsulate things.

    self.instructions attribute contains a dictionary with keys of the headers
    that have changes i.e. build instructions w.r.t baseline model
    """

    def __init__(self, build_instr_file=None):

        # create a change object for each section that is different from baseline
        self.instructions = {}
        self.metadata = {}
        if build_instr_file:
            # read the instructions and create a dictionary of Change objects
            allheaders = funcs.complete_inp_headers(build_instr_file)
            instructions = {}
            for section, _ in allheaders.items():
                change = INPSectionDiff(build_instr_file=build_instr_file, section=section)
                instructions.update({section: change})

            self.instructions = instructions

            # read the meta data
            self.metadata = vc_utils.read_meta_data(build_instr_file)

    def __add__(self, other):
        bi = BuildInstructions()
        for section, change_obj in self.instructions.items():
            if section in other.instructions:
                new_change = change_obj + other.instructions[section]
                bi.instructions[section] = new_change
            else:
                # section doesn't exist in other, maintain current instructions
                bi.instructions[section] = change_obj

        for section, change_obj in other.instructions.items():
            if section not in self.instructions:
                bi.instructions[section] = change_obj

        # combine the metadata
        # deepcopy so child structures aren't linked to original
        bi.metadata = deepcopy(self.metadata)
        otherbaseline = other.metadata['Parent Models']['Baseline']
        otheralternatives = other.metadata['Parent Models']['Alternatives']
        bi.metadata['Parent Models']['Baseline'].update(otherbaseline)
        bi.metadata['Parent Models']['Alternatives'].update(otheralternatives)
        bi.metadata['Log'].update(other.metadata['Log'])

        return bi

    def __radd__(self, other):
        # this is so we can call sum() on a list of build_instructions
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
        with open(filepath, 'w') as f:
            vc_utils.write_meta_data(f, self.metadata)
            for section, change_obj in self.instructions.items():
                section_df = pd.concat([change_obj.removed, change_obj.altered, change_obj.added])
                vc_utils.write_inp_section(f, allheaders=None, sectionheader=section,
                                           section_data=section_df, pad_top=False, na_fill='NaN')

    def build(self, baseline_dir, target_path):
        """
        build a complete INP file with the build instructions committed to a
        baseline model.
        """
        basemodel = swmmio.Model(baseline_dir)
        allheaders = funcs.complete_inp_headers(basemodel.inp.path)
        # new_inp = os.path.join(target_dir, 'model.inp')
        with open(target_path, 'w') as f:
            for section, _ in allheaders.items():

                # check if the section is not in problem_sections and there are changes
                # in self.instructions and commit changes to it from baseline accordingly
                if (section not in problem_sections
                        and allheaders[section]['columns'] != ['blob']
                        and section in self.instructions):

                    # df of baseline model section
                    basedf = create_dataframeINP(basemodel.inp.path, section)

                    # grab the changes to
                    changes = self.instructions[section]

                    # remove elements that have alterations and or tagged for removal
                    remove_ids = changes.removed.index | changes.altered.index
                    new_section = basedf.drop(remove_ids)

                    # add elements
                    new_section = pd.concat([new_section, changes.altered, changes.added])
                else:
                    # section is not well understood or is problematic, just blindly copy
                    new_section = create_dataframeINP(basemodel.inp.path, section=section)

                # write the section
                vc_utils.write_inp_section(f, allheaders, section, new_section)


class INPSectionDiff(object):
    """
    This object represents the 'changes' of a given section of a INP file
    with respect to another INP. Three main dataframes are attributes:
        added   --> includes elements that are new in model2 (compare to model1)
        removed --> elements that do not exist in model2, that were found to model1
        altered --> elements whose attributes have changes from model1 to model2


    """

    def __init__(self, model1=None, model2=None, section='[JUNCTIONS]', build_instr_file=None):
        self.model1 = model1 if model1 else ""
        self.model2 = model2 if model2 else ""

        if model1 and model2:
            df1 = create_dataframeINP(model1.inp.path, section)
            df2 = create_dataframeINP(model2.inp.path, section)
            m2_origin_string = os.path.basename(model2.inp.path).replace(' ', '-')

            # BUG -> this fails if a df1 or df2 is None i.e. if a section doesn't exist in one model
            added_ids = df2.index.difference(df1.index)
            removed_ids = df1.index.difference(df2.index)

            # find where elements were changed (but kept with same ID)
            common_ids = df1.index.difference(removed_ids)  # original - removed = in common
            # both dfs concatenated, with matched indices for each element
            full_set = pd.concat([df1.loc[common_ids], df2.loc[common_ids]])
            # remove whitespace
            full_set = full_set.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            # drop dupes on the set, all things that did not changed should have 1 row
            changes_with_dupes = full_set.drop_duplicates()
            # duplicate indicies are rows that have changes, isolate these
            # idx[idx.duplicated()].unique()
            changed_ids = changes_with_dupes.index[changes_with_dupes.index.duplicated()].unique()  # .get_duplicates()

            added = df2.loc[added_ids].copy()
            added['Comment'] = 'Added'  # from model {}'.format(model2.inp.path)
            added['Origin'] = m2_origin_string

            altered = df2.loc[changed_ids].copy()
            altered['Comment'] = 'Altered'  # in model {}'.format(model2.inp.path)
            altered['Origin'] = m2_origin_string

            removed = df1.loc[removed_ids].copy()
            # comment out the removed elements
            # removed.index = ["; " + str(x) for x in removed.index]
            removed['Comment'] = 'Removed'  # in model {}'.format(model2.inp.path)
            removed['Origin'] = m2_origin_string

            self.old = df1
            self.new = df2
            self.added = added
            self.removed = removed
            self.altered = altered

        if build_instr_file:
            # if generating from a build instructions file, do this (more efficient)
            df = create_dataframeBI(build_instr_file, section=section)

            self.added = df.loc[df['Comment'] == 'Added']
            self.removed = df.loc[df['Comment'] == 'Removed']
            self.altered = df.loc[df['Comment'] == 'Altered']

    def __add__(self, other):

        # this should be made more robust to catch conflicts
        change = INPSectionDiff()
        change.added = self.added.append(other.added)
        change.removed = self.removed.append(other.removed)
        change.altered = self.altered.append(other.altered)

        return change

    def __str__(self):
        s = ''
        diff = pd.concat([self.removed, self.added, self.altered])
        diffs = '\n{}'.format(diff.head().to_string())
        return s+diffs


class INPDiff(object):
    def __init__(self, model1=None, model2=None):
        """
        diff of all INP sections between two models
        :param model1:
        :param model2:
        >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES_XY_B
        >>> mydiff = INPDiff(MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES_XY_B)
        >>> mydiff.diffs['[XSECTIONS]']
                 Shape  Geom1  Geom2  Geom3  Geom4  Barrels  ;  Comment                     Origin
        Link
        1:4   CIRCULAR      1      0      0      0      1.0  ;  Removed  model_full_features_b.inp
        2:5   CIRCULAR      1      0      0      0      1.0  ;  Removed  model_full_features_b.inp
        3:4   CIRCULAR      1      0      0      0      1.0  ;  Removed  model_full_features_b.inp
        4:5   CIRCULAR      1      0      0      0      1.0  ;  Removed  model_full_features_b.inp
        5:J1  CIRCULAR      1      0      0      0      1.0  ;  Removed  model_full_features_b.inp
        <BLANKLINE>
        >>> print(mydiff)
        """
        m1 = model1
        m2 = model2
        if isinstance(m1, str):
            m1 = swmmio.Model(m1)
        if isinstance(m2, str):
            m2 = swmmio.Model(m2)
        self.m1 = m1
        self.m2 = m2
        self.diffs = OrderedDict()

        m1_sects = get_inp_sections_details(m1.inp.path, include_brackets=True)
        m2_sects = get_inp_sections_details(m2.inp.path, include_brackets=True)

        # get union of sections found, maintain order
        sects = list(m1_sects.keys()) + list(m2_sects.keys())
        seen = set()
        self.all_sections = [x for x in sects if not (x in seen or seen.add(x))]
        self.all_inp_objects = OrderedDict(m1_sects)
        self.all_inp_objects.update(m2_sects)
        for section in self.all_sections:
            if section not in problem_sections:
                # calculate the changes in the current section
                changes = INPSectionDiff(m1, m2, section)

                self.diffs[section] = changes

    def __str__(self):
        s = '--- {}\n+++ {}\n\n'.format(self.m1.inp.path, self.m2.inp.path)
        diffs = '\n\n'.join(['{}\n{}'.format(sect, d.__str__()) for sect, d in self.diffs.items()])
        return s+diffs


def generate_inp_from_diffs(basemodel, inpdiffs, target_dir):
    """
    create a new inp with respect to a baseline inp and changes instructed
    with a list of inp diff files (build instructions). This saves having to
    recalculate the differences of each model from the baseline whenever we want
    to combine versions.

    NOTE THIS ISN'T USED ANYWHERE. DELETE ????
    """

    # step 1 --> combine the diff/build instructions
    allheaders = funcs.complete_inp_headers(basemodel.inp.path)
    combi_build_instr_file = os.path.join(target_dir, 'build_instructions.txt')
    newinp = os.path.join(target_dir, 'new.inp')
    with open(combi_build_instr_file, 'w') as f:
        for header, _ in allheaders.items():
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
                    # remove the extra space between data in the same table
                    # coming from diffrent models.
                    if sect_s[-2:] == '\n\n':  # NOTE Check this section...
                        s += sect_s[:-1]
                    else:
                        s += sect_s

            f.write(s + '\n')

    # step 2 --> clean up the new combined diff instructions
    # df_dict = clean_inp_diff_formatting(combi_build_instr_file) #makes more human readable

    # step 3 --> create a new inp based on the baseline, with the inp_diff
    # instructions applied
    with open(newinp, 'w') as f:
        for section, _ in allheaders.items():
            print(section)
            if section not in problem_sections and allheaders[section]['columns'] != ['blob']:
                # check if a changes from baseline spreadheet exists, and use this
                # information if available to create the changes array
                df = create_dataframeINP(basemodel.inp.path, section)
                df['Origin'] = ''  # add the origin column if not there
                if section in df_dict:
                    df_change = df_dict[section]
                    ids_to_drop = df_change.loc[df_change['Comment'].isin(['Removed', 'Altered'])].index
                    df = df.drop(ids_to_drop)
                    df = df.append(df_change.loc[df_change['Comment'].isin(['Added', 'Altered'])])
                new_section = df
            else:
                # blindly copy this section from the base model
                new_section = create_dataframeINP(basemodel.inp.path, section=section)

            # write the section into the inp file and the excel file
            vc_utils.write_inp_section(f, allheaders, section, new_section)


def create_inp_build_instructions(inpA, inpB, path, filename, comments=''):
    """
    pass in two inp file paths and produce a spreadsheet showing the differences
    found in each of the INP sections. These differences should then be used
    whenever we need to rebuild this model from the baseline reference model.


    Note: this should be split into a func that creates a overall model "diff"
    that can then be written as a BI file or used programmatically
    """

    allsections_a = funcs.complete_inp_headers(inpA)
    modela = swmmio.Model(inpA)
    modelb = swmmio.Model(inpB)

    # create build insructions folder
    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path, filename) + '.txt'

    problem_sections = ['[TITLE]', '[CURVES]', '[TIMESERIES]', '[RDII]', '[HYDROGRAPHS]']
    with open(filepath, 'w') as newf:

        # write meta data
        metadata = {
            # 'Baseline Model':modela.inp.path,
            # 'ID':filename,
            'Parent Models': {
                'Baseline': {inpA: vc_utils.modification_date(inpA)},
                'Alternatives': {inpB: vc_utils.modification_date(inpB)}
            },
            'Log': {filename: comments}
        }
        # print metadata
        vc_utils.write_meta_data(newf, metadata)
        for section, _ in allsections_a.items():
            if section not in problem_sections:
                # calculate the changes in the current section
                changes = INPSectionDiff(modela, modelb, section)
                data = pd.concat([changes.removed, changes.added, changes.altered])
                # vc_utils.write_excel_inp_section(excelwriter, allsections_a, section, data)
                vc_utils.write_inp_section(newf, allsections_a, section, data, pad_top=False,
                                           na_fill='NaN')  # na fill fixes SNOWPACK blanks spaces issue

    return BuildInstructions(filepath)


def merge_models(inp1, inp2, target='merged_model.inp'):
    """
    Merge two separate swmm models into one model. This creates a diff, ignores
    removed sections, and uses inp1 settings where conflicts exist (altered sections in diff)
    :param m1:
    :param m2:
    :return:
    >>> from swmmio.tests.data import MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES_XY_B
    >>> merged_model = merge_models(MODEL_FULL_FEATURES_XY, MODEL_FULL_FEATURES_XY_B)
    """
    # model object to store resulting merged model
    m3 = swmmio.Model(inp1)

    inp_diff = INPDiff(inp1, inp2)
    with open(target, 'w') as newf:
        for section, _ in inp_diff.all_inp_objects.items():
            # don't consider the "removed" parts of the diff
            print('{}: {}'.format(section,inp_diff.all_inp_objects[section]['columns']))
            # check if the section is not in problem_sections and there are changes
            # in self.instructions and commit changes to it from baseline accordingly
            if (section not in problem_sections
                    and inp_diff.all_inp_objects[section]['columns'] != ['blob']
                    and section in inp_diff.diffs):

                # df of baseline model section
                basedf = create_dataframeINP(m3.inp.path, section)

                # grab the changes to
                changes = inp_diff.diffs[section]

                # remove elements that have alterations keep ones tagged for removal
                # (unchanged, but not present in m2)
                remove_ids = changes.altered.index
                new_section = basedf.drop(remove_ids)

                # add elements
                new_section = pd.concat([new_section, changes.altered, changes.added])
            else:
                # section is not well understood or is problematic, just blindly copy
                new_section = create_dataframeINP(m3.inp.path, section=section)
                print ('dealing with confusing section: {}\n{}'.format(section, new_section))

            # print(new_section.head())
            # write the section
            vc_utils.write_inp_section(newf, inp_diff.all_inp_objects, section, new_section, pad_top=True)

    return target
