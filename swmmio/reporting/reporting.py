
#Module is intended to provide high level access to post processing routines
#such that standard reporting and figures can be generated to report on the
#perfomance of given SFR alternatives/options

import compare_models as scomp
from swmmio.utils import swmm_utils as su
from swmmio.graphics import swmm_graphics as sg
from swmmio.graphics import draw_utils as du
from swmmio.utils.dataframes import create_dataframeRPT
import os
import pandas as pd

def generate_figures(model1, model2, bbox=None):

    #calculate the bounding box of the alternative/option
    #such that figures can be zoomed to the area
    #bbox = scomp.extents_of_changes(model1, model2, extent_buffer=1.0)

    #SIMPLE PLAN VIEW OF OPTION (showing new conduits)
    imgname = "00 Proposed Infrastructure"
    scomp.drawModelComparison(model1, model2, nodeSymb=None,
                                parcelSymb=None, bbox=bbox, imgName=imgname)

    #EXISTING CONDITIONS PARCEL FLOOD DURATION
    imgname = "01 Existing Parcel Flood Duration"
    imgDir=os.path.join(model2.inp.dir, 'img')
    sg.drawModel(model1, conduitSymb=None, nodeSymb=None, bbox=bbox, imgName=imgname, imgDir=imgDir)

    #PROPOSED CONDITIONS FLOOD DURATION
    imgname = "02 Proposed Parcel Flood Duration"
    #ops.update({'conduitSymb':du.conduit_options('proposed_simple')})
    sg.drawModel(model2, conduitSymb=None, nodeSymb=None, bbox=bbox, imgName=imgname)

    #IMPACT OF INFRASTRUCTURE
    imgname = "03 Impact of Option"
    scomp.drawModelComparison(model1, model2, nodeSymb=None, bbox=bbox, imgName=imgname)

    #IMPACT OF INFRASTRUCTURE STUDY-AREA-WIDE
    imgname = "04 Impact of Option - Overall"
    scomp.drawModelComparison(model1, model2, nodeSymb=None, bbox=su.study_area, imgName=imgname)

    #IMPACT OF INFRASTRUCTURE CHANGE OF PEAK FLOW
    imgname = "05 Hydraulic Deltas"
    scomp.drawModelComparison(model1, model2, conduitSymb=du.conduit_options('compare_flow'),
                                bbox=bbox, imgName=imgname)


def timeseries_join(elements, *models):
    """
    Given a list of element IDs and Model objects, a dataframe is returned
    with the elements' time series data for each model.
    Example:
        df = timeseries_join(elements = ['P1, P2'], model1, model2)
        returns df with index = DateTime and cols = [model1_P1_FlowCFS, model1_P2_FlowCFS,
                                                    model2_P1_FlowCFS, model2_P2_FlowCFS]
    """
    # dfs = [[dataframes.create_dataframeRPT(m.rpt, 'Link Results', el)[['FlowCFS']]
    #         for el in elements] for m in models]
    param_name = 'FlowCFS' #as named by our dataframe method
    section_name = 'Link Results' #in the rpt
    dfs = [create_dataframeRPT(m.rpt, section_name, elem)[[param_name]].rename(
                columns={param_name:'{}_{}_{}'.format(m.inp.name, elem, param_name)}
                )
                for m in models for elem in elements]

    df = pd.concat(dfs, axis=1)
    return df
