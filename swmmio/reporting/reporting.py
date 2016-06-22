
#Module is intended to provide high level access to post processing routines
#such that standard reporting and figures can be generated to report on the
#perfomance of given SFR alternatives/options

import compare_models as scomp
from swmmio.utils import swmm_utils as su
from swmmio.graphics import swmm_graphics as sg
from swmmio.graphics import draw_utils as du
import os

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
