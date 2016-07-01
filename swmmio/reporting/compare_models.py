#SWMM Compare - methods to compare rpt files

#for the purposes of this code, "existing" means 'existing system' as in, the existing conditions model
#whereas "proposed" means proposes system, as in, the model representing the system in the proposed conditions


import math
from swmmio.utils import swmm_utils as su
from swmmio.graphics import swmm_graphics as sg
from swmmio.graphics import draw_utils as du
import swmmio.parcels as p
#import SWMMIO
import os
import pandas as pd

from PIL import Image, ImageDraw

def get_all_unmatched_inp_elements (model1, model2):

	unmatches = {}
	for headerpair in model1.inp.headerList:

		#grab the section header
		header = headerpair[0].split("\n")[0]
		dict1 = model1.inp.createDictionary(header)
		dict2 = model2.inp.createDictionary(header)

		#returns all elements that are new or removed from model1 to model2
		added = 	[k for k in dict2 if k not in dict1]
		removed = 	[k for k in dict1 if k not in dict2]
		unmatches.update({header:{'added':added, 'removed':removed}})

	return unmatches
def extents_of_changes(model1, model2, extent_buffer=0.0):

	#Return a bbox sorounding the model elements that have changed

	#list of node IDs that have 'new' coordinates
	newcoordIDs = get_all_unmatched_inp_elements(model1, model2)['[COORDINATES]']['added']
	allcoords = model2.inp.createDictionary('[COORDINATES]')
	newcoords = [v for k,v in allcoords.iteritems() if k in newcoordIDs]

	#build dataframe with these coordinates
	df = pd.DataFrame(data=newcoords, columns=['x', 'y'], dtype=float )

	#create bbox from mins/maxima
	df['x']=df.x.astype(int)  #convert to int
	df['y']=df.y.astype(int)  #convert to int
	x1, y1, x2, y2 = df.x.min(), df.y.min(), df.x.max(), df.y.max()

	#Add a buffer (1 = no buffer)
	l = float(x2 - x1)  #length of extents (ft)
	buff = l*float(extent_buffer)

	bbox = [(x1-buff, y1-buff), (x2+buff, y2+buff)]
	return bbox

def parameter_delta(existing_elem, proposed_elem, parameter='maxflow'):

	#returns change from existing to proposed
	proposedVal = proposed_elem.get(parameter, 0.0)
	existingVal = existing_elem.get(parameter, 0.0)

	return proposedVal - existingVal

def joinModelData (model1, model2, bbox=None, joinType='conduit', compare_param=None):

	#joins data from two models in a side by side dictionary
	#presumably, a baseline and a proposed SFR solution

	if joinType == 'conduit':

		existing_elements = model1.organizeConduitData(bbox)['conduit_objects']
		proposed_elements = model2.organizeConduitData(bbox)['conduit_objects']

	elif joinType == 'node':

		existing_elements = model1.organizeNodeData(bbox)['node_objects']
		proposed_elements = model2.organizeNodeData(bbox)['node_objects']

	elif joinType == 'parcel':

		existing_elements = su.parcel_flood_duration(model1, parcel_features='PWD_PARCELS_SHEDS',
															threshold=0, bbox=bbox)['parcels']
		proposed_elements = su.parcel_flood_duration(model2, parcel_features='PWD_PARCELS_SHEDS',
															threshold=0, bbox=bbox)['parcels']


	joinedData = {}
	for id, data in proposed_elements.iteritems():

		proposed = data
		existing = existing_elements.get(id, {})
		lifecycle = 'existing'
		if not id in existing_elements:
			#element is unique to the proposed system (new infratructure)
			lifecycle = 'new'
		elif 'geom1' in proposed and proposed['geom1'] != existing_elements[id]['geom1']:
			#if this is ID matched one in the existing model
			#and geom 1 changes, this is a replaced/changed pipe
			lifecycle = 'changed'

		if compare_param:
			#if an explicit param is given, find the delta between the models
			#change = parameter_delta(existing, proposed, parameter=compare_param)
			proposedVal = proposed.get(compare_param, 0.0)
			existingVal = existing.get(compare_param, 0.0)
			compareDict = {
						'parameter':compare_param,
						'change':proposedVal-existingVal,
						'proposed':proposedVal,
						'existing':existingVal,
						'lifecycle':lifecycle
						}

		else:
			compareDict = {'proposed':proposed, 'existing':existing, 'lifecycle':lifecycle}

		joinedData.update({id:compareDict})

	return joinedData


