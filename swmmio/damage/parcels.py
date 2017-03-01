#PARCEL FLOOD DAMAGE CALCULATIONS
#ASSUMES INPUT DATA IN ADDITION TO SWMM results


import pandas as pd

def flood_duration(node_flood_df, parcel_node_df=None,
                   parcel_node_join_csv=None, threshold=0.08333):

    """
    Given a dataframe with node flood duration and a csv table resulting
    from a one-to-many join of model shed drainage areas to parcels, this
    function returns a dataframe with flood data associated to each node.

    Assumptions:
        Flooding that occurs at any node in the SWMM model is applied to all
        parcels falling within that node's drainage area. Drainage areas are
        assumed to be generated using a Thiessen polygon method, or similar.
    """

    #read the one-to-many parcels-nodes table into a Dataframe if csv provided
    if parcel_node_df is None:
        parcel_node_df = pd.read_csv(parcel_node_join_csv)

    useful_cols = ['PARCELID', 'OUTLET', 'SUBCATCH', 'ADDRESS']
    parcel_node_df = parcel_node_df[useful_cols]

    #clean up the nodes df, using only a few columns
    useful_cols = ['HoursFlooded', 'TotalFloodVol', 'MaxHGL', 'MaxNodeDepth']
    node_flood_df = node_flood_df[useful_cols]

    #join flood data to parcels by outlet, clean a bit more of the cols
    parcel_flood = pd.merge(parcel_node_df, node_flood_df,
                            left_on='OUTLET', right_index=True)
    parcel_flood = parcel_flood[['PARCELID','HoursFlooded','TotalFloodVol']]

    #groupby parcel id to aggregate the duplicates, return the max of all dups
    parcel_flood_max = parcel_flood.groupby('PARCELID').max()

    #filter only parcels with flood duration above the threshold
    parcel_flood_max = parcel_flood_max.loc[parcel_flood_max.HoursFlooded>=threshold]
    return parcel_flood_max

def compare_flood_duration(basedf,altdf,threshold=0.08333,delta_threshold=0.25):

    df = basedf.join(altdf, lsuffix='Baseline', rsuffix='Proposed', how='outer')
    df = df.fillna(0) #any NaN means no flooding observed
    delta = df.HoursFloodedProposed - df.HoursFloodedBaseline
    df = df.assign(DeltaHours=delta)

    def categorize(parcel):
        #rename for logic clarity
        existing_flood_duration = parcel.HoursFloodedBaseline
        proposed_flood_duration = parcel.HoursFloodedProposed
        flood_duration_delta = parcel.DeltaHours

        if ((existing_flood_duration >= threshold)
            and (proposed_flood_duration >= threshold)):
            #parcel used to and still floods, check how it changed:
            if flood_duration_delta > delta_threshold:
                #flood duration increased (more than delta_threhold)
                return 'increased_flooding'

            elif flood_duration_delta < - delta_threshold:
                #flooding duration decreased (more than delta_threhold)
                return 'decreased_flooding'

        elif (existing_flood_duration < threshold
              and proposed_flood_duration >= threshold
              and abs(flood_duration_delta) >= delta_threshold):
            #flooding occurs where it perviously did not
            return 'new_flooding'

        elif (existing_flood_duration >= threshold
              and proposed_flood_duration < threshold
              and abs(flood_duration_delta) >= delta_threshold):
            #parcel that previously flooded no longer does
            return 'eliminated_flooding'

    cats = df.apply(lambda row: categorize(row), axis=1)
    df = df.assign(Category=cats)

    return df
