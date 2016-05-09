#Utilities and such for SWMMIO processing
import math
from PIL import Image, ImageDraw, ImageFont, ImageOps
from time import strftime
import os
import numpy as np
import matplotlib.path as mplPath
from matplotlib.transforms import BboxBase
import pickle
import json
import arcpy
import draw_options as du

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
morris_10th = 	((2693740, 227260),	(2694412, 227693))

study_area = 	((2682005, 219180), (2701713, 235555))
dickenson_7th = ((2695378, 227948), (2695723, 228179))
packer_18th = 	((2688448, 219932), (2691332, 221857))
moore_broad = 	((2689315, 225537), (2695020, 228592))

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

	 
def parcel_flood_duration(model, parcel_features, threshold=0.083,  bbox=None, 
							gdb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb', 
							export_table=False,anno_results={}):
	
	#return a dictionary of each parcel ID with averagre flood duration
	
	#check if a parcel to node association dicitonary exists, load if possible
	parcel_to_nodes_filename = os.path.join(model.inp.dir, 'parcel_nodes_dict.txt')
	if not os.path.isfile(parcel_to_nodes_filename):
		
		#this is a heavy operation, allow a few minutes
		print "generating parcel/node association dictionary..."
		parcel_to_nodes_dict = parcel_to_nodes_dictionary(parcel_features, gdb=gdb, bbox=bbox) 
		
		#save for later use
		with open(parcel_to_nodes_filename, 'w') as dictSaveFile:
			pickle.dump(parcel_to_nodes_dict, dictSaveFile)
	else:
		print "loading parcel/node association dictionary..."
		parcel_to_nodes_dict = pickle.load( open(parcel_to_nodes_filename, 'r') ) 
		print "WARNING: make sure this loaded parcel dict contains all parcels!"
	
	#grab the list of flooded nodes, and create the dictionary of parcels linked to node IDs
	flooded_nodes = subsetElements(model, min=threshold, bbox=bbox, pair_only=True)
	
	#parcels_dict = parcel_to_nodes_dictionary(parcel_features, where = None, gdb=gdb, bbox=bbox) #this is heavy
	
	#tally how many were flooded above set durations
	#{minutes : number of parcels with flooding greater than}
	duration_partition = {
				5:0, 10:0, 15:0,
				30:0, 45:0, 60:0,
				75:0, 90:0, 105:0,
				120:0
				}
	#calculate average flood duration for each parcel
	parcels_flooded_count = 0
	for parcel, parcel_data in parcel_to_nodes_dict.iteritems():
	
		associated_nodes = parcel_data['nodes'] #associated nodes
		
		if len(associated_nodes) > 0:
			
			total_parcel_flood_dur = 0.0
			flood_duration = 0.0
			for node in associated_nodes:
				
				#look up the flood duration
				node_duration = flooded_nodes.get(node, 0)
				total_parcel_flood_dur += node_duration #for avereage calculation
				
				#parcel flooding duration assumed to be the max of all adjacent node durations
				flood_duration = max(flood_duration, node_duration)  
			
			avg_flood_duration = total_parcel_flood_dur/len(associated_nodes)
			parcel_data.update({'avg_flood_duration':avg_flood_duration, 'flood_duration':flood_duration})
			
			if flood_duration >= threshold: 
				#we've found a parcel that is considered flooded 
				parcels_flooded_count += 1
				
			for duration, count in duration_partition.iteritems():
				if flood_duration >= float(duration)/60.0:
					count += 1
					duration_partition.update({duration:count})
	
	parcels_count = len(parcel_to_nodes_dict)
	parcels_flooded_fraction = float(parcels_flooded_count)/float(parcels_count)
	
	results = {
				'parcels_flooded_count':parcels_flooded_count, 
				'parcels_count':parcels_count,
				'parcels_flooded_fraction':parcels_flooded_fraction,
				'duration_partition':duration_partition
				}
	
	results_string = "{} ({}%) of {} total".format(results['parcels_flooded_count'], round(results['parcels_flooded_fraction']*100),results['parcels_count'])
	
	print results_string
	
	#partition (detailed) results string
	partitioned_results = "\n"
	for d in sorted(duration_partition):
		perc_of_tot = int(round( float(duration_partition[d]) / float(results['parcels_count']) * 100 ))
		partitioned_results += '>{}mins : {} ({}%)\n'.format(d, duration_partition[d], perc_of_tot)
		
	#track results for annotation
	anno_results.update({'Total Parcels':results['parcels_count'], '\nParcels Flooded':partitioned_results})
	
	#add in the actual list of parcels for drawing
	results.update({'parcels':parcel_to_nodes_dict})
	
	return results
	 
