"""
Utility functions related to comparing SWMM models
"""
import pandas as pd


def conduits_cost_estimate(conduit_df, additional_costs=None):


    def calc_area(row):
        """calculate the cross-sectional area of a sewer segment. If the segment
        is multi-barrel, the area will reflect the total of all barrels"""

        if row.Shape == 'CIRCULAR':
            d = row.Geom1
            area = 3.1415 * (d * d) / 4
            return round((area * row.Barrels),2)

        if 'RECT' in row.Shape:
            #assume triangular bottom sections (geom3) deepens the excavated box
            return (row.Geom1 + row.Geom3) * float(row.Geom2) * row.Barrels
        if row.Shape =='EGG':
            #assume geom1 is the span
            return row.Geom1*1.5 * row.Barrels

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

    conduit_df['XArea'] = conduit_df.apply (lambda r: calc_area (r), axis=1)
    conduit_df['UnitCostLF'] = conduit_df.apply(lambda r: get_unit_cost(r), axis=1)
    conduit_df['Volume'] = conduit_df.apply (lambda r:compute_volume (r), axis=1)
    conduit_df['CostEstimate'] = conduit_df.apply (lambda r:compute_conduit_cost (r),axis=1)

    if additional_costs:
        #read in the supplemental cost data from the csv
        addcosts = pd.read_csv(additional_costs, index_col=0)
        conduit_df = conduit_df.join(addcosts).fillna(0)
        conduit_df['TotalCostEstimate'] = conduit_df.apply (lambda r:
                                                              added_cost(r),
                                                              axis=1)
    else:
        # NOTE this lingo here is weak...
        #additional_costs not provided, rename the CostEstimate to TotalCostEstimate
        conduit_df = conduit_df.rename(columns={"CostEstimate": "TotalCostEstimate"})

    return conduit_df