def compareNodes (model1, model2, bbox=None, floodthreshold=0.08333):

	#return a dict of node objects with the delta between models

	existing_elements = model1.organizeNodeData(bbox)['node_objects']
	proposed_elements = model2.organizeNodeData(bbox)['node_objects']

	for id, proposed in proposed_elements.iteritems():

		existing = existing_elements.get(id, {})

		if id in existing_elements:
			#not a new element
			flood_duration_delta = proposed.flood_duration - existing.flood_duration
			proposed.flood_duration = flood_duration_delta
			proposed.maxDepth = proposed.maxDepth - existing.maxDepth
			proposed.maxHGL = proposed.maxHGL = existing.maxHGL

			#detect what "type" the flooding change is
			if proposed.flood_duration >= floodthreshold and existing.flood_duration < floodthreshold:
				proposed.delta_type = 'new_flooding'

			elif existing.flood_duration >= floodthreshold and flood_duration_delta >= 0.25:
				#flooding increased by more than 15 minutes
				proposed.delta_type = 'increased_flooding'

			elif existing.flood_duration >= floodthreshold and flood_duration_delta <= -0.25:
				proposed.delta_type = 'decreased_flooding'

			elif existing.flood_duration >= floodthreshold and proposed.flood_duration < floodthreshold:
				proposed.delta_type = 'eliminated_flooding'

		else:
			#element is unique to the proposed system (new infratructure)
			lifecycle = 'new'


		proposed.is_delta = True

	return proposed_elements #with delta data

def compareConduits (model1, model2, bbox=None):

	#return a dict of node objects with the delta between models

	existing_elements = model1.organizeConduitData(bbox)['conduit_objects']
	proposed_elements = model2.organizeConduitData(bbox)['conduit_objects']

	for id, proposed in proposed_elements.iteritems():

		existing = existing_elements.get(id, {})
		if id in existing_elements:
			#dealinhg with an exiting pipe
			proposed.maxflow = proposed.maxflow - existing.maxflow
			proposed.maxQpercent = proposed.maxQpercent - existing.maxQpercent
			proposed.maxHGLDownstream = proposed.maxHGLDownstream - existing.maxHGLDownstream
			proposed.maxHGLUpstream = proposed.maxHGLUpstream - existing.maxHGLUpstream
			if proposed.geom1 != existing.geom1:
				#if this is ID matched one in the existing model
				#and geom 1 changes, this is a replaced/changed pipe
				proposed.lifecycle = 'changed'
		else:
			#element is unique to the proposed system (new infratructure)
			proposed.lifecycle = 'new'

		proposed.is_delta = True

	return proposed_elements #with delta data


def compareModelResults(model1, model2, bbox=None, parameter='floodDuration', joinType='node'):

	outFilePath = os.path.join(model2.inp.dir, model2.inp.name) + "_" + parameter + "_change.csv"
	joinedData = joinModelData(model1, model2, bbox=bbox, joinType=joinType)

	with open(outFilePath, 'w') as file:

		header = "id, existing " + parameter + ", proposed "+ parameter + ", " + parameter + "_change, " + "lifecycle," + "comment"
		#head = ', '.join('id', 'existing ')
		file.write("%s\n" % header)
		for element, data in joinedData.iteritems():

			change = su.elementChange(data, parameter=parameter)
			existing = data['existing'][parameter]
			proposed = data['proposed'][parameter]

			#line = element + ", " + str(change) + ", " + str(data['lifecycle'])

			line = ','.join([str(x) for x in [element, existing, proposed, change, data['lifecycle'] ] ])

			if data['existing'].get(parameter, 0) == 0 and data['proposed'].get(parameter, 0) > 0:
				line += ", new " + parameter

			file.write("%s\n" % line)

	#outFile.close()

	return outFilePath

def comparisonReport (model1, model2, bbox=None, threshold=0.083):

	outFile = os.path.join(model2.inp.dir, model2.inp.name) + "_change.csv"

	#joinedConduits = joinModelData(model1, model2, bbox)
	joinedNodes = joinModelData(model1, model2, bbox, joinType='node')

	#aggregate occurences of important changes to nodes
	nodesFloodDIncrease = 0 #nodes with an increase in flood duration
	nodesFloodDDecrease = 0 #nodes with an decrease in flood duration
	nodesFloodEliminated = 0 #nodes that previously flooded, that now do not at all(or less than 5 mins?)
	nodesFloodNew = 0#count of nodes flooding that previousl did not


	for node, data in joinedNodes.iteritems():

		#if 'floodDuration' in data['existing'] and 'floodDuration' in data['proposed']:
		existingFloodD = data['existing'].get('floodDuration', 0)
		proposedFloodD = data['proposed'].get('floodDuration', 0)
		#else:
		#	return node, data

		floodDurationChange = su.elementChange(data, parameter='floodDuration')

		if floodDurationChange > 0:
			nodesFloodDIncrease += 1

		if floodDurationChange < 0:
			nodesFloodDDecrease += 1

		if existingFloodD == 0 and proposedFloodD > threshold:
			nodesFloodNew += 1

		if proposedFloodD == 0 and existingFloodD > threshold:
			nodesFloodEliminated += 1


	with open (outFile, 'wb') as file:

		file.write("Model Comparison Report\n=======================\n\n")
		file.write("Associated Files:\n\t" + '\n'.join([model1.inp.filePath, model1.rpt.filePath, model2.inp.filePath, model2.rpt.filePath]) )
		file.write("\nAggregate Node Flooding Change\n============================\n\n")
		file.write("Nodes with flooding eliminated, {}\n".format(nodesFloodEliminated))
		file.write("Nodes with flooding decreased, {}\n".format(nodesFloodDDecrease))
		file.write("Nodes with flooding increased, {}\n".format(nodesFloodDIncrease))
		file.write("Nodes with new flooding, {}\n".format(nodesFloodNew))


	os.startfile(outFile)

