from swmmio.version_control.utils import write_inp_section
import swmmio
from swmmio.utils.text import get_inp_sections_details
import os
import tempfile
import shutil


def replace_inp_section(inp_path, modified_section_header, new_data):
    """
    modify an existing inp file by passing in new data (Pandas Dataframe)
    and the section header that should be modified. This function will overwrite
    all data in the old section with the passed data

    :param inp_path: path to inp file to be changed
    :param modified_section_header: section for which data should be change
    :param new_data: pd.DataFrame of data to overwrite data in the modified section
    :return: swmmio.Model instantiated with modified inp file
    """

    sections = get_inp_sections_details(inp_path)
    m = swmmio.Model(inp_path)
    with tempfile.TemporaryDirectory() as tempdir:
        with open(inp_path) as oldf:
            tmp_inp_path = os.path.join(tempdir, f'{m.inp.name}.inp')
            with open(tmp_inp_path, 'w') as new:

                # write each line as is from the original model until we find the
                # header of the section we wish to overwrite
                found_section = False
                found_next_section = False
                for line in oldf:
                    if modified_section_header in line:
                        # write the replacement data in the new file now
                        write_inp_section(new, sections,
                                          modified_section_header,
                                          new_data, pad_top=False)

                        found_section = True

                    if (found_section and any((f"[{es}]") in line for es in sections.keys()) and modified_section_header not in line):
                        found_next_section = True

                    if found_next_section or not found_section:
                        # write the lines from the original file
                        # if we haven't found the section to modify.
                        # if we have found the section and we've found the NEXT section
                        # continue writing original file's lines
                        new.write(line)

                if not found_section:
                    # the header doesn't exist in the old model
                    # so we should append it to the bottom of file
                    write_inp_section(new, sections,
                                      modified_section_header,
                                      new_data)

        # rename files and remove old if we should overwrite
        os.remove(inp_path)
        shutil.copy2(tmp_inp_path, inp_path)

    return swmmio.Model(inp_path)
