#Utilities and such for SWMMIO processing
import math
from PIL import Image, ImageDraw, ImageFont
import os
import webbrowser

#contants
sPhilaBox = 	((2683629, 220000), (2700700, 231000))
sPhilaSq =		((2683629, 220000), (2700700, 237071))
sPhilaSm1 = 	((2689018, 224343), (2691881, 226266))
sPhilaSm2 = 	((2685990, 219185), (2692678, 223831))
sPhilaSm3 = 	((2688842, 220590), (2689957, 221240))
sPhilaSm4 = 	((2689615, 219776), (2691277, 220738))
sPhilaSm5 = 	((2690303, 220581), (2690636, 220772))
d68	=			((2688936.500050336, 224270.35926787555), (2700921.2498855004, 230259.68740142623))
chris = 		((2688798, 221573), (2702834, 230620))
tinsq  = 		((2693388.74699889, 234280.936873894), (2693488.74712697, 234380.937001977))
rect = 			((2693377.03901705, 235014.632584977), (2694377.03898555, 235314.632641144))
gtownBox = 		((2688500, 263811), (2698000, 273000))
gtownSmall = 	((2693955.50306502, 263855.872771832), (2696255.85028725, 265418.372771829))


def getFeatureExtent(feature, where="SHEDNAME = 'D68-C1'", geodb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb'):
	
	import arcpy
	features = os.path.join(geodb, feature)
	for row in arcpy.da.SearchCursor(features, ["SHAPE@"], where_clause=where):
		
		#extent = row[0].extent
		#xy1,  xy2 =(extent.XMin, extent.YMin), (extent.XMax, extent.YMax)
		#return xy1, xy2
		return row
		for part in row[0]:
			xy1,  xy2 =(part[0].X, part[0].Y), (part[1].X, part[1].Y)
			
			print xy1, xy2
			#print part

	
#FUNCTIONS
def traceUpstream(model, startNode):
	
	#nodes = model.organizeNodeData(bbox)['nodeDictionaries']
	#links = model.organizeConduitData(bbox)['conduitDictionaries']
	inp = model.inp
	conduitsDict = inp.createDictionary("[CONDUITS]")
	storagesDict = inp.createDictionary("[STORAGE]")
	junctionsDict = inp.createDictionary("[JUNCTIONS]")
	outfallsDict = inp.createDictionary("[OUTFALLS]")
	allNodesDict = merge_dicts(storagesDict, junctionsDict, outfallsDict)
	
	upstreamNodes = []
	upstreamConduits = []
	
	#recursive function to trace upstream
	def traceUp (nodeID):
		#print "tracing from {}".format(nodeID)
		for conduit, data in conduitsDict.iteritems():
			
			conduitDnNodeID = None
			if len(data) >= 1:
				#not sure why i need to do this check, but it prevents an indexing error on some
				conduitUpNodeID = data[0]
				conduitDnNodeID = data[1]
			
			if conduitDnNodeID == nodeID:
				#this conduit is upstream of startNode
				#grab its upstream node ID
				upstreamConduits.append(conduit)
				upstreamNodes.append(conduitUpNodeID)
				traceUp(conduitUpNodeID)
	
	#kickoff the trace
	print "Starting trace from {}".format(startNode)
	traceUp(startNode)
	
	return {'upstreamNodes':upstreamNodes, 'upstreamConduits':upstreamConduits}

def traceFromNode(model, startNode, mode='up'):
	
	#nodes = model.organizeNodeData(bbox)['nodeDictionaries']
	#links = model.organizeConduitData(bbox)['conduitDictionaries']
	inp = model.inp
	conduitsDict = inp.createDictionary("[CONDUITS]")
	storagesDict = inp.createDictionary("[STORAGE]")
	junctionsDict = inp.createDictionary("[JUNCTIONS]")
	outfallsDict = inp.createDictionary("[OUTFALLS]")
	allNodesDict = merge_dicts(storagesDict, junctionsDict, outfallsDict)
	
	tracedNodes = []
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
				trace(conduitDnNodeID)
			
			if mode == 'up' and conduitDnNodeID == nodeID and conduit not in tracedConduits:
				#conduit not in traced conduits to prevent duplicates for some reason
				#this conduit is upstream of current node
				#grab its upstream node ID
				tracedConduits.append(conduit)
				tracedNodes.append(conduitUpNodeID)
				trace(conduitUpNodeID)
			
	#kickoff the trace
	print "Starting trace {0} from {1}".format(mode, startNode)
	trace(startNode)
	
	return {'nodes':tracedNodes, 'conduits':tracedConduits}

def randAlphaNum(n=6):
	import random
	chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
	return ''.join(random.choice(chars) for i in range(n))
	
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
def getX2(y1, y2, length, x1=0):
	
	#return the x2 coordinate given y1, y2, the line segment length, and x0
	
	a = y2 - y1
	c = length
	return math.sqrt(c*c - a*a) + x1
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
def greenRedGradient(x, xmin, xmax):
	
	range = xmax - xmin
	scale = 255 / range
	
	x = min(x, xmax) #limit any vals to the prescribed max
	
	#print "range = " + str(range)
	#print "scale = " + str(scale)
	r = int(round(x*scale))
	g = int(round(255 - x*scale))
	b = 0
	
	return (r, g, b)
def greyRedGradient(x, xmin, xmax):
	
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
def greyGreenGradient(x, xmin, xmax):
	
	range = xmax - xmin
	
	gMin = 100
	rbMax = 100
	gScale = (255 - gMin) / range
	rbScale = (rbMax) / range
	x = min(x, xmax) #limit any vals to the prescribed max
	
	
	#print "range = " + str(range)
	#print "scale = " + str(scale)
	r = int(round(rbMax - x*rbScale))
	g = int(round(x*rbScale + gMin ))
	b = int(round(rbMax - x*rbScale))
	
	return (r, g, b)
def blueRedGradient(x, xmin, xmax):
	
	range = xmax - xmin
	scale = 255 / range
	
	x = min(x, xmax) #limit any vals to the prescribed max
	
	#print "range = " + str(range)
	#print "scale = " + str(scale)
	r = int(round(x*scale))
	g = 0
	b = int(round(255 - x*scale))
	
	return (r, g, b)

def elementChange(elementData, parameter='maxflow'):
	
	#with a joined dictionary item, returns change from existing to proposed
	
	proposedVal = elementData['proposed'].get(parameter, 0.0)
	existingVal = elementData['existing'].get(parameter, 0.0)
	
	return proposedVal - existingVal

	#drawing UTILS

	
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

def convertPolygonToPixels(feature, where="SHEDNAME = 'D68-C1'", shiftRatio=None, targetImgW=1024, bbox=None, geodb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb'):
	
	import json
	
	import arcpy
	features = os.path.join(geodb, feature)
	polygons = {}
	for row in arcpy.da.SearchCursor(features, ["OBJECTID", "SHAPE@"], where_clause=where):
		try:
			polyArr = json.loads(row[1].JSON)['rings'][0] #(assumes poly has one ring)
			id = str(row[0])
			polygons.update({id:{'coordinates':polyArr}})
		except:
			"prob with ", id
	
	#find mins and maxs
	maxX = maxY = 0.0 #determine current width prior to ratio transform
	minX = minY = 99999999.0
	if not bbox:
		#review all points of the polygon to find min of all points
		for poly, polyData in polygons.iteritems():
			for seg in polyData['coordinates']:
				minX = min(minX, seg[0])
				minY = min(minY, seg[1])
				maxX = max(maxX, seg[0])
				maxY = max(maxY, seg[1])
		bbox = [(minX, minY),(maxX, maxY)]
	
	#can probably get rid of these, if polygons are always secondary to the model drawing stuff (in which these params should be defined)
	height = float(bbox[1][1]) - float(bbox[0][1])
	width = float(bbox[1][0]) - float(bbox[0][0])
	shiftRatio = float(targetImgW / width) # to scale down from coordinate to pixels
	
	for poly, polyData in polygons.iteritems():
		drawCoords = []
		for coord in polyData['coordinates']:
			
			drawCoord = coordToDrawCoord(coord, bbox, shiftRatio)
			drawCoords.append(drawCoord)
		polyData.update({'draw_coordinates':drawCoords})
	
	imgSize = (width*shiftRatio, height*shiftRatio)
	imgSize = [int(math.ceil(x)) for x in imgSize] #convert to ints
	
	polyImgDict = {'polygons':polygons, 'imgSize':imgSize , 'boundingBox': bbox, 'shiftRatio':shiftRatio }
	
	return polyImgDict
	
def convertCoordinatesToPixels(elementDict, targetImgW=1024, bbox=None, shiftRatio=None):
	
	#adds a dictionary to each conduit or node dict called
	#'draw_coordinates' which is a two part tuple, xy1, xy2
	
	if not bbox:
		#start by determining the max and min coordinates in the whole model
		maxX = maxY = 0.0 #determine current width prior to ratio transform
		minX = minY = 99999999
		for element, elementData in elementDict.iteritems():
			
			if 'existing' and 'proposed' in elementData:
				#then we have a "compare" dictionary, must drill down further, use proposed
				coordPair = elementData['proposed']['coordinates']
			else: 
				coordPair = elementData['coordinates']
			
			
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
	
	print "reg shift ratio = ", shiftRatio
	for element, elementData in elementDict.iteritems():
		
		if 'existing' and 'proposed' in elementData:
			#then we have a "compare" dictionary, must drill down further, use proposed
			coordPair = elementData['proposed']['coordinates']
		else: 
			coordPair = elementData['coordinates']
		
		
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
			
		elementData.update({'draw_coordinates':drawcoords})
	
	imgSize = (width*shiftRatio, height*shiftRatio)
	imgSize = [int(math.ceil(x)) for x in imgSize] #convert to ints
	modelSizeDict = {'imgSize':imgSize, 'boundingBox': bbox, 'shiftRatio':shiftRatio }
	return modelSizeDict

def coordToDrawCoord(coordinates, bbox, shiftRatio):
	
	#convert single coordinate pair into the drawing space (pixels rather than cartesian coords)
	#given a cartesian bbox and shiftRatio
	
	#transform coords by normalizing by the mins, apply a ratio to 
	#produce the desired width pixel space 
	
	minX = float(bbox[0][0])
	minY = float(bbox[0][1])
	maxX = float(bbox[1][0])
	maxY = float(bbox[1][1])
		
	height = maxY - minY
	width = maxX - minX
	
	x =  (coordinates[0] - minX) * shiftRatio
	y =  (height - coordinates[1] + minY) * shiftRatio #subtract from height because PIL origin is in top right	
	
	return (x,y)

	
def circleBBox(coordinates, radius):
	#returns the bounding box of a circle given as centriod coordinate and radius
	x = coordinates[0] #this indexing is because other elements haev more than on coordinate (ulgy pls fix)
	y = coordinates[1]
	r = radius
	
	return (x-r, y-r, x+r, y+r)

def drawNode(id, nodeData, draw, rpt=None, dTime=None, type='flood', xplier=1):
	
	color = (210, 210, 230) #default color 
	radius = 0 #aka don't show this node by default
	outlineColor = None 
	xy = nodeData['draw_coordinates']
	
	if dTime:
		
		data = rpt.returnDataAtDTime(id, dTime, sectionTitle="Node Results") 
		q = abs(float(data[2])) #absolute val because backflow
		floodingQ = float(data[3])
		HGL = float(data[5]) 
		
		if type=='flood':
			
			#node params
			if floodingQ > 1:
				radius = q/2 
				color = red #greenRedGradient(HGLup, 0, 15) #color
	
	elif 'existing' and 'proposed' in nodeData:
		#we're dealing with "compare" dictionary
		floodDurationChange = elementChange(nodeData, parameter='floodDuration')
		
		if floodDurationChange > 0 :
			#Flood duration increase
			radius = floodDurationChange*20
			color = red 
			
		if nodeData['existing'].get('floodDuration', 0) == 0 and nodeData['proposed'].get('floodDuration', 0) > 0:
			#new flooding found
			radius = floodDurationChange*20
			color = (250, 0, 250) #purple	
			outlineColor = (90, 90, 90)
		
	else:
		floodDuration = nodeData.get('floodDuration', 0)
		maxDepth = nodeData['maxDepth']
		maxHGL = nodeData['maxHGL']
	
		if type == 'flood':
			if floodDuration > 0.08333:
				radius = floodDuration*3
				color = red
	
	
	
	radius *= xplier
	draw.ellipse(circleBBox(xy, radius), fill =color, outline=outlineColor)
	
	
def drawConduit(id, conduitData, canvas, rpt=None, dTime = None, xplier = 1, highlighted=None, type="flow"):
	
	#Method for drawing (in plan view) a single conduit, given its RPT results 
	
	#default fill and size
	fill = (210, 210, 230)
	drawSize = 1
	coordPair = conduitData['draw_coordinates']
	
	#general method for drawing one conduit
	if rpt:
		#if an RPT is supplied, collect the summary data
		maxQPercent = conduitData['maxQpercent']
		q =  conduitData['maxflow']
		
		
		if maxQPercent !=0:
			capacity = q / maxQPercent
		else:
			capacity = 1
		stress = q / capacity
		
		if dTime:
			#if a datetime is provided, grab the specif flow data at this time
			data = rpt.returnDataAtDTime(id, dTime) #this is slow
			q = abs(float(data[2])) #absolute val because backflow	
			stress = q / capacity    #how taxed is the pipe
		
		#=================================
		#draw the conduit type as specifed
		#=================================		
		if type == "flow":
	
			fill = blue
			drawSize = int(round(math.pow(q, 0.67)))
		
		if type == "flow_stress":
	
			fill = greenRedGradient(q*100, 0, capacity*175)
			drawSize = int(round(math.pow(q, 0.67)))
		
		elif type == "flow_proposed":
			
			if highlighted and id in highlighted:
				fill = blueRedGradient(q*100, 0, capacity*175)
				drawSize = int(round(math.pow(q, 0.67)))		
		
		#elif type == "trace":
			
			
		
		elif type == "stress":
		
			if stress > 1:
				fill = greyRedGradient(stress+5, 0, 20)
				drawSize = int(round(math.pow(stress*4, 1)))
			
			if stress <= 1:
				fill = greyGreenGradient(stress+5, 0, 20)
				#drawSize = int(round(math.pow(stress*4, 1)))
				
		elif type == "stress_simple":
			
			if maxQPercent >= 1.75:
				fill = greenRedGradient(q*100, 0, capacity*300)
				drawSize = int(round(math.pow(stress*4, 1)))
			
		elif type == "remaining_capacity":
			#drawSizeMultiplier = 0.01
						
			remaining_capacity = capacity-q 
			if remaining_capacity > 0:
				fill = (0, 100, 255)
				drawSize = int( round( math.pow(remaining_capacity, 0.8)))
		
		
			
			#drawSize = int( round(max(remaining_capacity, 1)*xplier) )
			
	elif 'existing' and 'proposed' in conduitData:
		#we're dealing with "compare" dictionary
		lifecycle = conduitData['lifecycle'] #new, chnaged, or existing conduit
		qChange = 	elementChange(conduitData, parameter='maxflow')
		upHGL = 	elementChange(conduitData, parameter='maxHGLUpstream')
		dnHGL = 	elementChange(conduitData, parameter='maxHGLDownstream')
		maxQperc = 	elementChange(conduitData, parameter='maxQpercent')
		avgHGL = (upHGL + dnHGL) / 2.0
		
		
		#FIRST DRAW NEW OR CHANGED CONDUITS IN A CLEAR WAY
		if lifecycle == 'new':
			fill = blue
			drawSize = min(10, conduitData['proposed']['geom1'])*3 
		
		if lifecycle == 'changed':
			fill = blue
			drawSize = min(50, conduitData['proposed']['geom1'])*3 	
		
		#IF THE CONDUITS IS 'EXISTING', DISPLAY SYMBOLOGY ACCORDINGLY (how things changed, etc)
		if lifecycle == 'existing':
			
			if type == 'compare_flow':
					
				if qChange > 0:
					fill = greyRedGradient(qChange, 0, 20)
					drawSize = int(round(math.pow(qChange, 1)))
				
				if qChange <= 0:
					fill = greyGreenGradient(abs(qChange), 0, 20)
					drawSize = int(round(math.pow(qChange, 1)))
				
			if type == 'compare_hgl':
				
				if avgHGL > 0:
					fill = greyRedGradient(avgHGL+15, 0, 20)
					drawSize = int(round(math.pow(avgHGL*5, 1)))
				
				if avgHGL <= 0:
					fill = greyGreenGradient(abs(avgHGL)+15, 0, 20)
					drawSize = int(round(math.pow(avgHGL*5, 1)))
			
			if type == 'compare_stress':
				
				if maxQperc > 0:
					fill = greyRedGradient(maxQperc+15, 0, 20)
					drawSize = int(round(math.pow(maxQperc*10, 1)))
				
				if maxQperc <= 0:
					fill = greyGreenGradient(abs(maxQperc)+15, 0, 20)
					drawSize = int(round(math.pow(maxQperc*10, 1)))
	
	#if highlighted list is provided, overide any symbology for the highlighted conduits 	
	if highlighted and id in highlighted:
		fill = blue
		drawSize = 3	
		
	drawSize = int(drawSize*xplier)
			
	#draw that thing, 
	canvas.line(coordPair, fill = fill, width = drawSize)
	if pipeLengthPlanView(coordPair[0], coordPair[1]) > drawSize*0.75:
		#if length is long enough, add circles on the ends to smooth em out
		#this check avoids circles being drawn for tiny pipe segs
		canvas.ellipse(circleBBox(coordPair[0], drawSize*0.5), fill =fill)
		canvas.ellipse(circleBBox(coordPair[1], drawSize*0.5), fill =fill)

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
	
def annotateLine (canvas, dataDict, fontScale=1, annoKey='name', labeled = None):
	
	txt = dataDict[annoKey]
	if not txt in labeled:
		#do not repeat labels
		font = ImageFont.truetype(fontFile, int(25 * fontScale))
		imgTxt = Image.new('L', font.getsize(txt))
		drawTxt = ImageDraw.Draw(imgTxt)
		drawTxt.text((0,0), txt, font=font, fill=255)
		
		coords = dataDict['coordinates']
		drawCoord = dataDict['draw_coordinates']
		angle = angleBetweenPoint(coords[0], coords[1])
		texRot = imgTxt.rotate(angle, expand=1)
		#canvas.paste( ImageOps.colorize(texRot, (0,0,0), (255,255,84)), (242,60),  texRot)
		
		midpoint = midPoint(drawCoord[0], drawCoord[1])
		canvas.paste(texRot , midpoint,  texRot)
		
		labeled.append(txt) #keep tracj of whats been labeled 
	
	
		
def drawAnnotation (canvas, inp, rpt=None, imgWidth=1024, title=None, currentTstr = None, description = None, 
					objects = None, symbologyType=None, fill=(50,50,50), xplier=None):
	
	modelSize = (canvas.im.getbbox()[2], canvas.im.getbbox()[3]) 
	
	#define main fonts
	
		
	fScale = 1 #modelSize[0] / imgWidth
	#if xplier:
	#	fScale = xplier
	titleFont = ImageFont.truetype(fontFile, int(40 * fScale))
	font = ImageFont.truetype(fontFile, int(20 * fScale))
	
	path = None
	if rpt:
		path = rpt.filePath
	
	files = None
	if objects:
		#grab the file paths (assumes they are SWMMIO objects)
		files = []
		for o in objects:
			files.append(o.filePath)
		path = '\n'.join(files)
	
	annos = '\n'.join(filter(None, [description, path]))
	
	titleTxt = inp.name #inp name if no title provided
	if symbologyType:
		titleTxt = symbology_defs[symbologyType]['title'] + ": " + inp.name
		#if title: 
		#	titleTxt = title + " - " + titleTxt
	if title and not symbologyType: 
		titleTxt = title + ": " + inp.name
		
	
	annotationTxt = "Files:\n" + annos
	annoHeight = canvas.textsize(annotationTxt, font)[1] 
	

	#print "anno size = " + str(annoHeight)
	#print "anno text = " + annotationTxt
	canvas.text((10, modelSize[1] - annoHeight - 10), annotationTxt, fill, font=font)
	canvas.text((10, 15), titleTxt, fill, font=titleFont)
	
	if currentTstr:
		#timestamp i nlower rt corner
		annoHeight = canvas.textsize(currentTstr, font)[1] 
		annoWidth = canvas.textsize(currentTstr, font)[0] 
		canvas.text((modelSize[0] - annoWidth - 10, modelSize[1] - annoHeight - 10), currentTstr, fill, font=font)

#                                                                                                                                      
# wrapper around PIL 1.1.6 Image.save to preserve PNG metadata
#
# public domain, Nick Galbreath                                                                                                        
# http://blog.modp.com/2007/08/python-pil-and-png-metadata-take-2.html                                                                 
#                                                                                                                                       
def pngsave(im, file):
    # these can be automatically added to Image.info dict                                                                              
    # they are not user-added metadata
    reserved = ('interlace', 'gamma', 'dpi', 'transparency', 'aspect')

    # undocumented class
    from PIL import PngImagePlugin
    meta = PngImagePlugin.PngInfo()

    # copy metadata into new object
    for k,v in im.info.iteritems():
        if k in reserved: continue
        meta.add_text(k, v, 0)

    # and save
    im.save(file, "PNG", pnginfo=meta)
	
#dictionaries to hang on to



#drawType definitions
symbology_defs = {
	'compare_flow':{
		'title':'Flow Comparison',
		'description':'Shows the change in peak flows in conduits between a baseline and proposed model'
	},
	'compare_hgl':{
		'title':'HGL Comparison',
		'description':'Shows the change in HGL in conduits between a baseline and proposed model'
	},
	'capacity_remaining':{
		'title':'Remaining Capacity',
		'description':'Shows the amount of full flow capacity remaining in conduits'
	},
	'stress_simple':{
		'title':'Condiut Stress',
		'description':'Shows how taxed conduits are based on their flow (peak flow) with respect to their full-flow capacity'
	},
	'stress':{
		'title':'Condiut Stress',
		'description':'Shows how taxed conduits are based on their flow (peak flow) with respect to their full-flow capacity'
	},
	'compare_stress':{
		'title':'Conduit Stress Comparison',
		'description':'Shows the change in max q / full flow capacity (stress)'
	},
	'flow':{
		'title':'Condiut Flow',
		'description':'Shows the flow in conduits with line weight'
	},
	'flow_proposed':{
		'title':'Flow Proposed edj',
		'description':'Shows the flow in conduits with line weight'
	},
	'flow_stress':{
		'title':'Condiut Flow & Stress',
		'description':'Shows the flow in conduits with line weight and color based on "stress" (flow/full-flow capacity)'
	},
	'remaining_capacity':{
		'title':'Remaining Capacity',
		'description':'Shows the flow in conduits with line weight'
	},
	'trace':{
		'title':'Trace Upstream',
		'description':'Shows the flow in conduits with line weight'
	}
}


#COLOR DEFS
red = 		(250, 5, 5)
blue = 		(5, 5, 250)
white =		(250,250,240)
black = 	(0,3,18)

#For pipe profile development
gTownFloodStartElDict = {
    'T14_3_810': 15.4,
    'T14_3_540': 2.9,
    'T14_3_5_180': 9.9,
    'T14_3_1900': 15.4,
    'T14_3_10_20': 15.4,
    'T14_2_870': 21.9,
    'T14_2_730': 16.9,
    'T14_2_590': 26.4,
    'T14_2_450': 32.9,
    'T14_2_260': 28.9,
    'T14_2_2320': 12.9,
    'T14_2_2220': 9.9,
    'T14_2_2160': 10.9,
    'T14_2_1820': 11.4,
    'T14_2_1630': 12.9,
    'T14_2_1580': 16.4,
    'T14_2_1420': 16.9,
    'T14_2_1340': 21.4,
    'T14_1_1460_west': 46.9,
    'T14_3_1860': 15.9,
    'T14_3_1750': 16.4,
    'T14_3_900': 8.4,
    'T14_3_510': 4.9,
    'T14_3_5_120': 12.4,
    'T14_3_1360': 17.4,
    'T14_2_5_70': 10.9,
    'T14_2_2590': 11.4,
    'T14_1_1440_west': 27.4,
    'T14_2_592': 24.4,
    'T14_2_590_split': 26.4,
    'T14_3_735': 25.4,
    'T14_3_730': 13.9,
    'T14_3_710_split': 6.9,
    'T14_3_1860_split': 16.4,
    'T14_3_860': 7.9,
    'T14_3_630': 8.4,
    'T14_3_620': 13.4,
    'T14_3_5_230': 13.9,
    'T14_3_5_210': 12.4,
    'T14_3_1970': 10.4,
    'T14_3_1850': 15.9,
    'T14_3_1510': 19.9,
    'T14_2_5_220': 11.4,
    'T14_2_2690': 12.4,
    'T14_1_1480_west': 24.4,
    'T14_3_915': 15.9,
    'T14_3_910': 14.4,
    'T14_3_905': 6.9,
    'T14_3_900_split': 8.4,
    'T14_3_815': 10.9,
    'T14_3_810_split': 17.4,
    'T14_3_725': 5.4,
    'T14_3_720': 7.4,
    'T14_3_715': 3.9,
    'T14_3_555': 9.9,
    'T14_3_545': 15.4,
    'T14_3_540_split': 2.9,
    'T14_3_515': 2.4,
    'T14_3_510_split': 23.4,
    'T14_3_5_185': 12.4,
    'T14_3_5_180_split': 9.9,
    'T14_3_5_125': 11.9,
    'T14_3_5_120_split': 12.4,
    'T14_3_1910': 10.4,
    'T14_3_1905': 12.4,
    'T14_3_1900_split': 15.4,
    'T14_3_1865': 13.9,
    'T14_3_1760': 16.4,
    'T14_3_1755': 15.9,
    'T14_3_1750_split': 16.4,
    'T14_3_1375': 19.9,
    'T14_3_1370': 17.9,
    'T14_3_1365': 17.9,
    'T14_3_1360_split': 17.4,
    'T14_3_1260_split': 13.4,
    'T14_2_875': 19.4,
    'T14_2_870_split': 21.9,
    'T14_2_735': 18.4,
    'T14_2_730_split': 16.9,
    'T14_2_594': 22.9,
    'T14_2_5_90': 11.9,
    'T14_2_5_85': 10.4,
    'T14_2_5_80': 12.4,
    'T14_2_5_75': 10.4,
    'T14_2_5_70_split': 10.9,
    'T14_2_455': 31.4,
    'T14_2_450_split': 32.9,
    'T14_2_265': 32.9,
    'T14_2_260_split': 28.9,
    'T14_2_2595': 10.9,
    'T14_2_2590_split': 11.4,
    'T14_2_2335': 12.4,
    'T14_2_2330': 11.4,
    'T14_2_2325': 12.4,
    'T14_2_2320_split': 12.9,
    'T14_2_2225': 13.9,
    'T14_2_2220_split': 9.9,
    'T14_2_2165': 12.4,
    'T14_2_2160_split': 10.9,
    'T14_2_1825': 10.4,
    'T14_2_1820_split': 11.4,
    'T14_2_1635': 10.9,
    'T14_2_1630_split': 12.9,
    'T14_2_1585': 14.9,
    'T14_2_1580_split': 16.4,
    'T14_2_1435': 28.9,
    'T14_2_1425': 17.9,
    'T14_2_1420_split': 16.9,
    'T14_2_1345': 17.9,
    'T14_2_1340_split': 21.4,
    'T14_1_1465_west': 42.9,
    'T14_1_1460_west_split': 46.9,
    'T14_1_1440_west_split': 27.4,
    'T14_1_8_720': 3.4,
    'T14_1_8_710': 8.4,
    'T14_1_8_690': 7.9,
    'T14_1_8_590': 15.4,
    'T14_1_8_580': 15.9,
    'T14_1_8_560': 16.4,
    'T14_1_8_3_30': 12.9,
    'T14_1_8_3_260': 15.9,
    'T14_1_8_3_240': 14.9,
    'T14_1_8_3_20': 14.9,
    'Basement_T14_1_8_1_260': 20.9,
    'Basement_T14_1_6_70': 33.2,
    'Basement_T14_1_6_40': 18.4,
    'T14_1_6_70': 0.2,
    'Basement_T14_2_1_140': 13.4,
    'Basement_T14_2_1_130': 10.4,
    'Basement_T14_1_8_50': 20.9,
    'T14_3_9_90': 12.9,
    'T14_3_9_80': 12.9,
    'T14_3_9_40': 11.9,
    'T14_3_9_20': 15.9,
    'T14_3_9_180': 7.4,
    'T14_3_9_130': 12.9,
    'T14_3_9_110': 13.4,
    'T14_3_890': 9.4,
    'T14_3_80': 17.4,
    'T14_3_8_70': 13.9,
    'T14_3_8_60': 13.4,
    'T14_3_8_40': 12.4,
    'T14_3_8_30': 14.4,
    'T14_3_8_120': 10.4,
    'T14_3_8_110': 9.4,
    'T14_3_700': 10.4,
    'T14_3_7_80': 2.4,
    'T14_3_7_60': 19.4,
    'T14_3_690': 10.4,
    'T14_3_640': 7.9,
    'T14_3_6_90': 3.9,
    'T14_3_6_80': 0.15,
    'T14_3_6_70': 3.9,
    'T14_3_6_60': 13.9,
    'T14_3_6_40': 7.9,
    'T14_3_6_360': 4.9,
    'T14_3_6_350': 5.4,
    'T14_3_6_310': 7.9,
    'T14_3_6_280': 13.4,
    'T14_3_6_230': 8.4,
    'T14_3_6_210': 8.9,
    'T14_3_6_190': 9.9,
    'T14_3_6_160': 10.9,
    'T14_3_6_130': 15.9,
    'T14_3_6_100': 15.4,
    'T14_3_6_1_80': 10.9,
    'T14_3_6_1_50': 13.9,
    'T14_3_6_1_20': 14.9,
    'T14_3_6_1_130': 7.9,
    'T14_3_6_1_110': 8.9,
    'T14_3_5_70': 14.4,
    'T14_3_5_220': 12.4,
    'T14_3_5_10': 10.4,
    'T14_3_460': 10.4,
    'T14_3_450': 13.4,
    'T14_3_40': 17.4,
    'T14_3_4_40': 5.9,
    'T14_3_4_320': 8.9,
    'T14_3_4_310': 5.9,
    'T14_3_4_280': 14.4,
    'T14_3_4_250': 8.4,
    'T14_3_4_180': 8.9,
    'T14_3_4_140': 11.4,
    'T14_3_4_130': 14.9,
    'T14_3_4_100': 7.4,
    'T14_3_4_10': 6.9,
    'T14_3_390': 17.4,
    'T14_3_330': 10.4,
    'T14_3_300': 12.9,
    'T14_3_3_980': 2.9,
    'T14_3_3_950': 9.9,
    'T14_3_3_910': 5.4,
    'T14_3_3_870': 4.9,
    'T14_3_3_820': 8.9,
    'T14_3_3_740': 6.9,
    'T14_3_3_670': 6.9,
    'T14_3_3_600': 9.4,
    'T14_3_3_500': 6.9,
    'T14_3_3_50': 3.9,
    'T14_3_3_480': 12.9,
    'T14_3_3_430': 15.9,
    'T14_3_3_380': 6.4,
    'T14_3_3_290': 11.9,
    'T14_3_3_240': 7.4,
    'T14_3_3_2_90': 0.9,
    'T14_3_3_2_70': 2.4,
    'T14_3_3_2_60': 5.9,
    'T14_3_3_2_30': 4.9,
    'T14_3_3_2_230': 3.9,
    'T14_3_3_2_210': 13.9,
    'T14_3_3_2_20': 5.9,
    'T14_3_3_2_150': 5.4,
    'T14_3_3_2_10': 0.4,
    'T14_3_3_170': 5.9,
    'T14_3_3_140': 13.4,
    'T14_3_3_1050': 0.4,
    'T14_3_3_1000': 2.9,
    'T14_3_3_10': 7.4,
    'T14_3_3_1_80': 13.4,
    'T14_3_3_1_30': 5.4,
    'T14_3_3_1_220': 6.9,
    'T14_3_3_1_120': 7.4,
    'T14_3_3_1_10': 8.9,
    'T14_3_270': 15.9,
    'T14_3_250': 20.4,
    'T14_3_230': 23.4,
    'T14_3_2000': 8.4,
    'T14_3_200': 22.9,
    'T14_3_2_40': 3.4,
    'T14_3_2_30': 14.4,
    'T14_3_2_20': 13.4,
    'T14_3_1740': 18.9,
    'T14_3_1700': 17.4,
    'T14_3_170': 19.4,
    'T14_3_1680': 17.4,
    'T14_3_1670': 17.9,
    'T14_3_1640': 19.4,
    'T14_3_1610': 17.9,
    'T14_3_1570': 19.4,
    'T14_3_1540': 17.9,
    'T14_3_1520': 17.4,
    'T14_3_150': 14.4,
    'T14_3_1340': 16.9,
    'T14_3_1300': 18.4,
    'T14_3_1280': 16.9,
    'T14_3_1210': 13.9,
    'T14_3_1200': 16.4,
    'T14_3_120': 16.9,
    'T14_3_1190': 23.4,
    'T14_3_1160': 14.9,
    'T14_3_1150': 16.9,
    'T14_3_1120': 15.4,
    'T14_3_1110': 19.9,
    'T14_3_1080': 14.4,
    'T14_3_1020': 15.4,
    'T14_3_10_80': 11.9,
    'T14_3_10_70': 12.4,
    'T14_3_10_140': 11.9,
    'T14_3_10_120': 11.9,
    'T14_3_10_110': 11.4,
    'T14_3_10_1_30': 11.9,
    'T14_3_1_60': 13.4,
    'T14_3_1_10': 13.9,
    'T14_2_960': 13.9,
    'T14_2_930': 14.9,
    'T14_2_920': 21.9,
    'T14_2_900': 25.9,
    'T14_2_90_b': 21.4,
    'T14_2_90_a': 11.9,
    'T14_2_860': 18.4,
    'T14_2_850': 13.9,
    'T14_2_820': 14.4,
    'T14_2_800': 15.4,
    'T14_2_80_b': 16.9,
    'T14_2_80_a': 19.9,
    'T14_2_8_80': 14.9,
    'T14_2_8_60': 11.9,
    'T14_2_8_50': 15.9,
    'T14_2_8_30': 12.9,
    'T14_2_8_140': 9.4,
    'T14_2_8_110': 12.4,
    'T14_2_790': 17.4,
    'T14_2_770': 15.9,
    'T14_2_700': 20.4,
    'T14_2_70_b': 17.9,
    'T14_2_70_a': 21.9,
    'T14_2_7_50': 9.4,
    'T14_2_7_30': 10.4,
    'T14_2_7_130': 10.4,
    'T14_2_7_110': 11.4,
    'T14_2_6_80': 10.9,
    'T14_2_6_200': 9.4,
    'T14_2_6_20': 14.9,
    'T14_2_6_150': 9.9,
    'T14_2_6_100': 11.4,
    'T14_2_580': 27.4,
    'T14_2_560': 25.4,
    'T14_2_530': 27.9,
    'T14_2_5_30': 10.4,
    'T14_2_5_260': 12.4,
    'T14_2_5_250': 12.4,
    'T14_2_5_10': 19.4,
    'T14_2_40': 17.4,
    'T14_2_4_50': 10.4,
    'T14_2_4_30': 10.9,
    'T14_2_4_150': 8.4,
    'T14_2_4_130': 10.4,
    'T14_2_4_100': 10.9,
    'T14_2_380': 33.4,
    'T14_2_350': 33.4,
    'T14_2_320': 31.9,
    'T14_2_3_90': 9.9,
    'T14_2_3_80': 12.9,
    'T14_2_3_50': 8.9,
    'T14_2_3_130': 13.9,
    'T14_2_3_120': 11.9,
    'T14_2_3_10': 11.9,
    'T14_2_2740': 8.9,
    'T14_2_2710': 10.9,
    'T14_2_2530': 12.9,
    'T14_2_230': 24.4,
    'T14_2_220_a': 24.4,
    'T14_2_2120': 13.9,
    'T14_2_2070': 13.4,
    'T14_2_2040': 18.4,
    'T14_2_200_b': 23.9,
    'T14_2_200_a': 16.9,
    'T14_2_2_90': 13.4,
    'T14_2_2_50': 14.9,
    'T14_2_2_30': 18.4,
    'T14_2_2_20': 19.9,
    'T14_2_2_110': 11.4,
    'T14_2_2_10': 19.4,
    'T14_2_1940': 9.4,
    'T14_2_190_b': 23.9,
    'T14_2_190_a': 16.9,
    'T14_2_180_b': 21.9,
    'T14_2_180_a': 21.9,
    'T14_2_1780': 10.9,
    'T14_2_170_b': 22.4,
    'T14_2_170_a': 22.9,
    'T14_2_160_b': 8.9,
    'T14_2_160_a': 21.4,
    'T14_2_1510': 19.9,
    'T14_2_150_b': 9.4,
    'T14_2_150_a': 22.4,
    'T14_2_140_b': 13.4,
    'T14_2_1310': 16.9,
    'T14_2_130_b': 18.9,
    'T14_2_130_a': 9.9,
    'T14_2_1240': 14.4,
    'T14_2_1210': 14.4,
    'T14_2_120_b': 20.4,
    'T14_2_120_a': 8.4,
    'T14_2_1190': 14.4,
    'T14_2_1160': 15.9,
    'T14_2_1130': 13.9,
    'T14_2_1100': 13.9,
    'T14_2_110_b': 21.4,
    'T14_2_110_a': 9.4,
    'T14_2_1080': 14.9,
    'T14_2_1040': 14.4,
    'T14_2_1000': 13.9,
    'T14_2_100_b': 22.4,
    'T14_2_100_a': 10.4,
    'T14_2_1_70': 13.9,
    'T14_2_1_60': 15.4,
    'T14_2_1_120': 4.4,
    'T14_2_1_100': 9.9,
    'T14_2_1_10': 27.4,
    'T14_1_920': 18.4,
    'T14_1_910': 25.9,
    'T14_1_9_70': 11.9,
    'T14_1_9_20': 13.4,
    'T14_1_9_150': 8.9,
    'T14_1_9_100': 10.9,
    'T14_1_870': 25.9,
    'T14_1_8_680': 4.4,
    'T14_1_8_540': 21.9,
    'T14_1_8_490': 17.4,
    'T14_1_8_460': 7.4,
    'T14_1_8_410': 18.9,
    'T14_1_8_370': 18.4,
    'T14_1_8_340': 12.4,
    'T14_1_8_320': 11.9,
    'T14_1_8_300': 11.4,
    'T14_1_8_3_250': 16.4,
    'T14_1_8_3_10': 18.9,
    'T14_1_8_270': 7.4,
    'T14_1_8_240': 10.4,
    'T14_1_8_230': 5.9,
    'T14_1_8_2_460': 4.4,
    'T14_1_8_2_450': 7.9,
    'T14_1_8_2_370': 9.9,
    'T14_1_8_2_340': 6.4,
    'T14_1_8_2_320': 0.9,
    'T14_1_8_2_300': 3.4,
    'T14_1_8_2_260': 10.9,
    'T14_1_8_2_200': 6.9,
    'T14_1_8_2_180': 20.4,
    'T14_1_8_2_100': 9.4,
    'T14_1_8_2_1_80': 8.4,
    'T14_1_8_2_1_60': 10.9,
    'T14_1_8_2_1_30': 4.9,
    'T14_1_8_2_1_10': 4.4,
    'T14_1_8_190': 8.9,
    'T14_1_8_10': 20.9,
    'T14_1_8_1_560': 3.4,
    'T14_1_8_1_550': 11.9,
    'T14_1_8_1_540': 13.9,
    'T14_1_8_1_520': 13.4,
    'T14_1_8_1_510': 18.4,
    'T14_1_8_1_500': 14.9,
    'T14_1_8_1_490': 12.4,
    'T14_1_8_1_470': 14.9,
    'T14_1_8_1_410': 14.4,
    'T14_1_8_1_360': 14.4,
    'T14_1_8_1_320': 4.4,
    'T14_1_8_1_310': 9.9,
    'T14_1_8_1_300': 4.9,
    'T14_1_8_1_230': 3.4,
    'T14_1_8_1_150': 9.9,
    'T14_1_8_1_120': 9.4,
    'T14_1_8_1_100': 8.9,
    'T14_1_8_1_1_30': 0.4,
    'T14_1_8_1_1_20': 2.9,
    'T14_1_8_1_1_10': 3.9,
    'T14_1_710': 16.4,
    'T14_1_7_90': 30.9,
    'T14_1_7_80': 32.4,
    'T14_1_7_60': 26.9,
    'T14_1_7_40': 26.4,
    'T14_1_7_190': 10.4,
    'T14_1_7_180': 23.4,
    'T14_1_7_170': 26.9,
    'T14_1_7_130': 21.4,
    'T14_1_7_100': 21.9,
    'T14_1_7_10': 21.9,
    'T14_1_650': 28.4,
    'T14_1_6_130': 5.4,
    'T14_1_6_10': 15.9,
    'T14_1_5_70': 24.9,
    'T14_1_5_420': 11.4,
    'T14_1_5_380': 11.9,
    'T14_1_5_260': 17.9,
    'T14_1_5_20': 28.9,
    'T14_1_5_190': 16.4,
    'T14_1_5_100': 21.9,
    'T14_1_5_1_60': 14.9,
    'T14_1_5_1_20': 13.4,
    'T14_1_420': 25.4,
    'T14_1_4_50': 3.9,
    'T14_1_4_30': 14.9,
    'T14_1_320': 16.4,
    'T14_1_3_50': 10.9,
    'T14_1_3_100': 10.4,
    'T14_1_3_10': 13.9,
    'T14_1_2860': 20.4,
    'T14_1_2730': 19.9,
    'T14_1_2670': 19.9,
    'T14_1_2650_east': 19.4,
    'T14_1_2640_west': 23.9,
    'T14_1_2620': 18.9,
    'T14_1_2600_east': 21.4,
    'T14_1_2590_west': 19.4,
    'T14_1_2560_east': 18.4,
    'T14_1_2550_east': 19.4,
    'T14_1_2540_west': 19.9,
    'T14_1_2530_west': 19.4,
    'T14_1_2520_west': 19.4,
    'T14_1_2520_east': 20.4,
    'T14_1_2500_west': 18.9,
    'T14_1_2490_west': 19.9,
    'T14_1_2490_east': 20.9,
    'T14_1_2460_east': 21.9,
    'T14_1_2450_west': 18.4,
    'T14_1_2450_east': 20.9,
    'T14_1_2440_west': 17.4,
    'T14_1_2440_east': 18.4,
    'T14_1_2430': 18.9,
    'T14_1_2400_east': 21.4,
    'T14_1_240': 0.4,
    'T14_1_2390_east': 24.9,
    'T14_1_2360_east': 21.4,
    'T14_1_2320_east': 19.4,
    'T14_1_2290_east': 19.4,
    'T14_1_2280_east': 18.9,
    'T14_1_2230_east': 18.4,
    'T14_1_2200_east': 18.9,
    'T14_1_2130_east': 18.4,
    'T14_1_2090_east': 19.4,
    'T14_1_2080_east': 23.4,
    'T14_1_2_490': 6.9,
    'T14_1_2_410': 6.9,
    'T14_1_2_40': 17.4,
    'T14_1_2_320': 4.9,
    'T14_1_2_180': 25.9,
    'T14_1_1990_east': 28.9,
    'T14_1_1980_east': 33.4,
    'T14_1_1950_east': 33.9,
    'T14_1_1940_east': 37.9,
    'T14_1_1930_east': 41.4,
    'T14_1_1890_east': 42.4,
    'T14_1_1860_east': 36.9,
    'T14_1_1820_east': 31.9,
    'T14_1_1740_east': 26.9,
    'T14_1_1730_east': 28.9,
    'T14_1_1660_east': 23.9,
    'T14_1_1650_east': 23.4,
    'T14_1_1630_east': 23.9,
    'T14_1_1620_east': 23.4,
    'T14_1_1580_east': 18.9,
    'T14_1_1520_west': 0.9,
    'T14_1_1490_west': 1.4,
    'T14_1_1470_east': 19.4,
    'T14_1_1420_east': 19.9,
    'T14_1_1410': 19.4,
    'T14_1_1320': 21.4,
    'T14_1_1160': 25.4,
    'T14_1_1090': 17.9,
    'T14_1_1_680': 10.4,
    'T14_1_1_670': 11.4,
    'T14_1_1_650': 10.9,
    'T14_1_1_590': 10.4,
    'T14_1_1_460': 10.9,
    'T14_1_1_400': 10.9,
    'T14_1_1_40': 33.9,
    'T14_1_1_330': 9.4,
    'T14_1_1_280': 8.4,
    'T14_1_1_270': 9.9,
    'T14_1_1_250': 12.4,
    'T14_1_1_210': 9.4,
    'T14_1_1_170': 8.4,
    'T14_1_1_150': 15.9,
    'T14_1_1_10': 24.9
}
gtownSubset = {
    'T14_3_1080', 'T14_3_1020', 'T14_3_915', 'T14_3_910', 'T14_3_905',
    'T14_3_900', 'T14_3_890', 'T14_3_860', 'T14_3_815', 'T14_3_810',
    'T14_3_735', 'T14_3_730', 'T14_3_725', 'T14_3_720', 'T14_3_715',
    'T14_3_710'
}
gtownSub2 = {
    'T14_3_3_2_230', 'T14_3_3_2_210', 'T14_3_3_2_150', 'T14_3_3_2_120',
    'T14_3_3_2_90', 'T14_3_3_2_70', 'T14_3_3_2_60', 'T14_3_3_2_30',
    'T14_3_3_2_20', 'T14_3_3_2_10', 'T14_3_3_820', 'T14_3_3_740'
}
gtownSub3 = {
    'T14_3_3_2_230', 'T14_3_3_2_210', 'T14_3_3_2_150', 'T14_3_3_2_120',
    'T14_3_3_2_90', 'T14_3_3_2_70'
}
gtownSub4 = {
    'T14_3_3_2_230', 'T14_3_3_2_210', 'T14_3_3_2_150', 'T14_3_3_2_120',
    'T14_3_3_2_90', 'T14_3_3_2_70', 'T14_3_3_2_60', 'T14_3_3_2_30',
    'T14_3_3_2_20', 'T14_3_3_2_10', 'T14_3_3_820', 'T14_3_3_740',
    'T14_3_3_690', 'T14_3_3_670', 'T14_3_3_650', 'T14_3_3_600',
    'T14_3_3_500', 'T14_3_3_480', 'T14_3_3_430', 'T14_3_3_380',
    'T14_3_3_290', 'T14_3_3_240', 'T14_3_3_170', 'T14_3_3_140'
}
gtownSub5 = {
    'T14_3_1110', 'T14_3_1080', 'T14_3_1020', 'T14_3_915', 'T14_3_910',
    'T14_3_905', 'T14_3_900', 'T14_3_890', 'T14_3_860', 'T14_3_815',
    'T14_3_810', 'T14_3_735', 'T14_3_730', 'T14_3_725', 'T14_3_720',
    'T14_3_715', 'T14_3_710'
}
gtownSub6 = {
    'T14_1_8_1_560', 'T14_1_8_1_550', 'T14_1_8_1_540', 'T14_1_8_1_520',
    'T14_1_8_1_510', 'T14_1_8_1_500', 'T14_1_8_1_490', 'T14_1_8_1_470',
    'T14_1_8_1_410', 'T14_1_8_1_360', 'T14_1_8_1_320', 'T14_1_8_1_310',
    'T14_1_8_1_300', 'T14_1_8_1_260', 'T14_1_8_1_230', 'T14_1_8_1_150',
    'T14_1_8_1_120', 'T14_1_8_1_100', 'T14_1_8_50', 'T14_1_8_20',
    'T14_1_8_10', 'Subway_East_C', 'Subway_East_B', 'Subway_East_A',
    'T14_1_2400_east', 'T14_1_2390_east', 'T14_1_2360_east',
    'T14_1_2320_east', 'T14_1_2290_east', 'T14_1_2280_east',
    'T14_1_2230_east', 'T14_1_2200_east', 'T14_1_2130_east',
    'T14_1_2090_east', 'T14_1_2080_east', 'T14_1_1990_east',
    'T14_1_1980_east', 'T14_1_1950_east', 'T14_1_1940_east',
    'T14_1_1930_east', 'T14_1_1890_east', 'T14_1_1880_east',
    'T14_1_1860_east', 'T14_1_1820_east', 'T14_1_1740_east',
    'T14_1_1730_east', 'T14_1_1660_east', 'T14_1_1650_east',
    'T14_1_1630_east', 'T14_1_1620_east', 'T14_1_1580_east',
    'T14_1_1470_east', 'T14_1_1420_east', 'T14_1_1410', 'T14_1_1320',
    'T14_1_1160', 'T14_1_1090', 'T14_1_920', 'T14_1_910', 'T14_1_870',
    'T14_1_710', 'T14_1_650', 'T14_1_420', 'T14_1_320', 'T14_1_240'
}
gtownOutfallToTrunkSplit = {
    'T14_1_2860', 'T14_1_2730', 'T14_1_2670_east', 'T14_1_2650_east',
    'T14_1_2620_east', 'T14_1_2600_east', 'T14_1_2560_east',
    'T14_1_2550_east', 'T14_1_2520_east', 'T14_1_2490_east',
    'T14_1_2460_east', 'T14_1_2450_east', 'T14_1_2440_east', 'T14_1_2430',
    'Subway_East_C', 'Subway_East_B', 'Subway_East_A', 'T14_1_2400_east',
    'T14_1_2390_east', 'T14_1_2360_east', 'T14_1_2320_east',
    'T14_1_2290_east', 'T14_1_2280_east', 'T14_1_2230_east',
    'T14_1_2200_east', 'T14_1_2130_east', 'T14_1_2090_east',
    'T14_1_2080_east', 'T14_1_1990_east', 'T14_1_1980_east',
    'T14_1_1950_east', 'T14_1_1940_east', 'T14_1_1930_east',
    'T14_1_1890_east', 'T14_1_1880_east', 'T14_1_1860_east',
    'T14_1_1820_east', 'T14_1_1740_east', 'T14_1_1730_east',
    'T14_1_1660_east', 'T14_1_1650_east', 'T14_1_1630_east',
    'T14_1_1620_east', 'T14_1_1580_east', 'T14_1_1470_east',
    'T14_1_1420_east', 'T14_1_1410', 'T14_1_1320', 'T14_1_1160',
    'T14_1_1090', 'T14_1_920', 'T14_1_910', 'T14_1_870', 'T14_1_710',
    'T14_1_650', 'T14_1_420', 'T14_1_320', 'T14_1_240'
}
gtownWestBranch = {
    'T14_3_10_140', 'T14_3_10_120', 'T14_3_10_110', 'T14_3_10_80',
    'T14_3_10_70', 'T14_3_10_20', 'T14_3_1850', 'T14_3_1760', 'T14_3_1755',
    'T14_3_1750', 'T14_3_1740', 'T14_3_1700', 'T14_3_1680', 'T14_3_1670',
    'T14_3_1640', 'T14_3_1610', 'T14_3_1570', 'T14_3_1540', 'T14_3_1520',
    'T14_3_1510', 'T14_3_1375', 'T14_3_1370', 'T14_3_1365', 'T14_3_1360',
    'T14_3_1340', 'T14_3_1300', 'T14_3_1280', 'T14_3_1260', 'T14_3_1210',
    'T14_3_1200', 'T14_3_1190', 'T14_3_1160', 'T14_3_1150', 'T14_3_1120',
    'T14_3_1110', 'T14_3_1080', 'T14_3_1020', 'T14_3_915', 'T14_3_910',
    'T14_3_905', 'T14_3_900', 'T14_3_890', 'T14_3_860', 'T14_3_815',
    'T14_3_810', 'T14_3_735', 'T14_3_730', 'T14_3_725', 'T14_3_720',
    'T14_3_715', 'T14_3_710', 'T14_3_700', 'T14_3_690', 'T14_3_640',
    'T14_3_630', 'T14_3_620', 'T14_3_555', 'T14_3_545', 'T14_3_540',
    'T14_3_515', 'T14_3_510', 'T14_3_460', 'T14_3_450', 'T14_3_390',
    'T14_3_330', 'T14_3_300', 'T14_3_270', 'T14_3_250', 'T14_3_240',
    'T14_3_230', 'T14_3_200', 'T14_3_170', 'T14_3_150'
}
gtownEastBranch = {
    'T14_2_2710', 'T14_2_2690', 'T14_2_2595', 'T14_2_2590', 'T14_2_2530',
    'T14_2_2335', 'T14_2_2330', 'T14_2_2325', 'T14_2_2320', 'T14_2_2225',
    'T14_2_2220', 'T14_2_2165', 'T14_2_2160', 'T14_2_2120', 'T14_2_2070',
    'T14_2_2040', 'T14_2_1940', 'T14_2_1825', 'T14_2_1820', 'T14_2_1780',
    'T14_2_1635', 'T14_2_1630', 'T14_2_1585', 'T14_2_1580', 'T14_2_1510',
    'T14_2_1435', 'T14_2_1425', 'T14_2_2740', 'T14_2_1420', 'T14_2_1345',
    'T14_2_1340', 'T14_2_1310', 'T14_2_1240', 'T14_2_1210', 'T14_2_1190',
    'T14_2_1160', 'T14_2_1130', 'T14_2_1100', 'T14_2_1080', 'T14_2_1040',
    'T14_2_1000', 'T14_2_960', 'T14_2_930', 'T14_2_920', 'T14_2_900',
    'T14_2_875', 'T14_2_870', 'T14_2_860', 'T14_2_850', 'T14_2_820',
    'T14_2_800', 'T14_2_790', 'T14_2_770', 'T14_2_735', 'T14_2_730',
    'T14_2_700', 'T14_2_594', 'T14_2_592', 'T14_2_590', 'T14_2_580',
    'T14_2_560', 'T14_2_530', 'T14_2_455', 'T14_2_450', 'T14_2_380',
    'T14_2_350', 'T14_2_320', 'T14_2_265', 'T14_2_260', 'T14_2_230_a',
    'T14_2_220_a', 'T14_2_200_a', 'T14_2_190_a', 'T14_2_180_a',
    'T14_2_170_a', 'T14_2_160_a', 'T14_2_150_a', 'T14_2_130_a',
    'T14_2_120_a', 'T14_2_110_a', 'T14_2_100_a', 'T14_2_90_a', 'T14_2_80_a',
    'T14_2_70_a', 'T14_2_40'
}

fontFile = r"C:\Data\Code\Fonts\Raleway-Regular.ttf"