# UTILITY/HELPER FUNCTIONS FOR DRAWING
import pandas as pd
import math
import os
from PIL import Image


def save_image(img, img_path, antialias=True, auto_open=False):
    # get the size from the Image object
    imgSize = (img.getbbox()[2], img.getbbox()[3])
    if antialias:
        size = (int(imgSize[0] * 0.5), int(imgSize[1] * 0.5))
        img.thumbnail(size, Image.ANTIALIAS)

    img.save(img_path)
    if auto_open:
        os.startfile(img_path)


def px_to_irl_coords(df, px_width=4096.0, bbox=None, shift_ratio=None):
    """
    given a dataframe with element id (as index) and X1, Y1 columns (and
    optionally X2, Y2 columns), return a dataframe with the coords as pixel
    locations based on the targetImgW.
    """

    df = df.loc[pd.notnull(df.coords)]

    if not bbox:
        xs = [xy[0] for verts in df.coords.tolist() for xy in verts]
        ys = [xy[1] for verts in df.coords.tolist() for xy in verts]
        xmin, ymin, xmax, ymax = (min(xs), min(ys), max(xs), max(ys))
        bbox = [(xmin, ymin), (xmax, ymax)]

    else:
        df = clip_to_box(df, bbox)  # clip if necessary
        xmin = float(bbox[0][0])
        ymin = float(bbox[0][1])

    # find the actual dimensions, use to find scale factor
    height = bbox[1][1] - bbox[0][1]
    width = bbox[1][0] - bbox[0][0]

    if not shift_ratio:
        # to scale down from coordinate to pixels
        shift_ratio = float(px_width / width)

    def shft_coords(row):
        # parse through coords (nodes, or link) and adjust for pixel space
        return [(int((xy[0] - xmin) * shift_ratio),
                 int((height - xy[1] + ymin) * shift_ratio))
                for xy in row.coords]

    # insert new column with the shifted coordinates
    draw_coords = df.apply(lambda row: shft_coords(row), axis=1)
    if not (draw_coords.empty and df.empty):
        df = df.assign(draw_coords=draw_coords)

    return df, bbox, int(height * shift_ratio), int(width * shift_ratio), shift_ratio


def circle_bbox(coordinates, radius=5):
    """the bounding box of a circle given as centriod coordinate and radius"""

    x = coordinates[0]
    y = coordinates[1]
    r = radius

    return (x - r, y - r, x + r, y + r)


def clip_to_box(df, bbox):
    """clip a dataframe with a coords column to a bounding box"""

    def any_xy_in_box(row, bbox):
        # because im confused with list comprehensions rn
        return any([point_in_box(bbox, pt) for pt in row])

    coords = df.coords.tolist()
    result = [any_xy_in_box(p, bbox) for p in coords]
    return df.loc[result]


def angle_bw_points(xy1, xy2):
    dx, dy = (xy2[0] - xy1[0]), (xy2[1] - xy1[1])

    angle = (math.atan(float(dx) / float(dy)) * 180 / math.pi)
    if angle < 0:
        angle = 270 - angle
    else:
        angle = 90 - angle
    # angle in radians
    return angle


def midpoint(xy1, xy2):
    dx, dy = (xy2[0] + xy1[0]), (xy2[1] + xy1[1])
    midpt = (int(dx / 2), int(dy / 2.0))

    # angle in radians
    return midpt


def point_in_box(bbox, point):
    """check if a point falls with in a bounding box, bbox"""
    LB = bbox[0]
    RU = bbox[1]

    x = point[0]
    y = point[1]

    if x < LB[0] or x > RU[0]:
        return False
    elif y < LB[1] or y > RU[1]:
        return False
    else:
        return True


def length_bw_coords(upstreamXY, downstreamXY):
    # return the distance (units based on input) between two points
    x1 = float(upstreamXY[0])
    x2 = float(downstreamXY[0])
    y1 = float(upstreamXY[1])
    y2 = float(downstreamXY[1])

    return math.hypot(x2 - x1, y2 - y1)


def rotate_coord_about_point(xy, radians, origin=(0, 0)):
    """Rotate a point around a given origin
    https://gist.github.com/LyleScott/e36e08bfb23b1f87af68c9051f985302
    """
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy
