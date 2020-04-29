from datetime import datetime
import os
import json
import shutil

from swmmio.utils.functions import format_inp_section_header


def copy_rpts_hsf(from_dir, to_dir, search_dir):
    """
    walk through a directory and find all rpts and hot start files and copy to
    another location based on the relative path from the to_dir.

    ex:
        to_directory = r'P:\02_Projects\SouthPhila\SE_SFR\MasterModels'
        from_dir = r'F:\models\SPhila\MasterModels_170104'
        search_dir = r'F:\models\SPhila\MasterModels_170104\Combinations'
        copy_rpts_hsf(from_dir, to_dir, search_dir)


    Good for model results written on a local drive to a network drive
    """

    # chain.from_iterable(os.walk(path) for path in paths):
    for path, dirs, files in os.walk(search_dir):
        for f in files:
            if '.rpt' in f:
                rpt_path = os.path.join(path, f)
                to_dir = path.replace(from_dir, to_dir)
                dest = os.path.join(to_dir, f)
                shutil.copyfile(src=rpt_path, dst=dest)

            if '.hsf' in f:
                hsf_path = os.path.join(path, f)
                to_dir = path.replace(from_dir, to_dir)
                dest = os.path.join(to_dir, f)
                shutil.copyfile(src=hsf_path, dst=dest)


def write_inp_section(file_object, allheaders, sectionheader, section_data, pad_top=True, na_fill=''):
    """
    given an open file object, list of header sections, the current
    section header, and the section data in a Pandas Dataframe format, this function writes
    the data to the file object.
    """

    f = file_object
    add_str = ''
    sectionheader = format_inp_section_header(sectionheader)
    if not section_data.empty:
        if pad_top:
            f.write('\n\n' + sectionheader + '\n')  # add SWMM-friendly header e.g. [DWF]
        else:
            f.write(sectionheader + '\n')
        if allheaders and (sectionheader in allheaders) and allheaders[sectionheader]['columns'] == ['blob']:
            # to left justify based on the longest string in the blob column
            formatter = '{{:<{}s}}'.format(section_data[sectionheader].str.len().max()).format
            add_str = section_data.fillna('').to_string(
                index_names=False,
                header=False,
                index=False,
                justify='left',
                formatters={sectionheader: formatter}
            )

        else:
            # naming the columns to the index name so the it prints in-line with col headers
            f.write(';;')
            # to left justify on longest string in the Comment column
            # this is overly annoying, to deal with 'Objects' vs numbers to remove
            # two bytes added from the double semicolon header thing (to keep things lined up)
            objectformatter = {hedr: ' {{:<{}}}'.format(section_data[hedr].apply(str).str.len().max()).format
                               for hedr in section_data.columns}
            numformatter = {hedr: '  {{:<{}}}'.format(section_data[hedr].apply(str).str.len().max()).format
                            for hedr in section_data.columns if section_data[hedr].dtype != "O"}
            objectformatter.update(numformatter)
            add_str = section_data.fillna(na_fill).to_string(
                index_names=False,
                header=True,
                justify='left',
                formatters=objectformatter  # {'Comment':formatter}
            )

        # write the dataframe as a string
        f.write(add_str + '\n\n')


def write_meta_data(file_object, metadicts):
    file_object.write(json.dumps(metadicts, indent=4))
    file_object.write('\n' + '=' * 100 + '\n\n')


def read_meta_data(filepath):
    s = ''
    with open(filepath) as file_object:
        for line in file_object:
            if '================' in line:
                break
            s += line.strip()

    return json.loads(s)


def bi_is_current(build_instr_file):
    """
    check if a given build instruction file has any parent models whose
    date modified does not match the date modified of the parent INP file
    """

    meta = read_meta_data(build_instr_file)
    baseline = meta['Parent Models']['Baseline']
    alternatives = meta['Parent Models']['Alternatives']
    # parents = baseline.update(alternatives)
    # print meta['Parent Models']['Baseline']
    # print alternatives
    for inp, revisiondate in baseline.items():
        if modification_date(inp) != revisiondate:
            return False

    for inp, revisiondate in alternatives.items():
        if modification_date(inp) != revisiondate:
            return False

    return True


def bi_latest_parent_date_modified(vc_dir, parentname):
    """
    given a path to a version control directory of build instructions and the
    name of the parent model, return the parent model's revision date
    """
    newest_bi = newest_file(vc_dir)
    meta = read_meta_data(newest_bi)
    # with open (newest_bi) as f:

    return meta['Parent Models'][parentname]


def newest_file(directory):
    """
    return the newest file (most recent) in a given directory. Beware that
    people report the min / max to do different things per OS...
    """
    files = os.listdir(directory)
    return max([os.path.join(directory, f) for f in files], key=os.path.getctime)


def modification_date(filename, string=True):
    """
    get modification datetime of a file
    credit: Christian Oudard
    'stackoverflow.com/questions/237079/how-to-get-file-creation-modification-
    date-times-in-python'
    """
    t = os.path.getmtime(filename)
    dt = datetime.fromtimestamp(t)
    if string:
        return dt.strftime("%y-%m-%d %H:%M")
    else:
        return dt  # datetime.fromtimestamp(t)