def drawModelComparison(model1, model2, delta_parcels=None, anno_results = {}, **kwargs):

	#unpack and update the options
	ops = du.default_draw_options()
	ops.update({'conduitSymb':du.conduit_options('proposed_simple')}) #default overide
	#print ops
	for key, value in kwargs.iteritems():
		ops.update({key:value})

	#return ops
	width = ops['width']
	xplier = ops['xplier']
	bbox = ops['bbox']
	imgName = ops['imgName'] # for some reason saveImage() won't take the dict reference
	imgDir = ops['imgDir']

	#joinedConduits = joinModelData(model1, model2, bbox)
	#joinedNodes = joinModelData(model1, model2, bbox, joinType='node')
	conduits_delta = compareConduits(model1, model2, bbox)
	nodes_delta = compareNodes(model1, model2, bbox)


	xplier *= width/1024 #scale the symbology sizes
	width = width*2

	modelSizeDict = su.convertCoordinatesToPixels(conduits_delta, bbox=bbox, targetImgW=width)
	shiftRatio = modelSizeDict['shiftRatio']

	su.convertCoordinatesToPixels(nodes_delta, targetImgW=width, bbox=bbox, shiftRatio=shiftRatio)
	imgSize = modelSizeDict['imgSize']
	if not bbox:
		bbox = modelSizeDict['boundingBox']
	shiftRatio = modelSizeDict['shiftRatio']

	imgSize = [int(x) for x in imgSize]
	img = Image.new('RGB', imgSize, ops['bg'])
	draw = ImageDraw.Draw(img)

	#anno_results = {}

	#DRAW THE PARCELS
	if ops['parcelSymb']:

		#joined_parcels = joinModelData(model1, model2, bbox, joinType='parcel')
		floodthresh = ops['parcelSymb']['threshold']
		delta_thresh = ops['parcelSymb']['delta_threshold']

		if not delta_parcels:
			print 'calculating existig parcel flooding'
			existing_parcel_flooding = p.parcel_flood_duration(model1, parcel_features='PWD_PARCELS_SHEDS',
													bbox=None, anno_results=anno_results)['parcels']


			proposed_parcel_flooding = p.parcel_flood_duration(model2, parcel_features='PWD_PARCELS_SHEDS',
												bbox=None, anno_results=anno_results)['parcels']
		 	print 'calculating delta  parcel flooding'
			delta_parcels = p.compareParcels(existing_parcel_flooding, proposed_parcel_flooding,
											bbox=None, floodthreshold=floodthresh,
											delta_threshold=delta_thresh,
											anno_results=anno_results)['parcels']

		sg.drawParcels(draw, delta_parcels, options=ops['parcelSymb'], bbox=bbox,
						width=width, shiftRatio=shiftRatio)

	if ops['basemap']:
		sg.drawBasemap(draw, img=img, options=ops['basemap'], width=width, bbox=bbox,
						shiftRatio=shiftRatio, xplier=xplier)

	drawCount = 0
	#DRAW THE CONDUITS
	if ops['conduitSymb']:
		for id, conduit in conduits_delta.iteritems():
			if conduit.coordinates: #has coordinate? draw. protect from rdii junk
				su.drawConduit(conduit, draw, ops['conduitSymb'], xplier = xplier)
				drawCount += 1

	#DRAW THE NODES
	if ops['nodeSymb']:
		for id, node in nodes_delta.iteritems():
			#return nodeDict
			if node.coordinates: #this prevents draws if no flow is supplied (RDII and such)
				#drawNode(node, draw, options, rpt=None, dTime=None, xplier=1):
				su.drawNode(node, draw, options=ops['nodeSymb'], dTime=None, xplier=xplier)
				drawCount += 1
			# if ('floodDuration' and 'maxDepth' in nodeDict['proposed']) and ('floodDuration' and 'maxDepth' in nodeDict['existing']):
				# #this prevents draws if no flow is supplied (RDII and such)
				# su.drawNode(node, nodeDict, draw, rpt=None, options=ops['nodeSymb'], dTime=None, xplier=xplier)
				# drawCount += 1

	#su.drawAnnotation (draw, model2.inp, imgWidth=width, title=title, objects=[model1.rpt, model2.rpt], symbologyType=conduitSymb, fill=su.black)
	su.annotateMap (draw, model1, model2, options=ops, results = anno_results)
	del draw
	#SAVE IMAGE TO DISK
	sg.saveImage(img, model2, imgName, imgDir=imgDir)



#end
