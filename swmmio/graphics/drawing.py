from swmmio.defs.constants import red, purple, lightblue, lightgreen, black, lightgrey, grey
from swmmio.defs.config import FONT_PATH
from swmmio.graphics.utils import circle_bbox, length_bw_coords, angle_bw_points, midpoint
from PIL import Image, ImageDraw, ImageFont, ImageOps
from time import strftime
import math
import os


# FUNCTIONS FOR COMPUTING THE VISUAL CHARACTERISTICS OF MODEL ELEMENTS
def node_draw_size(node):
    """given a row of a nodes() dataframe, return the size it should be drawn"""

    if 'draw_size' in node.axes[0]:
        # if this value has already been calculated
        return node.draw_size

    radius = 0  # aka don't show this node by default
    if 'HoursFlooded' in node and node.HoursFlooded >= 0.083:
        radius = node.HoursFlooded * 3
    return radius


def node_draw_color(node):
    """given a row of a nodes() dataframe, return the color it should be drawn"""

    if 'draw_color' in node.axes[0]:
        # if this value has already been calculated
        return node.draw_color

    color = '#d2d2e6'  # (210, 210, 230) #default color
    if 'HoursFlooded' in node and node.HoursFlooded >= 0.083:
        color = red
    return color


def conduit_draw_size(conduit):
    """return the draw size of a conduit"""

    if 'draw_size' in conduit.axes[0]:
        # if this value has already been calculated
        return conduit.draw_size

    draw_size = 1
    if 'MaxQPerc' in conduit and conduit.MaxQPerc >= 1:
        capacity = conduit.MaxQ / conduit.MaxQPerc
        stress = conduit.MaxQ / capacity
        fill = gradient_grey_red(conduit.MaxQ * 100, 0, capacity * 300)
        draw_size = int(round(math.pow(stress * 10, 0.8)))

    elif 'Geom1' in conduit:
        draw_size = conduit.Geom1

    return draw_size


def conduit_draw_color(conduit):
    """return the draw color of a conduit"""

    if 'draw_color' in conduit.axes[0]:
        # if this value has already been calculated
        return conduit.draw_color

    fill = '#787882'  # (120, 120, 130)
    if 'MaxQPerc' in conduit and conduit.MaxQPerc >= 1:
        capacity = conduit.MaxQ / conduit.MaxQPerc
        stress = conduit.MaxQ / capacity
        fill = gradient_grey_red(conduit.MaxQ * 100, 0, capacity * 300)
    return fill


def parcel_draw_color(parcel, style='risk'):
    if style == 'risk':
        fill = gradient_color_red(parcel.HoursFlooded + 0.5, 0, 3)
    if style == 'delta':
        fill = lightgrey  # default
        if parcel.Category == 'increased_flooding':
            # parcel previously flooded, now floods more
            fill = red

        if parcel.Category == 'new_flooding':
            # parcel previously did not flood, now floods in proposed conditions
            fill = purple

        if parcel.Category == 'decreased_flooding':
            # parcel flooding problem decreased
            fill = lightblue  # du.lightgrey

        if parcel.Category == 'eliminated_flooding':
            # parcel flooding problem eliminated
            fill = lightgreen

    return fill


# PIL DRAW METHODS APPLIED TO ImageDraw OBJECTS
def draw_node(node, draw):
    """draw a node to the given PIL ImageDraw object"""
    color = node_draw_color(node)
    radius = node_draw_size(node)
    draw.ellipse(circle_bbox(node.draw_coords[0], radius), fill=color)


def draw_conduit(conduit, draw):
    # default fill and size
    fill = conduit_draw_color(conduit)
    draw_size = int(conduit_draw_size(conduit))
    xys = conduit.draw_coords

	# draw that thing
    draw.line(xys, fill=fill, width=draw_size)
    if length_bw_coords(xys[0], xys[-1]) > draw_size * 0.75:
        # if length is long enough, add circles on the ends to smooth em out
		# this check avoids circles being drawn for tiny pipe segs
        draw.ellipse(circle_bbox(xys[0], draw_size * 0.5), fill=fill)
        draw.ellipse(circle_bbox(xys[1], draw_size * 0.5), fill=fill)