def parcel_to_nodes_dictionary(feature, cols = ["PARCELID", "OUTLET", "SUBCATCH", "SHAPE@"], bbox=None, gdb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb'):
	
	#create dictionary with keys for each parcel, and sub array containing associated nodes
	features = os.path.join(gdb, feature)
	import arcpy
	parcels = {}
	for row in arcpy.da.SearchCursor(features, cols):
		
		#first check if parcel is in bbox
		jsonkey = 'rings' #for arc polygons
		geometrySections = json.loads(row[3].JSON)[jsonkey]
		parcel_in_bbox=True #assume yes first
		for i, section in enumerate(geometrySections):
			#check if part of geometry is within the bbox, skip if not
			if bbox and len ( [x for x in section if pointIsInBox(bbox, x)] ) == 0:
				parcel_in_bbox=False #continue #skip this section if none of it is within the bounding box
			
		if not parcel_in_bbox:
			continue #skip if not in bbox
		
		PARCELID = str(row[0])
		if PARCELID in parcels:
			#append to existing array
			parcels[PARCELID]['nodes'].append(row[1])
			parcels[PARCELID]['sheds'].append(row[2])
		else:
			#new parcel id found
			
			#parcels.update({ PARCELID:{'nodes':[row[1]], 'sheds':[row[2]] }} )
			parcels.update({ PARCELID:{'nodes':[row[1]], 'sheds':[row[2]] }} )
			
	return parcels
	
def shape2Pixels(feature, cols = ["OBJECTID", "SHAPE@"],  where="SHEDNAME = 'D68-C1'", shiftRatio=None, targetImgW=1024, bbox=None, gdb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb'):
	
	#take data from a geodatabase and organize in a dictionary with coordinates and draw_coordinates
	
	
	
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

	


def drawNode(id, nodeData, draw, options, rpt=None, dTime=None, xplier=1):
	
	color = (210, 210, 230) #default color 
	radius = 0 #aka don't show this node by default
	outlineColor = None 
	xy = nodeData['draw_coordinates']
	threshold = options['threshold']
	type = options['type']
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
			color = purple #purple	
			outlineColor = (90, 90, 90)
		
	else:
		floodDuration = nodeData.get('floodDuration', 0)
		maxDepth = nodeData['maxDepth']
		maxHGL = nodeData['maxHGL']
	
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
	draw.ellipse(du.circleBBox(xy, radius), fill =color, outline=outlineColor)

def drawConduit(id, conduitData, canvas, options, rpt=None, dTime = None, xplier = 1, highlighted=None):
	
	#Method for drawing (in plan view) a single conduit, given its RPT results 
	
	#default fill and size
	fill = (120, 120, 130)
	drawSize = 1
	should_draw = True #boolean that can prevent a draw based on params
	coordPair = conduitData['draw_coordinates']
	type = options['type']
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
			drawSize = min(10, conduitData['proposed']['geom1']) 
		
		if lifecycle == 'changed':
			fill = blue
			drawSize = min(50, conduitData['proposed']['geom1'])
		
		#IF THE CONDUITS IS 'EXISTING', DISPLAY SYMBOLOGY ACCORDINGLY (how things changed, etc)
		if lifecycle == 'existing':
			
			if type == 'proposed_simple':
				#drawSize = 0 #don't draw, only print the proposed infrastructure
				#fill = red
				should_draw = False
			if type == 'compare_flow':
					
				if qChange > 0:
					fill = du.greyRedGradient(qChange, 0, 20)
					drawSize = int(round(math.pow(qChange, 1)))
				
				if qChange <= 0:
					fill = du.greyGreenGradient(abs(qChange), 0, 20)
					drawSize = int(round(math.pow(qChange, 1)))
				
			if type == 'compare_hgl':
				
				if avgHGL > 0:
					fill = du.greyRedGradient(avgHGL+15, 0, 20)
					drawSize = int(round(math.pow(avgHGL*5, 1)))
				
				if avgHGL <= 0:
					fill = du.greyGreenGradient(abs(avgHGL)+15, 0, 20)
					drawSize = int(round(math.pow(avgHGL*5, 1)))
			
	
	#if highlighted list is provided, overide any symbology for the highlighted conduits 	
	if highlighted and id in highlighted:
		fill = blue
		drawSize = 3	
		
	drawSize = int(drawSize*xplier)
			
	
	if should_draw:
		#draw that thing
		canvas.line(coordPair, fill = fill, width = drawSize)
		if pipeLengthPlanView(coordPair[0], coordPair[1]) > drawSize*0.75:
			#if length is long enough, add circles on the ends to smooth em out
			#this check avoids circles being drawn for tiny pipe segs
			canvas.ellipse(du.circleBBox(coordPair[0], drawSize*0.5), fill =fill)
			canvas.ellipse(du.circleBBox(coordPair[1], drawSize*0.5), fill =fill)

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
	files = '\n'.join([m.rpt.filePath for m in filter(None, [model, model2])])
	title = ', '.join([m.inp.name for m in filter(None, [model, model2])])
	symbology_string = ', '.join([s['title'] for s in filter(None, [nodeSymb, conduitSymb, parcelSymb])])
	title += ": " + symbology_string 
	
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




#end