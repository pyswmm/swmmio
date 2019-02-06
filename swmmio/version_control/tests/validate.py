#METHODS USED TO VALIDATE INP FILES (e.g. ensure no duplicates exists)

from swmmio.utils import functions as funcs
from swmmio.utils import dataframes

def search_for_duplicates(inp_path, verbose = False):
    """
    scan an inp file and determine if any element IDs are duplicated in
    any section. Method: count the uniques and compare to total length
    """
    headers = funcs.complete_inp_headers(inp_path)['headers']
    dups_found = False
<<<<<<< HEAD
    for header, cols, in headers.iteritems():
=======
    for header, cols, in headers.items():
>>>>>>> 20c5e0571a9e48d405822dc963669df8811e6d33
        if cols != 'blob':

            df = dataframes.create_dataframeINP(inp_path, section=header)
            elements = df.index
            n_unique = len(elements.unique()) #number of unique elements
            n_total = len(elements) #total number of elements
            if verbose:
<<<<<<< HEAD
                print '{} -> (uniques, total) -> ({}, {})'.format(header, n_unique , n_total)

            if n_unique != n_total:
                dups = ', '.join(df[df.index.duplicated()].index.unique().tolist())
                print 'duplicate found in {}\nsection: {}\n{}'.format(inp_path, header, dups)
=======
                print('{} -> (uniques, total) -> ({}, {})'.format(header, n_unique , n_total))

            if n_unique != n_total:
                dups = ', '.join(df[df.index.duplicated()].index.unique().tolist())
                print('duplicate found in {}\nsection: {}\n{}'.format(inp_path, header, dups))
>>>>>>> 20c5e0571a9e48d405822dc963669df8811e6d33
                dups_found = True

    return dups_found
