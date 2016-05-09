#SWMM Compare - methods to compare rpt files

#for the purposes of this code, "existing" means 'existing system' as in, the existing conditions model
#whereas "proposed" means proposes system, as in, the model representing the system in the proposed conditions


import math
import swmm_utils as su
import swmm_graphics as sg
import draw_utils as du
#import SWMMIO
import os
from PIL import Image, ImageDraw


def getUnmatchedElementsInSection (inp1, inp2, section="[CONDUITS]"):

	#used to identify what elements are unique in two similar models,
	#presumably to identify which elements are 'proposed' vs existing

	dict1 = inp1.createDictionary(section)
	dict2 = inp2.createDictionary(section)

	#differ = su.DictDiffer(dict1, dict2)

	#uniqs found with this:
	unmatchedList = list (   set(dict1.keys()) - set(dict2.keys())   )
	return unmatchedList


def joinModelData (model1, model2, bbox=None, joinType='conduit'):

	#joins data from two models in a side by side dictionary
	#presumably, a baseline and a proposed SFR solution


	if joinType == 'conduit':
		
		existingConduits = model1.organizeConduitData(bbox)['conduitDictionaries']
		proposedConduits = model2.organizeConduitData(bbox)['conduitDictionaries'] #proposed as in, the whole system in the proposed conditions

		joinedData = {}
		for conduit, conduitData in proposedConduits.iteritems():

			proposed = conduitData

			lifecycle = 'existing'
			if not conduit in existingConduits:
				#conduit is unique to the proposed system (new infratructure)
				lifecycle = 'new'

			elif proposed['geom1'] != existingConduits[conduit]['geom1']:
				#if this is ID matched one in the existing model
				#and geom 1 changes, this is a replaced/changed pipe
				lifecycle = 'changed'

			existing = existingConduits.get(conduit, {})


			compareDict = {'proposed':proposed, 'existing':existing, 'lifecycle':lifecycle}
			joinedData.update({conduit:compareDict})

	elif joinType == 'node':
	
		existingNodes = model1.organizeNodeData(bbox)['nodeDictionaries']
		proposedNodes = model2.organizeNodeData(bbox)['nodeDictionaries'] #proposed as in, the whole system in the proposed conditions

		joinedData = {}
		for node, nodeData in proposedNodes.iteritems():

			proposed = nodeData

			lifecycle = 'existing'
			if not node in existingNodes:
				#conduit is unique to the proposed system (new infratructure)
				lifecycle = 'new'

			existing = existingNodes.get(node, {})

			compareDict = {'proposed':proposed, 'existing':existing, 'lifecycle':lifecycle}
			joinedData.update({node:compareDict})
	
	elif joinType == 'parcel':
		
		parcels_existing = su.parcel_flood_duration(model1, parcel_features='PWD_PARCELS_SHEDS', 
															threshold=0, bbox=bbox)['parcels']
		parcels_proposed = su.parcel_flood_duration(model2, parcel_features='PWD_PARCELS_SHEDS', 
															threshold=0, bbox=bbox)['parcels']
		
		joinedData = {}
		for parcel, parcel_data in parcels_proposed.iteritems():
		
			proposed = parcel_data
			existing = parcels_existing.get(parcel, {})
			compareDict = {'proposed':proposed, 'existing':existing, 'lifecycle':None}
			joinedData.update({parcel:compareDict})

	return joinedData

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

def drawModelComparison(model1, model2, **kwargs):

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

	joinedConduits = joinModelData(model1, model2, bbox)
	joinedNodes = joinModelData(model1, model2, bbox, joinType='node')

	xplier *= width/1024 #scale the symbology sizes
	width = width*2

	modelSizeDict = su.convertCoordinatesToPixels(joinedConduits, bbox=bbox, targetImgW=width)
	shiftRatio = modelSizeDict['shiftRatio']

	su.convertCoordinatesToPixels(joinedNodes, targetImgW=width, bbox=bbox, shiftRatio=shiftRatio)
	imgSize = modelSizeDict['imgSize']
	if not bbox:
		bbox = modelSizeDict['boundingBox']
	shiftRatio = modelSizeDict['shiftRatio']

	imgSize = [int(x) for x in imgSize]
	img = Image.new('RGB', imgSize, ops['bg'])
	draw = ImageDraw.Draw(img)
	
	#DRAW THE PARCELS
	if ops['parcelSymb']:
		
		joined_parcels = joinModelData(model1, model2, bbox, joinType='parcel')
		#track results
		
		sg.drawParcels(draw, joined_parcels, options=ops['parcelSymb'], bbox=bbox, width=width, shiftRatio=shiftRatio)
	
	if ops['basemap']:
		sg.drawBasemap(draw, img=img, options=ops['basemap'], width=width, bbox=bbox, shiftRatio=shiftRatio, xplier=xplier)

	drawCount = 0
	#DRAW THE CONDUITS
	if ops['conduitSymb']:
		for conduit, conduitData in joinedConduits.iteritems():
			su.drawConduit(conduit, conduitData, draw, ops['conduitSymb'], xplier = xplier)
			drawCount += 1

	#DRAW THE NODES
	if ops['nodeSymb']:
		for node, nodeDict in joinedNodes.iteritems():
			#return nodeDict

			if ('floodDuration' and 'maxDepth' in nodeDict['proposed']) and ('floodDuration' and 'maxDepth' in nodeDict['existing']):
				#this prevents draws if no flow is supplied (RDII and such)
				su.drawNode(node, nodeDict, draw, rpt=None, options=ops['nodeSymb'], dTime=None, xplier=xplier)
				drawCount += 1

	#su.drawAnnotation (draw, model2.inp, imgWidth=width, title=title, objects=[model1.rpt, model2.rpt], symbologyType=conduitSymb, fill=su.black)
	su.annotateMap (draw, model1, model2, options=ops)
	del draw
	#SAVE IMAGE TO DISK
	sg.saveImage(img, model2, imgName)



#end
