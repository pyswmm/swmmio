#READ/WRITE REPORTS AS JSON
import json
import pandas as pd
from pandas.io.json import json_normalize
from swmmio.utils import spatial
from swmmio.graphics import swmm_graphics as sg
from swmmio.reporting.reporting import FloodReport
from definitions import *
import geojson


def decode_report(rpt_path):
    #read report from json into a dict
    with open(rpt_path, 'r') as f:
        read_rpt = json.loads(f.read())

    #parse the geojson
    def df_clean(uncleandf):
        cleaned_cols = [x.split('.')[-1] for x in uncleandf.columns]
        uncleandf.columns = cleaned_cols
        clean_df = uncleandf.rename(columns={'coordinates':'coords'}).drop(['type'], axis=1)
        clean_df = clean_df.set_index(['Name'])
        return clean_df

    #parse conduit data into a dataframe
    conds_df = json_normalize(read_rpt['conduits']['features'])
    conds_df = df_clean(conds_df)

    #parse node data into a dataframe
    nodes_df = json_normalize(read_rpt['nodes']['features'])
    nodes_df = df_clean(nodes_df)

    #parse parcel data into a dataframe
    pars_df = json_normalize(read_rpt['parcels']['features'])
    pars_df = df_clean(pars_df)

    return {'conduits':conds_df, 'nodes':nodes_df, 'parcels':pars_df}

def encode_report(rpt, rpt_path, is_compare=False):

    rpt_dict = {}

    #write parcel json files
    parcels = spatial.read_shapefile(sg.config.parcels_shapefile)
    parcels = parcels[['PARCELID', 'coords']] #omit 'ADDRESS', 'OWNER1'
    if is_compare:
        flooded = rpt.flood_comparison
        rpt = rpt.alt_report
    else:
        flooded = rpt.parcel_flooding
    flooded = pd.merge(flooded, parcels, right_on='PARCELID', left_index=True)
    rpt_dict['parcels'] = spatial.write_geojson(flooded, geomtype='polygon')

    #encode conduit data into geojson
    rpt_dict['conduits'] = spatial.write_geojson(rpt.model.conduits())
    rpt_dict['nodes'] = spatial.write_geojson(rpt.model.nodes(),geomtype='point')



    with open(rpt_path, 'w') as f:
        f.write(json.dumps(rpt_dict))

    #start writing that thing
    with open(BETTER_BASEMAP_PATH, 'r') as bm:
        filename = os.path.join(os.path.dirname(rpt_path), rpt.model.name + '.html')
        with open(filename, 'wb') as newmap:
            for line in bm:
                if '//INSERT GEOJSON HERE ~~~~~' in line:
                    newmap.write('conduits = {};\n'.format(geojson.dumps(rpt_dict['conduits'])))
                    newmap.write('nodes = {};\n'.format(geojson.dumps(rpt_dict['nodes'])))
                    newmap.write('parcels = {};\n'.format(geojson.dumps(rpt_dict['parcels'])))
                else:
                    newmap.write(line)
