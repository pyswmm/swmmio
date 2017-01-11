import math
from swmmio.graphics import * #constants
from swmmio.graphics.utils import circle_bbox, length_bw_coords

def draw_node(node, draw):
	color = (210, 210, 230) #default color
	radius = 0 #aka don't show this node by default
	if node.HoursFlooded >= 0.083:
		radius = node.HoursFlooded*3
		color = red

	draw.ellipse(circle_bbox(node.draw_coords[0], radius), fill = color)

def draw_conduit(conduit, draw):
    #default fill and size
    fill = (120, 120, 130)
    draw_size = 1
    xys = conduit.draw_coords

    if conduit.MaxQPerc >= 1:
        capacity = conduit.MaxQ / conduit.MaxQPerc
        stress = conduit.MaxQ / capacity
        fill = gradient_grey_red(conduit.MaxQ*100, 0, capacity*300)
        draw_size = int(round(math.pow(stress*10, 0.8)))


    #draw that thing
    draw.line(xys, fill = fill, width = draw_size)
    if length_bw_coords(xys[0], xys[-1]) > draw_size*0.75:
        #if length is long enough, add circles on the ends to smooth em out
        #this check avoids circles being drawn for tiny pipe segs
        draw.ellipse(circle_bbox(xys[0], draw_size*0.5), fill = fill)
        draw.ellipse(circle_bbox(xys[1], draw_size*0.5), fill = fill)


def gradient_grey_red(x, xmin, xmax):

	range = xmax - xmin

	rMin = 100
	bgMax = 100
	rScale = (255 - rMin) / range
	bgScale = (bgMax) / range
	x = min(x, xmax) #limit any vals to the prescribed max


	#print "range = " + str(range)
	#print "scale = " + str(scale)
	r = int(round(x*rScale + rMin ))
	g = int(round(bgMax - x*bgScale))
	b = int(round(bgMax - x*bgScale))

	return (r, g, b)

def line_size(q, exp=1):
	return int(round(math.pow(q, exp)))
