#!/usr/bin/env python
#coding:utf-8

#Utilities and such for SWMMIO processing
import math
from PIL import Image, ImageDraw, ImageFont, ImageOps
from time import strftime
import os
import numpy as np
# import matplotlib.path as mplPath
# from matplotlib.transforms import BboxBase
import pickle
import json
#import arcpy
from swmmio.graphics import draw_utils as du

#contants
sPhilaBox = 	((2683629, 220000), (2700700, 231000))
sPhilaSq =		((2683629, 220000), (2700700, 237071))
sPhilaSm1 = 	((2689018, 224343), (2691881, 226266))
sPhilaSm2 = 	((2685990, 219185), (2692678, 223831))
sPhilaSm3 = 	((2688842, 220590), (2689957, 221240))
sPhilaSm4 = 	((2689615, 219776), (2691277, 220738))
sPhilaSm5 = 	((2690303, 220581), (2690636, 220772))
sm6 = 			((2692788, 225853), (2693684, 226477))
chris = 		((2688798, 221573), (2702834, 230620))
nolibbox= 		((2685646, 238860),	(2713597, 258218))
mckean = 		((2691080, 226162),	(2692236, 226938))
d68d70 = 		((2691647, 221073),	(2702592, 227171))
d70 = 			((2694096, 222741),	(2697575, 225059))
ritner_moyamen =((2693433, 223967),	(2694587, 224737))
morris_10th = 	((2693740, 227260),	(2694412, 227693))
morris_12th = 	((2693257, 227422),	(2693543, 227614))
study_area = 	((2682005, 219180), (2701713, 235555))
dickenson_7th = ((2695378, 227948), (2695723, 228179))
packer_18th = 	((2688448, 219932), (2691332, 221857))
moore_broad = 	((2689315, 225537), (2695020, 228592))
oregon_front =  ((2695959, 221033), (2701749, 224921))
mckean_2nd = 	((2696719, 224600), (2699010, 226150))

#COLOR DEFS
red = 		(250, 5, 5)
blue = 		(5, 5, 250)
shed_blue = (0,169,230)
white =		(250,250,240)
black = 	(0,3,18)
lightgrey = (235, 235, 225)
grey = 		(100,95,97)
park_green = (115, 178, 115)
green = 	(115, 220, 115)
water_grey = (130, 130, 130)
purple = (250, 0, 250)

#FONTS
fontFile = r"C:\Data\Code\Fonts\Raleway-Regular.ttf"

