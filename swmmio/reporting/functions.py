"""
Utility functions related to comparing SWMM models
"""
import pandas as pd
from swmmio.version_control import inp

def length_of_new_and_replaced_conduit(model1, model2):

    changes = inp.Change(model1, model2, section ='[CONDUITS]')
    df = pd.concat([changes.added, changes.altered])

    return df.Length.sum()
