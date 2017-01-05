
#Module is intended to provide high level access to post processing routines
#such that standard reporting and figures can be generated to report on the
#perfomance of given SFR alternatives/options

from swmmio.reporting import compare_models as scomp
from swmmio.reporting import functions
from swmmio.utils import swmm_utils as su
from swmmio.graphics import swmm_graphics as sg
from swmmio.graphics import draw_utils as du
from swmmio.utils.dataframes import create_dataframeRPT
from swmmio import parcels as p
import os
import math
import pandas as pd
from definitions import *



class Report(object):

    def __init__(self, baseline_model, option, existing_parcel_flooding = None,
                 additional_costs=None):

        #parcel_features = 'PWD_PARCELS_SHEDS_PPORT' #'PWD_PARCELS_SHEDS'
        #parcel calculations
        anno_results={}
        #if not existing_parcel_flooding:
        existing_parcel_flooding = p.parcel_flood_duration(baseline_model, parcel_features=PARCEL_FEATURES,
    											bbox=None, anno_results=anno_results)['parcels']

        proposed_parcel_flooding = p.parcel_flood_duration(option, parcel_features=PARCEL_FEATURES,
												bbox=None, anno_results=anno_results)['parcels']

        delta_parcels = p.compareParcels(existing_parcel_flooding, proposed_parcel_flooding,
										bbox=None, floodthreshold=0.0833,
										delta_threshold=0.25,
										anno_results=anno_results)

        self.baseline=baseline_model
        self.option = option
        self.delta_parcels = delta_parcels['parcels']
        self.anno_results = anno_results
        self.sewer_miles_new = functions.length_of_new_and_replaced_conduit(baseline_model, option)  / 5280.0
        self.sewer_miles_replaced = None
        self.storage_new = None #some volume measurement
        self.cost_estimate_data = functions.estimate_cost_of_new_conduits(baseline_model, option, additional_costs)
        self.cost_estimate = self.cost_estimate_data.TotalCostEstimate.sum() / math.pow(10, 6)
        self.parcels_new_flooding = delta_parcels['new_flooding']
        self.parcels_worse_flooding = delta_parcels['increased_flooding']
        self.parcels_eliminated_flooding = delta_parcels['eliminated_flooding']
        self.parcels_flooding_improved = delta_parcels['decreased_flooding'] + delta_parcels['eliminated_flooding']

        print '{} new miles '.format(self.sewer_miles_new)
        print '{} parcels deltas'.format(len(self.delta_parcels))

    def write (self, report_dir):
        #generate the figures
        generate_figures(self.baseline, self.option,
                        delta_parcels = self.delta_parcels,
                        anno_results = self.anno_results,
                        bbox = su.d68d70, imgDir=report_dir)

        #write the cost estimate file
        costsdf  = self.cost_estimate_data[['Length', 'Shape', 'Geom1', 'Geom2',
                                            'Geom3', 'XArea', 'Volume',
                                            'CostEstimate', 'AdditionalCost',
                                            'AddCostNotes', 'TotalCostEstimate']]
        costsdf.to_csv(os.path.join(report_dir, self.option.inp.name + '_cost_data.csv'))
        #write text report
        with open(os.path.join(report_dir, 'report.txt'), 'w') as f:
            f.write('Parcels Improved {}\n'.format(self.parcels_flooding_improved))
            f.write('New Sewer Miles {}\n'.format(self.sewer_miles_new))
            f.write('Cost Estimate {}\n'.format(self.cost_estimate))

def generate_figures(model1, model2, delta_parcels=None, anno_results = {},
                    bbox=None, imgDir=None, verbose=False):

    #calculate the bounding box of the alternative/option
    #such that figures can be zoomed to the area
    #bbox = scomp.extents_of_changes(model1, model2, extent_buffer=1.0)

    #SIMPLE PLAN VIEW OF OPTION (showing new conduits)
    imgname = "00 Proposed Infrastructure"
    scomp.drawModelComparison(model1, model2, nodeSymb=None, parcelSymb=None,
                                bbox=bbox, imgName=imgname, imgDir=imgDir)

    #EXISTING CONDITIONS PARCEL FLOOD DURATION
    imgname = "01 Existing Parcel Flood Duration"
    if not imgDir:
        imgDir=os.path.join(model2.inp.dir, 'img')
    sg.drawModel(model1, conduitSymb=None, nodeSymb=None, bbox=bbox,
                 imgName=imgname, imgDir=imgDir)

    #PROPOSED CONDITIONS FLOOD DURATION
    imgname = "02 Proposed Parcel Flood Duration"
    sg.drawModel(model2, conduitSymb=None, nodeSymb=None, bbox=bbox,
                  imgName=imgname, imgDir=imgDir)

    #IMPACT OF INFRASTRUCTURE
    imgname = "03 Impact of Option"
    scomp.drawModelComparison(model1, model2,
                                delta_parcels = delta_parcels,
                                anno_results = anno_results,
                                nodeSymb=None, bbox=bbox,
                                imgName=imgname, imgDir=imgDir)

    #IMPACT OF INFRASTRUCTURE STUDY-AREA-WIDE
    imgname = "04 Impact of Option - Overall"
    scomp.drawModelComparison(model1, model2,
                                delta_parcels = delta_parcels,
                                anno_results = anno_results,
                                nodeSymb=None, bbox=su.study_area,
                                imgName=imgname, imgDir=imgDir)

    #IMPACT OF INFRASTRUCTURE CHANGE OF PEAK FLOW
    imgname = "05 Hydraulic Deltas"
    scomp.drawModelComparison(model1, model2,
                                delta_parcels = delta_parcels,
                                anno_results = anno_results,
                                conduitSymb=du.conduit_options('compare_flow'),
                                bbox=bbox, imgName=imgname, imgDir=imgDir)


def timeseries_join(elements, *models):
    """
    Given a list of element IDs and Model objects, a dataframe is returned
    with the elements' time series data for each model.
    Example:
        df = timeseries_join(elements = ['P1, P2'], model1, model2)
        returns df with index = DateTime and cols = [model1_P1_FlowCFS, model1_P2_FlowCFS,
                                                    model2_P1_FlowCFS, model2_P2_FlowCFS]
    """
    # dfs = [[dataframes.create_dataframeRPT(m.rpt.path, 'Link Results', el)[['FlowCFS']]
    #         for el in elements] for m in models]
    param_name = 'FlowCFS' #as named by our dataframe method
    section_name = 'Link Results' #in the rpt
    dfs = [create_dataframeRPT(m.rpt.path, section_name, elem)[[param_name]].rename(
                columns={param_name:'{}_{}_{}'.format(m.inp.name, elem, param_name)}
                )
                for m in models for elem in elements]

    df = pd.concat(dfs, axis=1)
    return df