def draw_parcel_risk(parcel, draw):
    fill = gradient_color_red(parcel.HoursFlooded + 0.5, 0, 3)
    draw.polygon(parcel.draw_coords, fill=fill)


def draw_parcel_risk_delta(parcel, draw):
    if parcel.Category == 'increased_flooding':
        # parcel previously flooded, now floods more
        fill = red

    if parcel.Category == 'new_flooding':
        # parcel previously did not flood, now floods in proposed conditions
        fill = purple

    if parcel.Category == 'decreased_flooding':
        # parcel flooding problem decreased
        fill = lightblue  # du.lightgrey

    if parcel.Category == 'eliminated_flooding':
        # parcel flooding problem eliminated
        fill = lightgreen

    draw.polygon(parcel.draw_coords, fill=fill)


def annotate_streets(df, img, text_col):
    # confirm font file location
    if not os.path.exists(FONT_PATH):
        print('Error loading default font. Check your FONT_PATH')
        return None

    unique_sts = df[text_col].unique()
    for street in unique_sts:
        draw_coords = df.loc[df.ST_NAME == street, 'draw_coords'].tolist()[0]
        coords = df.loc[df.ST_NAME == street, 'coords'].tolist()[0]
        font = ImageFont.truetype(FONT_PATH, int(25))
        imgTxt = Image.new('L', font.getsize(street))
        drawTxt = ImageDraw.Draw(imgTxt)
        drawTxt.text((0, 0), street, font=font, fill=(10, 10, 12))
        angle = angle_bw_points(coords[0], coords[1])
        texrot = imgTxt.rotate(angle, expand=1)
        mpt = midpoint(draw_coords[0], draw_coords[1])
        img.paste(ImageOps.colorize(texrot, (0, 0, 0), (10, 10, 12)), mpt, texrot)


def gradient_grey_red(x, xmin, xmax):
    range = xmax - xmin

    rMin = 100
    bgMax = 100
    rScale = (255 - rMin) / range
    bgScale = (bgMax) / range
    x = min(x, xmax)  # limit any vals to the prescribed max

    # print "range = " + str(range)
    # print "scale = " + str(scale)
    r = int(round(x * rScale + rMin))
    g = int(round(bgMax - x * bgScale))
    b = int(round(bgMax - x * bgScale))

    return (r, g, b)


def line_size(q, exp=1):
    return int(round(math.pow(q, exp)))


def gradient_color_red(x, xmin, xmax, startCol=lightgrey):
    range = xmax - xmin

    rMin = startCol[0]
    gMax = startCol[1]
    bMax = startCol[2]

    rScale = (255 - rMin) / range
    gScale = (gMax) / range
    bScale = (bMax) / range
    x = min(x, xmax)  # limit any vals to the prescribed max

    # print "range = " + str(range)
    # print "scale = " + str(scale)
    r = int(round(x * rScale + rMin))
    g = int(round(gMax - x * gScale))
    b = int(round(bMax - x * bScale))

    return (r, g, b)


def annotate_title(title, draw):
    size = (draw.im.getbbox()[2], draw.im.getbbox()[3])
    scale = 1 * size[0] / 2048
    fnt = ImageFont.truetype(FONT_PATH, int(40 * scale))
    draw.text((10, 15), title, fill=black, font=fnt)


def annotate_timestamp(draw):
    size = (draw.im.getbbox()[2], draw.im.getbbox()[3])
    scale = 1 * size[0] / 2048
    fnt = ImageFont.truetype(FONT_PATH, int(20 * scale))

    timestamp = strftime("%b-%d-%Y %H:%M:%S")
    txt_height = draw.textsize(timestamp, fnt)[1]
    txt_width = draw.textsize(timestamp, fnt)[0]
    xy = (size[0] - txt_width - 10, 15)
    draw.text(xy, timestamp, fill=grey, font=fnt)


def annotate_details(txt, draw):
    size = (draw.im.getbbox()[2], draw.im.getbbox()[3])
    scale = 1 * size[0] / 2048
    fnt = ImageFont.truetype(FONT_PATH, int(20 * scale))

    txt_height = draw.textsize(txt, fnt)[1]

    draw.text((10, size[1] - txt_height - 10),
              txt, fill=black, font=fnt)