def getFeatureExtent(feature, where="SHEDNAME = 'D68-C1'", geodb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb'):

	import arcpy
	features = os.path.join(geodb, feature)
	for row in arcpy.da.SearchCursor(features, ["SHAPE@"], where_clause=where):

		#extent = row[0].extent
		#xy1,  xy2 =(extent.XMin, extent.YMin), (extent.XMax, extent.YMax)
		#return xy1, xy2
		#return row
		for part in row[0]:
			xy1,  xy2 =(part[0].X, part[0].Y), (part[1].X, part[1].Y)

			print xy1, xy2
			#print part

#FUNCTIONS
def traceFromNode(model, startNode, mode='up', stopnode=None):

	#nodes = model.organizeNodeData(bbox)['nodeDictionaries']
	#links = model.organizeConduitData(bbox)['conduitDictionaries']
	inp = model.inp
	conduitsDict = inp.createDictionary("[CONDUITS]")
	storagesDict = inp.createDictionary("[STORAGE]")
	junctionsDict = inp.createDictionary("[JUNCTIONS]")
	outfallsDict = inp.createDictionary("[OUTFALLS]")
	allNodesDict = merge_dicts(storagesDict, junctionsDict, outfallsDict)

	tracedNodes = [startNode] #include the starting node
	tracedConduits = []

	#recursive function to trace upstream
	def trace (nodeID):
		#print "tracing from {}".format(nodeID)
		for conduit, data in conduitsDict.iteritems():

			conduitUpNodeID = conduitDnNodeID = None
			if len(data) >= 1:
				#not sure why i need to do this check, but it prevents an indexing error on some
				conduitUpNodeID = data[0]
				conduitDnNodeID = data[1]

			if mode=='down' and conduitUpNodeID == nodeID and conduit not in tracedConduits:
				#conduit not in traced conduits to prevent duplicates for some reason
				#grab its dnstream node ID
				tracedConduits.append(conduit)
				tracedNodes.append(conduitDnNodeID)
				if stopnode and conduitDnNodeID == stopnode:
					break
				trace(conduitDnNodeID)

			if mode == 'up' and conduitDnNodeID == nodeID and conduit not in tracedConduits:
				#conduit not in traced conduits to prevent duplicates for some reason
				#this conduit is upstream of current node
				#grab its upstream node ID
				tracedConduits.append(conduit)
				tracedNodes.append(conduitUpNodeID)
				if stopnode and conduitUpNodeID == stopnode:
					break
				trace(conduitUpNodeID)

	#kickoff the trace
	print "Starting trace {0} from {1}".format(mode, startNode)
	trace(startNode)
	print "Traced {0} nodes from {1}".format(len(tracedNodes), startNode)
	return {'nodes':tracedNodes, 'conduits':tracedConduits}

def length_of_conduits(conduitsubset):

	#return the total length of conduits given a dictionary of Link objects
	l = 0
	for id, conduit in conduitsubset.iteritems():
		l +=conduit.length

	return l

def length_of_new_conduit(model1, model2):
    newconduitIDs = scomp.get_all_unmatched_inp_elements(model1, model2)['[CONDUITS]']['added']
    all_conduits = model2.organizeConduitData()['conduit_objects']
    l = 0
    for condID in newconduitIDs:
        l += all_conduits[condID].length

    return l



def pointIsInBox (bbox, point):

		#pass a lower left (origin) and upper right tuple representing a box,
		#and a tuple point to be tested

		LB = bbox[0]
		RU = bbox[1]

		x = point[0]
		y = point[1]

		if x < LB[0] or x >  RU[0]:
			return False
		elif y < LB[1] or y > RU[1]:
			return False
		else:
			return True

def pipeLengthPlanView(upstreamXY, downstreamXY):

	#return the distance (units based on input) between two points
	x1 = float(upstreamXY[0])
	x2 = float(downstreamXY[0])
	y1 = float(upstreamXY[1])
	y2 = float(downstreamXY[1])

	return math.hypot(x2 - x1, y2 - y1)
def pipeProfileLengthTransform(planLength, upstreamEl, downstreamEl, xTrans, yTrans):

	#tranform a pipe legth in x and y direction via its components

	ycomponent = upstreamEl - downstreamEl
	newXComponent = planLength * xTrans
	newYComponent = ycomponent * yTrans

	return math.hypot(newXComponent, newYComponent)
def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
		if dictionary:
			result.update(dictionary)
    return result


def elementChange(elementData, parameter='maxflow'):

	#with a joined dictionary item, returns change from existing to proposed

	proposedVal = elementData['proposed'].get(parameter, 0.0)
	existingVal = elementData['existing'].get(parameter, 0.0)

	return proposedVal - existingVal

def subsetConduitsInBoundingBox(conduitsDict, boundingBox):

	newDict = {}
	for conduit, conduitData in conduitsDict.iteritems():
		if 'existing' and 'proposed' in conduitData:
			#then we have a "compare" dictionary, must drill down further, use proposed
			coordPair = conduitData['proposed']['coordinates']
		else:
			coordPair = conduitData['coordinates']

		if boundingBox and (not pointIsInBox(boundingBox, coordPair[0]) or not pointIsInBox(boundingBox, coordPair[1])):
			#ship conduits who are not within a given boudning box
			continue

		newDict.update({conduit:conduitData})

	return 	newDict

def subsetElements(model, type='node', key='floodDuration', min=0.083, max=99999, bbox=None, pair_only=False):
	#return a subset of a dictionary of swmm elements based on a value

	if type=='node':
		elems = model.organizeNodeData(bbox)['node_objects']

	elif type=='conduit':
		elems = model.organizeConduitData(bbox)['conduit_objects']
	else: return []

	if pair_only:
		#only return the element and the value being filtered on
		subset = {k:v.flood_duration for (k,v) in elems.items() if v.flood_duration >= min }
	else:
		subset = {k:v for (k,v) in elems.items() if v.flood_duration >= min }

	return subset

def shape2Pixels(feature, cols = ["OBJECTID", "SHAPE@"],  where="SHEDNAME = 'D68-C1'", shiftRatio=None, targetImgW=1024, bbox=None, gdb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb'):

	#take data from a geodatabase and organize in a dictionary with coordinates and draw_coordinates
	import arcpy
	features = os.path.join(gdb, feature)
	geometryDicts = {}
	for row in arcpy.da.SearchCursor(features, cols, where_clause=where):

		try:
			#detect what shape type this is
			geomType = row[1].type
			jsonkey = 'rings' #default for polygons, for accessing polygon vert coords
			if geomType == 'polyline':
				jsonkey = 'paths'


			geometrySections = json.loads(row[1].JSON)[jsonkey] # an array of parts
			#geomArr = json.loads(row[1].JSON)[jsonkey][0] #(assumes poly has one ring)

			for i, section in enumerate(geometrySections):

				#check if part of geometry is within the bbox, skip if not
				if bbox and len ( [x for x in section if pointIsInBox(bbox, x)] ) == 0:
					continue #skip this section if none of it is within the bounding box

				id = str(row[0])
				if len(geometrySections) > 1:
					id = str(row[0]) + "." + str(i)

				geometryDict = {'coordinates':section, 'geomType':geomType}
				#geometryDicts.update({id:{'coordinates':geomArr}})

				#add any other optional cols, starting at 3rd col item
				for j, col in enumerate(cols[2:]):
					col_data = str(row[j+2])
					geometryDict.update({col:col_data})

				geometryDicts.update({id:geometryDict})

		except:
			"prob with ", row[0]

	#find mins and maxs
	maxX = maxY = 0.0 #determine current width prior to ratio transform
	minX = minY = 99999999.0
	if not bbox:
		#review all points of the polygon to find min of all points
		for geom, geomData in geometryDicts.iteritems():
			for seg in geomData['coordinates']:
				minX = min(minX, seg[0])
				minY = min(minY, seg[1])
				maxX = max(maxX, seg[0])
				maxY = max(maxY, seg[1])
		bbox = [(minX, minY),(maxX, maxY)]

	#can probably get rid of these, if polygons are always secondary to the model drawing stuff (in which these params should be defined)
	height = float(bbox[1][1]) - float(bbox[0][1])
	width = float(bbox[1][0]) - float(bbox[0][0])
	shiftRatio = float(targetImgW / width) # to scale down from coordinate to pixels

	for geom, geomData in geometryDicts.iteritems():
		drawCoords = []
		for coord in geomData['coordinates']:

			drawCoord = coordToDrawCoord(coord, bbox, shiftRatio)
			drawCoords.append(drawCoord)
		geomData.update({'draw_coordinates':drawCoords})

	imgSize = (width*shiftRatio, height*shiftRatio)
	imgSize = [int(math.ceil(x)) for x in imgSize] #convert to ints

	polyImgDict = {'geometryDicts':geometryDicts, 'imgSize':imgSize , 'boundingBox': bbox, 'shiftRatio':shiftRatio }

	return polyImgDict

def pixel_coords_from_irl_coords(df, targetImgW=1024,
									bbox=None, shiftRatio=None):

	"""
	given a dataframe with element id (as index) and X1, Y1 columns (and
	optionally X2, Y2 columns), return a dataframe with the coords as pixel
	locations based on the targetImgW.
	"""
	xmin, ymin, xmax, ymax = (df.X.min(), df.Y.min(),df.X.max(), df.Y.max())
	if not bbox:
		#start by determining the max and min coordinates in the whole model
		bbox = [(xmin, ymin),(xmax, ymax)]

	#find the actual dimensions, use to find scale factor
	height = bbox[1][1] - bbox[0][1]
	width = bbox[1][0] - bbox[0][0]
	if not shiftRatio:
		# to scale down from coordinate to pixels
		shiftRatio = float(targetImgW / width)

	def shft_x_crds(row):
		return (row.X - xmin) * shiftRatio

	def shft_y_crds(row):
		return (height - row.Y + ymin) * shiftRatio

	#copy the given df and insert new columns with the shifted coordinates
	df_shft = df[:]
	df_shft.insert(0, 'X_px', df_shft.apply(lambda row: shft_x_crds(row), axis = 1))
	df_shft.insert(0, 'Y_px', df_shft.apply(lambda row: shft_y_crds(row), axis = 1))
	# df_shft.loc[:,'Y_px'] = df_shft.apply(lambda row: shft_y_crds(row), axis = 1)

	return df_shft

def convertCoordinatesToPixels(element_objs, targetImgW=1024, bbox=None, shiftRatio=None):

	"""
	adds a dictionary to each conduit or node dict called 'draw_coordinates'
	which is a two part tuple, xy1, xy2
	"""

	if not bbox:
		#start by determining the max and min coordinates in the whole model
		maxX = maxY = 0.0 #determine current width prior to ratio transform
		minX = minY = 99999999
		for id, element in element_objs.iteritems():

			coordPair = element.coordinates

			if type(coordPair[0]) is list:
				#loop for elements with multiple coordinates (lines)
				#each coordinate is a list
				for coord in coordPair:
					minX = min(minX, coord[0])
					minY = min(minY, coord[1])
					maxX = max(maxX, coord[0])
					maxY = max(maxY, coord[1])

			else:
				minX = min(minX, coordPair[0])
				minY = min(minY, coordPair[1])
				maxX = max(maxX, coordPair[0])
				maxY = max(maxY, coordPair[1])

		bbox = [(minX, minY),(maxX, maxY)]

	height = float(bbox[1][1]) - float(bbox[0][1])
	width = float(bbox[1][0]) - float(bbox[0][0])
	if not shiftRatio:
		shiftRatio = float(targetImgW / width) # to scale down from coordinate to pixels

	for id, element in element_objs.iteritems():

		coordPair = element.coordinates

		drawcoords = []
		if type(coordPair[0]) is list:
			#loop for elements with multiple coordinates (lines)
			#each coordinate is a list
			for coord in coordPair:
				xy = coordToDrawCoord(coord, bbox, shiftRatio)
				drawcoords.append(xy)
		else:
			#zeroth index is not list, therefore coordPair is a single coord
			drawcoords = coordToDrawCoord(coordPair, bbox, shiftRatio)

		element.draw_coordinates = drawcoords

	imgSize = (width*shiftRatio, height*shiftRatio)
	imgSize = [int(math.ceil(x)) for x in imgSize] #convert to ints
	modelSizeDict = {'imgSize':imgSize, 'boundingBox': bbox, 'shiftRatio':shiftRatio }
	return modelSizeDict

def coordToDrawCoord(coordinates, bbox=None, shiftRatio=None, shiftRatioY=None, width=None, height=None):
	"""
	convert single coordinate pair into the drawing space (pixels rather than
	cartesian coords) given a cartesian bbox and shiftRatio
	"""

	#transform coords by normalizing by the mins, apply a ratio to
	#produce the desired width pixel space
	minX = minY = 0
	if bbox:
		minX = float(bbox[0][0])
		minY = float(bbox[0][1])
		maxX = float(bbox[1][0])
		maxY = float(bbox[1][1])

		height = maxY - minY
		width = maxX - minX

	if not shiftRatioY:
		shiftRatioY = shiftRatio
	x =  (coordinates[0] - minX) * shiftRatio
	y =  (height - coordinates[1] + minY) * shiftRatioY #subtract from height because PIL origin is in top right

	return (x,y)

def circleBBox(coordinates, radius):
	#returns the bounding box of a circle given as centriod coordinate and radius
	x = coordinates[0] #this indexing is because other elements haev more than on coordinate (ulgy pls fix)
	y = coordinates[1]
	r = radius

	return (x-r, y-r, x+r, y+r)


def drawNode(node, draw, options, rpt=None, dTime=None, xplier=1):

	color = (210, 210, 230) #default color
	radius = 0 #aka don't show this node by default
	outlineColor = None
	xy = node.draw_coordinates #(node.X_px, node.Y_px)
	threshold = options['threshold']
	type = options['type']
	if dTime:

		data = rpt.returnDataAtDTime(node.id, dTime, sectionTitle="Node Results")
		q = abs(float(data[2])) #absolute val because backflow
		floodingQ = float(data[3])
		HGL = float(data[5])

		if type=='flood':

			#node params
			if floodingQ > 1:
				radius = q/2
				color = red #greenRedGradient(HGLup, 0, 15) #color

	elif node.is_delta:
		#we're dealing with "compare" object
		#floodDurationChange = elementChange(node, parameter='floodDuration')

		if node.flood_duration > 0 :
			#Flood duration increases
			radius = node.flood_duration*20
			color = red

		#if nodeData['existing'].get('floodDuration', 0) == 0 and nodeData['proposed'].get('floodDuration', 0) > 0:
		if node.delta_type == 'new_flooding':
			#new flooding found
			radius = node.flood_duration*20
			color = purple #purple
			outlineColor = (90, 90, 90)

	else:
		floodDuration = node.flood_duration
		maxDepth = node.maxDepth
		maxHGL = node.maxHGL

		if type == 'flood':
			#if floodDuration > 0.08333:
			if floodDuration >= threshold:
				radius = floodDuration*3
				color = red

		if type == 'flood_color':
			radius = 3
			if floodDuration >= threshold:
				yellow = (221, 220, 0)
				color = du.col2RedGradient(floodDuration, 0, 1, startCol=yellow) #options['fill'](floodDuration, 0, 1+threshold)
			else:

				radius = 1

	radius *= xplier
	draw.ellipse(circleBBox(xy, radius), fill =color, outline=outlineColor)

def drawConduit(conduit, draw, options, rpt=None, dTime = None, xplier = 1, highlighted=None):

	#Method for drawing (in plan view) a single conduit, given its RPT results

	#default fill and size
	fill = (120, 120, 130)
	drawSize = 1
	should_draw = True #boolean that can prevent a draw based on params
	coordPair = conduit.draw_coordinates
	type = options['type']
	#general method for drawing one conduit
	if rpt:
		#if an RPT is supplied, collect the summary data
		maxQPercent = conduit.maxQpercent
		q =  conduit.maxflow

		if maxQPercent !=0:
			capacity = q / maxQPercent
		else:
			capacity = 1
		stress = q / capacity

		if dTime:
			#if a datetime is provided, grab the specif flow data at this time
			data = rpt.returnDataAtDTime(conduit.id, dTime) #this is slow
			q = abs(float(data[2])) #absolute val because backflow
			stress = q / capacity    #how taxed is the pipe

		remaining_capacity = capacity-q
		#=================================
		#draw the conduit type as specifed
		#=================================
		if type == "flow":

			fill = options['fill']
			drawSize = options['draw_size'](q, options['exp'])

		if type == "flow_stress":

			fill = options['fill'](q*100, 0, capacity*175)
			drawSize = options['draw_size'](q, options['exp']) #int(round(math.pow(q, 0.67)))

		elif type == "stress":

			if maxQPercent >= 1:
				fill = options['fill'](q*100, 0, capacity*300) #greenRedGradient(q*100, 0, capacity*300)
				drawSize = options['draw_size'](stress*options['xplier'], options['exp']) #int(round(math.pow(stress*4, 1)))

		elif type == "capacity_remaining":

			if remaining_capacity > 0:
				fill = (0, 100, 255)
				drawSize = int( round( math.pow(remaining_capacity, 0.8)))



			#drawSize = int( round(max(remaining_capacity, 1)*xplier) )

	elif conduit.is_delta:
		#we're dealing with "compare" dictionary
		qChange = 	conduit.maxflow #elementChange(conduitData, parameter='maxflow')
		maxQperc = 	conduit.maxQpercent #elementChange(conduitData, parameter='maxQpercent')

		#default draw behavoir = draw grey lines proportional to geom1
		drawSize = min(7, conduit.geom1*0.7)
		fill = du.mediumgrey
		# #FIRST DRAW NEW OR CHANGED CONDUITS IN A CLEAR WAY
		# if conduit.lifecycle == 'new':
		# 	fill = blue
		# if conduit.lifecycle == 'changed':
		# 	fill = green #blue
			#drawSize = min(10, conduit.geom1)

		#IF THE CONDUITS IS 'EXISTING', DISPLAY SYMBOLOGY ACCORDINGLY (how things changed, etc)
		if conduit.lifecycle == 'existing':

			if type == 'proposed_simple':
				#drawSize = 0 #don't draw, only print the proposed infrastructure
				#fill = red
				#should_draw = False
				pass
			if type == 'compare_flow':
				drawSize = options['draw_size'](abs(qChange*options['xplier']), options['exp'])
				if qChange > 0:
					fill = du.greyRedGradient(qChange+15, 0, 20)
					#drawSize = int(round(math.pow(qChange, 0.67)))

				if qChange <= 0:
					fill = du.greyGreenGradient(abs(qChange)+15, 0, 20)
					#drawSize = int(round(math.pow(abs(qChange), 0.67)))

			if type == 'compare_hgl':

				avgHGL = (conduit.maxHGLUpstream + conduit.maxHGLDownstream) / 2.0
				drawSize = options['draw_size'](abs(avgHGL*options['xplier']), options['exp'])
				if avgHGL > 0:
					fill = du.red #du.greyRedGradient(avgHGL+15, 0, 20)
					#drawSize = int(round(math.pow(avgHGL, 1)))

				if avgHGL <= 0:
					fill = du.green_bright #du.greyGreenGradient(abs(avgHGL)+15, 0, 20)
					#drawSize = int(round(math.pow(avgHGL, 1)))


	#if highlighted list is provided, overide any symbology for the highlighted conduits
	if highlighted and conduit.id in highlighted:
		fill = blue
		drawSize = 3
	#FIRST DRAW NEW OR CHANGED CONDUITS IN A CLEAR WAY
	if conduit.lifecycle == 'new':
		fill = blue
	if conduit.lifecycle == 'changed':
		fill = green #blue
	drawSize = int(drawSize*xplier)


	if should_draw:
		#draw that thing
		draw.line(coordPair, fill = fill, width = drawSize)
		if pipeLengthPlanView(coordPair[0], coordPair[1]) > drawSize*0.75:
			#if length is long enough, add circles on the ends to smooth em out
			#this check avoids circles being drawn for tiny pipe segs
			draw.ellipse(du.circleBBox(coordPair[0], drawSize*0.5), fill =fill)
			draw.ellipse(du.circleBBox(coordPair[1], drawSize*0.5), fill =fill)

def angleBetweenPoint(xy1, xy2):
	dx, dy = (xy2[0] - xy1[0]), (xy2[1] - xy1[1])

	angle = (math.atan(float(dx)/float(dy)) * 180/math.pi )
	if angle < 0:
		angle = 270 - angle
	else:
		angle = 90 - angle
	#angle in radians
	return angle

def midPoint(xy1, xy2):

	dx, dy = (xy2[0] + xy1[0]), (xy2[1] + xy1[1])
	midpt = ( int(dx/2), int(dy/2.0) )

	#angle in radians
	return midpt

def annotateLine (img, dataDict, fontScale=1, annoKey='name', labeled = None):

	txt = dataDict[annoKey]

	if not txt in labeled:
		#do not repeat labels
		font = ImageFont.truetype(fontFile, int(25 * fontScale))
		imgTxt = Image.new('L', font.getsize(txt))
		drawTxt = ImageDraw.Draw(imgTxt)
		drawTxt.text((0,0), txt, font=font, fill=(10,10,12))

		coords = dataDict['coordinates']
		drawCoord = dataDict['draw_coordinates']
		angle = angleBetweenPoint(coords[0], coords[1])
		texRot = imgTxt.rotate(angle, expand=1)
		#canvas.paste( ImageOps.colorize(texRot, (0,0,0), (255,255,84)), (242,60),  texRot)

		midpoint = midPoint(drawCoord[0], drawCoord[1])
		#img.paste(texRot , midpoint,  texRot)
		img.paste(ImageOps.colorize(texRot, (0,0,0), (10,10,12)), midpoint,  texRot)
		labeled.append(txt) #keep tracj of whats been labeled



#def drawAnnotation (canvas, inp, rpt=None, imgWidth=1024, title=None, currentTstr = None, description = None,
#					objects = None, symbologyType=None, fill=(50,50,50), xplier=None):
def annotateMap (canvas, model, model2=None, currentTstr = None, options=None, results={}):

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
