#UTILITY/HELPER FUNCTOINS FOR DRAWING
import pandas as pd
import math
from swmmio.graphics import * #constants


def pixel_coords_from_irl_coords(df, px_width=2048,
									bbox=None, shift_ratio=None):

    """
    given a dataframe with element id (as index) and X1, Y1 columns (and
    optionally X2, Y2 columns), return a dataframe with the coords as pixel
    locations based on the targetImgW.
    """

    df = df.loc[pd.notnull(df.coords)]
    xs = [xy[0] for verts in df.coords.tolist() for xy in verts]
    ys = [xy[1] for verts in df.coords.tolist() for xy in verts]


    xmin, ymin, xmax, ymax = (min(xs), min(ys), max(xs), max(ys))
    if not bbox:
        #start by determining the max and min coordinates in the whole model
        bbox = [(xmin, ymin),(xmax, ymax)]

    #find the actual dimensions, use to find scale factor
    height = bbox[1][1] - bbox[0][1]
    width = bbox[1][0] - bbox[0][0]
    if not shift_ratio:
        # to scale down from coordinate to pixels
        shift_ratio = float(px_width / width)

    def shft_coords(row):
        #parse through coords (nodes, or link) and adjust for pixel space
        return [(int((xy[0] - xmin)*shift_ratio),
					int((height - xy[1] + ymin)*shift_ratio))
						for xy in  row.coords]

    #copy the given df and insert new columns with the shifted coordinates
    draw_coords = df.apply(lambda row:shft_coords(row), axis=1)
    df = df.assign(draw_coords = draw_coords)

    return df, bbox, int(height*shift_ratio), int(width*shift_ratio)

def circle_bbox(coordinates, radius=5):
    """the bounding box of a circle given as centriod coordinate and radius"""

    x = coordinates[0]
    y = coordinates[1]
    r = radius

    return (x-r, y-r, x+r, y+r)

def length_bw_coords(upstreamXY, downstreamXY):

    #return the distance (units based on input) between two points
    x1 = float(upstreamXY[0])
    x2 = float(downstreamXY[0])
    y1 = float(upstreamXY[1])
    y2 = float(downstreamXY[1])

    return math.hypot(x2 - x1, y2 - y1)
