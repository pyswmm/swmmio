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


def identify_possible_next_ops(option_id):

    """
    given a alternative ID, return a list of possible next implementation levels.
        alt = alternative, the major category of an SFR solution. AKA a
        "segment category"

        degree = the level of implementation of the alternative. E.g.
        3rd implementation scenario of Mifflin alternative

    requires that the alternative ID "buckets" are sorted alphabetically in each
    alternative ID.
    """
    alt_buckets = {'M':0, 'R':0, 'W':0}
    #first, find the alts that are currently not implemented at all
    possibles = []
    possibles += [{x:1} for x in alt_buckets.keys() if x not in filter(str.isalpha, option_id)]

    #iterate through option id's components
    for op in option_id.split('_'):

        #parse the passed in option into its buckets
        alt_name = filter(str.isalpha, op)
        alt_degree = int(filter(str.isdigit, op))
        alt_buckets.update({alt_name:alt_degree})

        #increment the option_id
        nxt_degree = alt_degree + 1
        next_op = {alt_name:nxt_degree}
        possibles.append(next_op)


    results = [] # output list of potential next implementation scenarios
    for p in possibles:
        # "deep copy" the buckets dict
        d = {k:v for k,v in alt_buckets.items()} #{'M':1, 'R':1, 'W':0}
        d.update(p)

        #remove any genres with zero implementation
        d2 = { k:v for k, v in d.items() if v != 0 }

        #convert to id format, sort alphebetically
        string_alts = ['{}{}'.format(key, str(val).zfill(2)) for key, val in d2.iteritems()]
        reformatted_op = '_'.join(sorted(string_alts))
        results.append(reformatted_op)

    return results

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
        """calculate the cross-sectional area of a sewer segment"""

        if row.Shape == 'CIRCULAR':
            d = row.Geom1
            area = 3.1415 * (d * d) / 4
            return round((area * row.Barrels),2)

        if 'RECT' in row.Shape:
            #assume triangular bottom sections (geom3) deepens the excavated box
            return (row.Geom1 + row.Geom3) * row.Geom2
        if row.Shape =='EGG':
            #assume geom1 is the span
            return row.Geom1*1.5

    def get_unit_cost(row):
        cost_dict = {1.0:570,
                    1.5:570,
                    1.75:610,
                    2.0:680,
                    2.25:760,
                    2.5:860,
                    3.0:1020,
                    3.5:1200,
                    4.0:1400,
                    4.5:1550,
                    5.0:1700,
                    5.5:1960,
                    6.0:2260,
                    7.0:2600,
                    7.5:3000,
                    }

        def round_to(n, precision):
            correction = 0.5 if n >= 0 else -0.5
            return int( n/precision+correction ) * precision

        def round_to_05(n):
            return round_to(n, 0.05)

        cleaned_geom = round_to_05(row.Geom1)
        # print '{}: Raw Geom1 = {} is rounded  to {}'.format(row.InletNode, row.Geom1, cleaned_geom)

        RectBox_UnitCost = 80
        if row.Shape == 'CIRCULAR':
            try:
                val = cost_dict[cleaned_geom]
            except:
                val = 0
            return val
        if 'RECT' in row.Shape:
            """
            assume any triangular bottom section adds to
            overall excavation box section
            """
            val = round(RectBox_UnitCost*row.XArea,2)
            return val
        if row.Shape == 'EGG':
            """
            We're going to treat this like a box"
            """
            val = round(RectBox_UnitCost*row.XArea,2)
            return val


    def compute_conduit_cost(row):
        return row.UnitCostLF * row.Length

    def compute_volume(row):
        return row.XArea * row.Length

    def added_cost(row):
        #add in any additional cost data (from crossing water mains, etc)
        return row.CostEstimate + row.AdditionalCost

    newconduits['XArea'] = newconduits.apply (lambda row: calc_area (row), axis=1)
    newconduits['UnitCostLF'] = newconduits.apply(lambda row: get_unit_cost(row), axis=1)
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
