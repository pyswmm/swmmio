# METHODS USED TO VALIDATE INP FILES (e.g. ensure no duplicates exists)
import swmmio.utils.functions
import swmmio.utils.text
from swmmio.utils.dataframes import dataframe_from_inp


def search_for_duplicates(inp_path, verbose=False):
    """
    scan an inp file and determine if any element IDs are duplicated in
    any section. Method: count the uniques and compare to total length
    """
    headers = swmmio.utils.text.get_inp_sections_details(inp_path)["headers"]
    dups_found = False
    for header, cols, in headers.items():
        if cols != "blob":

            df = dataframe_from_inp(inp_path, section=header)
            elements = df.index
            n_unique = len(elements.unique()) #number of unique elements
            n_total = len(elements) #total number of elements
            if verbose:
                print(f"{header} -> (uniques, total) -> ({n_unique}, {n_total})")

            if n_unique != n_total:
                dups = ", ".join(df[df.index.duplicated()].index.unique().tolist())
                print(f"duplicate found in {inp_path}\nsection: {header}\n{dups}")
                dups_found = True

    return dups_found
