import math
from swmmio.graphics.constants import * #constants
from swmmio.graphics import config, options
from swmmio.graphics.utils import *
from PIL import Image, ImageDraw, ImageFont, ImageOps
# from swmmio.utils import swmm_utils as su
import os

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

def draw_parcel(parcel, draw):
	fill = gradient_color_red(parcel.HoursFlooded + 0.5, 0, 3)
	draw.polygon(parcel.draw_coords, fill=fill)

def annotate_streets(df, img, text_col):

	#confirm font file location
	if not os.path.exists(config.font_file):
		print 'Error loading defautl font. Check your config.font_file'
		return None

	unique_sts = df[text_col].unique()
	for street in unique_sts:
		draw_coords = df.loc[df.ST_NAME==street, 'draw_coords'].tolist()[0]
		coords = df.loc[df.ST_NAME==street, 'coords'].tolist()[0]
		font = ImageFont.truetype(config.font_file, int(25))
		imgTxt = Image.new('L', font.getsize(street))
		drawTxt = ImageDraw.Draw(imgTxt)
		drawTxt.text((0,0), street, font=font, fill=(10,10,12))
		angle = angle_bw_points(coords[0], coords[1])
		texrot = imgTxt.rotate(angle, expand=1)
		mpt = midpoint(draw_coords[0], draw_coords[1])
		img.paste(ImageOps.colorize(texrot, (0,0,0), (10,10,12)), mpt,  texrot)

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

def gradient_color_red(x, xmin, xmax, startCol=lightgrey):

	range = xmax - xmin

	rMin = startCol[0]
	gMax = startCol[1]
	bMax = startCol[2]

	rScale = (255 - rMin) / range
	gScale = (gMax) / range
	bScale = (bMax) / range
	x = min(x, xmax) #limit any vals to the prescribed max


	#print "range = " + str(range)
	#print "scale = " + str(scale)
	r = int(round(x*rScale + rMin ))
	g = int(round(gMax - x*gScale))
	b = int(round(bMax - x*bScale))

	return (r, g, b)


#LEGACY CODE !!!!!!
def _annotateMap (canvas, model, model2=None, currentTstr = None, options=None, results={}):

	#unpack the options
	nodeSymb = 		options['nodeSymb']
	conduitSymb = 	options['conduitSymb']
	basemap = 		options['basemap']
	parcelSymb = 	options['parcelSymb']
	traceUpNodes =	options['traceUpNodes']
	traceDnNodes =	options['traceDnNodes']

	modelSize = (canvas.im.getbbox()[2], canvas.im.getbbox()[3])

	#define main fonts
	fScale = 1 * modelSize[0] / 2048
	titleFont = ImageFont.truetype(fontFile, int(40 * fScale))
	font = ImageFont.truetype(fontFile, int(20 * fScale))

	#Buid the title and files list (handle 1 or two input models)
	#this is hideous, or elegant?
	files = title = results_string = symbology_string = annotationTxt = ""
	files = '\n'.join([m.rpt.path for m in filter(None, [model, model2])])
	title = ' to '.join([m.inp.name for m in filter(None, [model, model2])])
	symbology_string = ', '.join([s['title'] for s in filter(None, [nodeSymb, conduitSymb, parcelSymb])])
	title += "\n" + symbology_string

	#params_string = ''.join([" > " + str(round(s['threshold']*600)/10) + "min " for s in filter(None, [parcelSymb])])
	#build the title


	#collect results
	for result, value in results.iteritems():
		results_string += '\n' + result + ": " + str(value)

	#compile the annotation text
	if results:
		annotationTxt = results_string + "\n"
	annotationTxt += files


	annoHeight = canvas.textsize(annotationTxt, font)[1]

	canvas.text((10, 15), title, fill=black, font=titleFont)
	canvas.text((10, modelSize[1] - annoHeight - 10), annotationTxt, fill=black, font=font)


	if currentTstr:
		#timestamp in lower right corner
		annoHeight = canvas.textsize(currentTstr, font)[1]
		annoWidth = canvas.textsize(currentTstr, font)[0]
		canvas.text((modelSize[0] - annoWidth - 10, modelSize[1] - annoHeight - 10), currentTstr, fill=black, font=font)

	#add postprocessing timestamp
	timestamp = strftime("%b-%d-%Y %H:%M:%S")
	annoHeight = canvas.textsize(timestamp, font)[1]
	annoWidth = canvas.textsize(timestamp, font)[0]
	canvas.text((modelSize[0] - annoWidth - 10, annoHeight - 5), timestamp, fill=du.grey, font=font)




#end
