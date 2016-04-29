#Utilities and such for SWMMIO processing
import math
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import numpy as np
import matplotlib.path as mplPath

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
d70 = 			((2694096, 222741),	(2697575, 225059))
ritner_moyamen =((2693433, 223967),	(2694587, 224737))

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

def col2RedGradient(x, xmin, xmax, startCol=lightgrey):
	
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

	#lightgrey = (235, 235, 225)

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

def subsetElements(model, type='node', key='floodDuration', min=0.083, max=99999, bbox=None, pair_only=False):
	#return a subset of a dictionary of swmm elements based on a value 
	
	if type=='node':
		elems = model.organizeNodeData(bbox)['nodeDictionaries']
		
	elif type=='conduit':
		elems = model.organizeConduitData(bbox)['conduitDictionaries']
	else: return []
	
	if pair_only:
		#only return the element and the value being filtered on 
		subset = {k:v[key] for (k,v) in elems.items() if v[key] >= min and v[key] < max}
	else:
		subset = {k:v for (k,v) in elems.items() if v[key] >= min and v[key] < max}
	
	return subset


def parcelsFlooded(model, threshold = 0.083, bbox=None, shiftRatio=None, width=1024):

	#return list of nodes with flood duration above threshold 
	flooded_nodes = subsetElements(model, min=threshold, bbox=bbox)
	print '{} flooded nodes found'.format(len(flooded_nodes))
	
	#return sheds that contain these floode nodes (room for optimization here, don't need to rescan the arcpy search cursor every time...)
	sheds = shape2Pixels("detailedsheds", where=None, targetImgW=width, shiftRatio=shiftRatio, bbox=bbox)['geometryDicts']
	parcels = shape2Pixels("parcels3", where=None, targetImgW=width, shiftRatio=shiftRatio, bbox=bbox)
	
	imgSize = parcels['imgSize']
	parcels = parcels['geometryDicts']
	print 'Processing {0} sheds and {1} parcels'.format(len(sheds), len(parcels))
	
	sheds_with_flooded_nodes = {}
	parcels_flooded = {}
	for shed, data in sheds.iteritems():
		#create a path object and test if contains any flooded nodes
		coords = data['coordinates']
		shed_path = mplPath.Path(coords) #matplotlib Path object 
		
		floodDurationSum = 0.0 #to calc the average duration in the shed
		flood_nodes_in_shed = {}
		for node, data in flooded_nodes.iteritems():
			if shed_path.contains_point(data['coordinates']): #maybe used contains_points for efficiency
				
				#we found a shed with flooding
				flood_nodes_in_shed.update({node:data['floodDuration']})
				
				floodDurationSum += data['floodDuration']
				
		#build a dictionary containing each shed with flooded nodes, 
		#containing a dictionary of each node with hours flooded
		if flood_nodes_in_shed:
			avgDuration = floodDurationSum / float(len(flood_nodes_in_shed))
			#flood_nodes_in_shed.update({'avgerage_duration':avgDuration})
			
			sheds_with_flooded_nodes.update({shed:flood_nodes_in_shed})
			
			#find the parcels that intersection
			for parcel, data in parcels.iteritems():
				coords = data['coordinates']
				parcel_path = mplPath.Path(coords) #matplotlib Path object 
				if shed_path.intersects_path(parcel_path):
					
					parcels_flooded.update({parcel:{'shed':shed,'avgerage_duration':avgDuration, 'flooded_nodes':flood_nodes_in_shed, 'draw_coordinates':data['draw_coordinates']}})
					#return parcels_flooded
	
	print 'Found {0} sheds and {1} parcels with flooding above {2} hours.'.format(len(sheds_with_flooded_nodes), len(parcels_flooded), threshold)
	return {'sheds':sheds_with_flooded_nodes, 'parcels':parcels_flooded, 'imgSize':imgSize}

def shape2Pixels(feature, cols = ["OBJECTID", "SHAPE@"], where="SHEDNAME = 'D68-C1'", shiftRatio=None, targetImgW=1024, bbox=None, gdb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb'):
	
	#take data from a geodatabase and organize in a dictionary with coordinates and draw_coordinates
	
	import json
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
		#img.paste(texRot, midpoint)# , drawCoord,  texRot)
		
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
	if symbologyType and symbologyType in symbology_defs:
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
shed_blue = (0,169,230)
white =		(250,250,240)
black = 	(0,3,18)
lightgrey = (235, 235, 225)
grey = 		(100,95,97)

#FONTS
fontFile = r"C:\Data\Code\Fonts\Raleway-Regular.ttf"

#end