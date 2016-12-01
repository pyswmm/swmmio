"""
Utility functions related to comparing SWMM models
"""
import pandas as pd
from swmmio.version_control import inp
from swmmio.utils.dataframes import create_dataframeINP
import os

def length_of_new_and_replaced_conduit(model1, model2):

    changes = inp.Change(model1, model2, section ='[CONDUITS]')
    df = pd.concat([changes.added, changes.altered])

    return df.Length.sum()

def create_shapefile_of_new_conduits(model1, model2, filename=None):
    """
    given a baseline model and a option, create a shapefile including only the
    new conduits.
    """

    changes = inp.Change(model1, model2, section='[CONDUITS]')
    df = pd.concat([changes.added, changes.altered])
    new_conduit_ids = df.index.tolist()

    if filename is None:
        filename = os.path.join(os.path.dirname(model2.inp.filePath),
                                'shapefiles',
                                model2.inp.name + '_new_conduits.shp')

    #create the containing directory if necessary
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    model2.export_to_shapefile(element_type='conduit',
                               filename=filename,
                               subset=new_conduit_ids)

def estimate_cost_of_new_conduits(baseline, newmodel, additional_costs=None):

    changes = inp.Change(baseline, newmodel, section ='[CONDUITS]')
    newconduits = pd.concat([changes.added, changes.altered])
    newconduits.drop([';', 'Comment', 'Origin'], axis=1, inplace=True)

    xsections = create_dataframeINP(newmodel.inp, section='[XSECTIONS]')
    xsections.drop([';', 'Comment', 'Origin'], axis=1, inplace=True)

    #join the xsection data to the newconduits df. convert geoms to numbers
    newconduits = newconduits.join(xsections)
    geoms = ['Geom1','Geom2','Geom2','Geom4']
    newconduits[geoms] = newconduits[geoms].apply(pd.to_numeric)

    def calc_area(row):
        """
        calculate the cross-sectional area of a sewer segment in the
        passed dataframe
        """
        if row.Shape == 'CIRCULAR':
            d = row.Geom1
            area = 3.1415 * (d * d) / 4
            return area * row.Barrels

        if 'RECT' in row.Shape:
            """
            assume any triangular bottom section adds to
            overall excavation box section
            """
            return (row.Geom1 + row.Geom3) * row.Geom2


    def compute_conduit_cost(row, unitcost=80):

        return row.XArea * row.Length * unitcost

    def compute_volume(row):
        return row.XArea * row.Length

    def added_cost(row):
        #add in any additional cost data (from crossing water mains, etc)
        return row.CostEstimate + row.AdditionalCost

    newconduits['XArea'] = newconduits.apply (lambda row: calc_area (row), axis=1)
    newconduits['Volume'] = newconduits.apply (lambda row:
                                               compute_volume (row), axis=1)
    newconduits['CostEstimate'] = newconduits.apply (lambda row:
                                                     compute_conduit_cost (row),
                                                     axis=1)

    if additional_costs:
        #read in the supplemental cost data from the csv
        addcosts = pd.read_csv(additional_costs, index_col=0)
        newconduits = newconduits.join(addcosts).fillna(0)
        newconduits['TotalCostEstimate'] = newconduits.apply (lambda row:
                                                              added_cost(row),
                                                              axis=1)
    else:
        # NOTE this lingo here is weak... 
        #additional_costs not provided, rename the CostEstimate to TotalCostEstimate
        newconduits = newconduits.rename(columns={"CostEstimate": "TotalCostEstimate"})

    return newconduits
