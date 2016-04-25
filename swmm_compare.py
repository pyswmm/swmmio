#SWMM Compare - methods to compare rpt files 

#for the purposes of this code, "existing" means 'existing system' as in, the existing conditions model
#whereas "proposed" means proposes system, as in, the model representing the system in the proposed conditions


import math
import swmm_utils as su
import swmm_graphics as sg
#import SWMMIO
import os
from PIL import Image, ImageDraw
import webbrowser #to open images (seems dumb to have to use this)

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
		conduitDict1 = model1.organizeConduitData(bbox)
		conduitDict2 = model2.organizeConduitData(bbox)
		
		existingConduits = conduitDict1['conduitDictionaries']
		proposedConduits = conduitDict2['conduitDictionaries'] #proposed as in, the whole system in the proposed conditions
		
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
		nodeDict1 = model1.organizeNodeData(bbox)
		nodeDict2 = model2.organizeNodeData(bbox)
		
		existingNodes = nodeDict1['nodeDictionaries']
		proposedNodes = nodeDict2['nodeDictionaries'] #proposed as in, the whole system in the proposed conditions
		
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
	
	
	return joinedData
	
def differenceBetweenConduits(conduitDict1, conduitDict2):
	
	#return a dictionary with the difference in values in conduitDict1 and 2
	diff = {
		'downstreamEl':			conduitDict1['downstreamEl'] - 		conduitDict2['downstreamEl'], 
		'geom1': 				conduitDict1['geom1'] - 			conduitDict2['geom1'], 
		'maxDpercent': 			conduitDict1['maxDpercent'] - 		conduitDict2['maxDpercent'], 
		'maxHGLDownstream': 	conduitDict1['maxHGLDownstream'] - 	conduitDict2['maxHGLDownstream'], 
		'maxHGLUpstream': 		conduitDict1['maxHGLUpstream'] - 	conduitDict2['maxHGLUpstream'], 
		'maxQpercent': 			conduitDict1['maxQpercent'] - 		conduitDict2['maxQpercent'], 
		'upstreamEl': 			conduitDict1['upstreamEl'] - 		conduitDict2['upstreamEl'], 
		'maxDepthUpstream': 	conduitDict1['maxDepthUpstream'] - 	conduitDict2['maxDepthUpstream'], 
		'maxflow': 				conduitDict1['maxflow'] - 			conduitDict2['maxflow'], 
		'maxDepthDownstream':	conduitDict1['maxDepthDownstream']-	conduitDict2['maxDepthDownstream']
		}
	
	return diff


def compareModelResults(model1, model2, bbox=None, parameter='floodDuration', joinType='node'):
	
	outFilePath = os.path.join(model2.inp.dir, model2.inp.name) + "_" + parameter + "_change.csv"
	joinedData = joinModelData(model1, model2, bbox=bbox, joinType=joinType)
	
	with open(outFilePath, 'w') as file:
		
		header = "id, " + parameter + "_change, " + "lifecycle," + "comment"
		file.write("%s\n" % header)
		for element, data in joinedData.iteritems():
			
			change = su.elementChange(data, parameter=parameter)
			line = element + ", " + str(change) + ", " + data['lifecycle']
			
			if data['existing'].get('floodDuration', 0) == 0 and data['proposed'].get('floodDuration', 0) > 0:
				line += ", newflooding"
			
			file.write("%s\n" % line)
		
	#outFile.close()
	
	return outFilePath

def comparisonReport (model1, model2, bbox=None, durationfloor=0.083):
	
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
		
		if existingFloodD == 0 and proposedFloodD > durationfloor:
			nodesFloodNew += 1
		
		if proposedFloodD == 0 and existingFloodD > durationfloor:
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
	
def drawModelComparison(imgName, model1, model2, imgDir=None, bg = su.white,  
					width = 1024, bbox=None, conduitSymb='compare_hgl',
					title=None, xplier=0.3,  basemap=True, nodeSymb='flood'):
	
	
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
	img = Image.new('RGB', imgSize, bg) 
	draw = ImageDraw.Draw(img) 
	
	if basemap:
		sg.drawBasemap(draw, width=width, bbox=bbox, shiftRatio=shiftRatio)
	
	drawCount = 0
	#DRAW THE CONDUITS
	if conduitSymb:
		for conduit, conduitData in joinedConduits.iteritems():
				
			su.drawConduit(conduit, conduitData, draw, type=conduitSymb, xplier=xplier)	
			drawCount += 1
	
	#DRAW THE NODES
	if nodeSymb:
		for node, nodeDict in joinedNodes.iteritems():
			#return nodeDict
			
			if ('floodDuration' and 'maxDepth' in nodeDict['proposed']) and ('floodDuration' and 'maxDepth' in nodeDict['existing']): 
				#this prevents draws if no flow is supplied (RDII and such)
				su.drawNode(node, nodeDict, draw, rpt=None, dTime=None, type=nodeSymb, xplier=xplier)
				drawCount += 1
	
	su.drawAnnotation (draw, model2.inp, imgWidth=width, title=title, objects=[model1.rpt, model2.rpt], symbologyType=conduitSymb, fill=su.black)	
	del draw
	#SAVE IMAGE TO DISK
	sg.saveImage(img, model2, imgName)
	
	
	
#import the inps and sift the the conduit dictionaries,
#for each conduit in rpt1, check if the matching conduit 
#in rpt2 is greater in flow or whatever. 
#create maybe a dictionary of conduits where certain things happend 
#(e.g. increase in flow), create a log of this info, create an image highlighting these pipes

"""
	compare = SWMM_Compare.compareRPTs(inp1, inp2, rpt1, rpt2)

	for conduit, data in compare.iteritems():
	proposedQ = data['proposed'].get('maxflow', None)
	existingQ = data['existing'].get('maxflow', None)
	if proposedQ and existingQ:
		if proposedQ < existingQ:
			print conduit
"""