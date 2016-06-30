#!/usr/bin/env python
#coding:utf-8

#graphical functions for SWMM files
#import swmmio
from swmmio.utils import swmm_utils as su
from swmmio.graphics import draw_utils as du
from swmmio import parcels
import re
import os
import numpy
from PIL import Image, ImageDraw, ImageFont
import datetime
from datetime import timedelta
from time import gmtime, strftime
import pickle



def saveImage(img, model, imgName=None, imgDir=None, antialias=True, open=False, fileExt=".png", verbose=False):

	#get the size from the Image object
	imgSize = (img.getbbox()[2], img.getbbox()[3])

	#if imgName not specified, define as model name
	if not imgName:
		imgName = model.inp.name

	#create the saving location as necessary
	if not imgDir:
		inp = model.inp
		rpt = model.rpt
		standardDir = os.path.join(inp.dir, "img")
		if not os.path.exists(standardDir):
			#if no directory is specified and none exists at
			#standard location create a new directory
			os.makedirs(os.path.join(inp.dir, "img"))
		newFile = os.path.join(standardDir, imgName) + fileExt
	else:
		#imDir is specified by user
		if not os.path.exists(imgDir):
			#if directory doesn't exist, create new
			os.makedirs(imgDir)
		newFile = os.path.join(imgDir, imgName) + fileExt

	if verbose: print "saving image to: " + newFile

	#shrink for antialiasing niceness (though this blows up the file about 5x)
	if antialias:
		size = (int(imgSize[0]*0.5), int(imgSize[1]*0.5))
		img.thumbnail(size, Image.ANTIALIAS)

	img.save(newFile)
	if open:
		os.startfile(newFile)


def createFeaturesDict(options={},  bbox=None, shiftRatio=None, width=1024):

	#create dictionary containing draw coordinate data for the given basemap options

	gdb = options['gdb']
	features = options['features']

	import arcpy
	if arcpy.Exists(gdb):
		#if the gdb exists, then we can move forward
		#for feature, data in features.iteritems():
		for featureOps in features:
			feature = featureOps['feature']
			if arcpy.Exists(os.path.join(gdb, feature)):

				#this check so that we don't repeat this heavy op over an over
				featureDict = su.shape2Pixels(feature, bbox=bbox, targetImgW=width, where=None, cols=featureOps['cols'],
														shiftRatio=shiftRatio, gdb=gdb)

				featureOps.update({'featureDict':featureDict}) #retain this for later if necessary
				#featureOps['featureDict'].update{featureDict}) #retain this for later if necessary
			else:
				print '{} not found'.format(feature)
	else:
		print '{} not found'.format(gdb)
		return None

	return features


def drawParcels(draw, parcel_flooding_results,  options={}, bbox=None, width=1024, shiftRatio=None):

	parcels_pixels = su.shape2Pixels("PWD_PARCELS_SPhila_ModelSpace", where=None,
									cols = ["PARCELID", "SHAPE@"], targetImgW=width,
									shiftRatio=shiftRatio, bbox=bbox)

	#if 'parcels' in parcel_flooding_results:
	#	parcel_flooding_results = parcel_flooding_results['parcels'] #HACKKK
	threshold = options['threshold']
	newflood = moreflood = floodEliminated= floodlowered= 0
	for PARCELID, parcel in parcel_flooding_results.iteritems():
		fill = du.lightgrey #default
		try:
			if parcel.is_delta:
				#we're dealing with "compare" dictionary
				if parcel.delta_type == 'increased_flooding':
					#parcel previously flooded, now floods more
					fill = du.red
					moreflood += 1

				if parcel.delta_type == 'new_flooding':
					#parcel previously did not flood, now floods in proposed conditions
					fill = du.purple
					newflood += 1

				if parcel.delta_type == 'decreased_flooding':
					#parcel flooding problem decreased
					fill =du.lightblue #du.lightgrey
					floodlowered += 1

				if parcel.delta_type == 'eliminated_flooding':
					#parcel flooding problem eliminated
					fill =du.lightgreen
					floodEliminated += 1

			elif parcel.flood_duration > threshold:
				fill = du.col2RedGradient(parcel.flood_duration + 0.5, 0, 3)

			parcel_pix = parcels_pixels['geometryDicts'][PARCELID]
			draw.polygon(parcel_pix['draw_coordinates'], fill=fill, outline=options['outline'])
		except:
			pass

	#print "newflood = {}\nmoreflood={}\nfloodEliminated={}\nfloodlowered={}".format(newflood, moreflood, floodEliminated, floodlowered)
	#saveImage(img, None, imgName=model.inp.name + "_parcels", imgDir=r'C:\Users\Adam.Erispaha\Desktop\S Phila SWMM\img')

def drawBasemap(draw, img=None, featureDicts=None, options={}, bbox=None, shiftRatio=None, width=1024, xplier=1):


	if not featureDicts:
		#generate the dict containing drawable data
		featureDicts = createFeaturesDict(options,  bbox=bbox, shiftRatio=shiftRatio, width=width) #will return None if probs finding data

	#if featureDicts:
	#	features = featureDicts['features']

	polyDrawCount = 0
	anno_streets = []
	#for feature, data in features.iteritems():
	for feature in featureDicts:
		featureDict = feature['featureDict']
		for poly, polyData in featureDict['geometryDicts'].iteritems():
			if polyData['geomType'] == 'polygon':
				draw.polygon(polyData['draw_coordinates'], fill=feature['fill'], outline=feature['outline'])
				polyDrawCount += 1

			elif polyData['geomType'] == 'polyline':

				draw.line(polyData['draw_coordinates'], fill=feature['fill'], width=feature['width']*xplier)
				if 'ST_NAME' in polyData:
					su.annotateLine(img, polyData, annoKey='ST_NAME', labeled = anno_streets)
					polyDrawCount += 1

def drawModel (model, **kwargs):

	#unpack and update the options
	ops = du.default_draw_options()
	for key, value in kwargs.iteritems():
		ops.update({key:value})
	#return ops
	width = ops['width']
	xplier = ops['xplier']
	bbox = ops['bbox']
	imgName = ops['imgName'] # for some reason saveImage() won't take the dict reference
	imgDir = ops['imgDir'] # for some reason saveImage() won't take the dict reference

	focusConduits = []
	for node in ops['traceUpNodes']:
		#return list of elements upstream of node
		focusConduits += su.traceFromNode(model, node, mode='up')['conduits']

	for node in ops['traceDnNodes']:
		#return list of elements downstream of node
		focusConduits += su.traceFromNode(model, node, mode='down')['conduits']

	#antialias X2
	xplier *= width/1024 #scale the symbology sizes
	width = width*2

	#parse out the main objects of this model
	inp = model.inp
	rpt = model.rpt

	#organize relavant data from SWMM files, #FIX TO NOT RUN ALL THIS IF NOT NECESSARY
	conduitData = model.organizeConduitData(bbox) #dictionary of overall model data, dimension, and the conduit dicts
	conduits = conduitData['conduit_objects']
	pixelData = su.convertCoordinatesToPixels(conduits, targetImgW=width, bbox=bbox)
	shiftRatio = pixelData['shiftRatio']
	imgSize = pixelData['imgSize']

	if not bbox:
		bbox = pixelData['boundingBox'] #this is the box tightly wrapping all conduits, will be <= the user provided bbox

	#node data
	nodeData = model.organizeNodeData(bbox)
	nodes = nodeData['node_objects']
	su.convertCoordinatesToPixels(nodes, targetImgW=width, bbox=bbox)

	img = Image.new('RGB', imgSize, ops['bg'])
	draw = ImageDraw.Draw(img)

	anno_results = {}

	#DRAW THE PARCELS
	if ops['parcelSymb']:

		#grab the parcel&node dict that associates node IDs to each parcel
		parcel_flooding_results = parcels.parcel_flood_duration(model, parcel_features=ops['parcelSymb']['feature'],
															threshold=ops['parcelSymb']['threshold'],
															gdb= ops['parcelSymb']['gdb'], bbox=None,
															anno_results=anno_results)

		drawParcels(draw, parcel_flooding_results['parcels'], options=ops['parcelSymb'], bbox=bbox, width=width, shiftRatio=shiftRatio)

	#DRAW THE BASEMAP
	if ops['basemap']:
		drawBasemap(draw, img=img, options=ops['basemap'], width=width, bbox=bbox, shiftRatio=shiftRatio, xplier = xplier)

	drawCount = 0

	#DRAW THE CONDUITS
	if ops['conduitSymb']:
		for id, conduit in conduits.iteritems():

			if conduit.coordinates: #has coordinate? draw. protect from rdii junk
				su.drawConduit(conduit, draw, ops['conduitSymb'], rpt=rpt, xplier = xplier, highlighted=focusConduits)
				drawCount += 1

	#DRAW THE NODES
	if ops['nodeSymb']:
		for id, node in nodes.iteritems():
			if node.coordinates: #this prevents draws if no flow is supplied (RDII and such)
				#drawNode(node, draw, options, rpt=None, dTime=None, xplier=1):
				su.drawNode(node, draw, rpt=rpt, options=ops['nodeSymb'], dTime=None, xplier=xplier)
				drawCount += 1


	#if conduitDrawCount > 0 and conduitDrawCount % 2000 == 0: print str(conduitDrawCount) + " pipes processed "
	su.annotateMap (draw, model, options=ops, results=anno_results)
	del draw, ops

	#SAVE IMAGE TO DISK
	saveImage(img, model, imgName, imgDir=imgDir)



def drawProfile (model, upNode=None, dnNode=None, imgName=None, imgDir=None, width = 1024, height=512, drawSizeMultiplier = .01,
				bgroundColor=(0,3,18), bbox = None, conduitSubset = None, extraData=None):


	w = width*2
	h = height*2
	if upNode:
		#trace from up node to downstream stop node
		traced = su.traceFromNode(model, startNode=upNode, mode='down', stopnode=dnNode)
		conduitSubset = traced['conduits']
		nodeSubset = traced['nodes']

	#match the coordinates for each conduit
	conduitData = model.organizeConduitData(subset = conduitSubset)
	nodeData = model.organizeNodeData(subset=nodeSubset)
	conduits = conduitData['conduit_objects']
	nodes = nodeData['node_objects']
	minEl = nodeData['minEl']
	maxEl = nodeData['maxEl']
	reachLength = su.length_of_conduits(conduits)

	#transform
	profileHeight = maxEl - minEl

	sX = w / reachLength # to scale down from coordinate to pixels
	sY = h / profileHeight # to scale down from coordinate to pixels

	print w, " x " , h
	print 'profileHeight = ', profileHeight
	print "minEl = ",  minEl
	print "maxEl = ",  maxEl
	print "shiftRatioY = ",  sY
	print "shiftRatioX = ",  sX
	print 'reachLength = ', reachLength

	#return nodes
	img = Image.new('RGB', (w, h))
	draw = ImageDraw.Draw(img)
	x=0 #starting x location
	print '{}, {}, {}, {}, {}, {}'.format('conduit.id', 'x', 'upinvert', 'crown', 'flood_el', 'dnnode.maxHGL')
	for c in conduitSubset:

		#collect data about the curren conduit
		conduit = conduits[c]#grab object from dict\
		l = conduit.length
		upnode = nodes[conduit.upNodeID]
		dnnode = nodes[conduit.downNodeID]

		upfloodel = upnode.invert + upnode.maxDepth
		dnfloodel = dnnode.invert + dnnode.maxDepth

		inletoffset = conduit.inletoffset
		outletoffset = conduit.outletoffset
		geom1 = conduit.geom1
		upcondinv = upnode.invert + inletoffset
		dncondinv = dnnode.invert + outletoffset

		#compute the draw coordinates for each line segment
		upcondinvxy = su.coordToDrawCoord((x, upcondinv),shiftRatio=sX, shiftRatioY=sY, width=w, height=h)
		dncondinvxy = su.coordToDrawCoord((x+l, dncondinv),shiftRatio=sX, shiftRatioY=sY, width=w, height=h)
		#s = '{}: x={} upinv={}, dninv={}, uppeak={}, downpk={}'.format(conduit.id,x, upnode.invert, dnnode.invert, upnode.maxHGL, dnnode.maxHGL)
		s = '{}, {}, {}, {}, {}, {}'.format(conduit.id,x, upcondinv, upcondinv + geom1, upfloodel, upnode.maxHGL)
		x += l
		#print s
		print (upcondinvxy, dncondinvxy)
		draw.line((upcondinvxy, dncondinvxy), fill = (200, 200, 200), width = 2)



		#coordToDrawCoord(coordinates, bbox=None, shiftRatio=None, width=None, height=None)

	print '{}, {}, {}, {}, {}, {}'.format(conduit.id,x, upcondinv, upcondinv + geom1, upfloodel, upnode.maxHGL)
	saveImage(img, model, imgName)
		#draw bottom of current conduit
		#coords = None
		#dr_inv_coords = su.coordToDrawCoord(coordinates, bbox=None, shiftRatio=None, width=None, height=None)



	# for conduitID, data in conduiteElevationDicts.iteritems():
	#
	# 	#print data
	# 	drawLength = round(data['length'] * shiftRatioX, 5)
	# 	#need to shirt the x n y components of the length
	#
	# 	inv1 =		round((maxEl - data['upstreamEl']) * shiftRatioY, 5) #subtract from height because PIL origin is in top right
	# 	inv2 = 		round((maxEl - data['downstreamEl'])  * shiftRatioY, 5)  #subtract from height because PIL origin is in top right
	# 	HGL1 = 		round((maxEl - data['maxHGLUpstream']) * shiftRatioY, 5)
	# 	HGL2 = 		round((maxEl - data['maxHGLDownstream']) * shiftRatioY, 5)
	# 	upFloodEl = None
	# 	dnFloodEl = None
	# 	if extraData and data['upFloodEl'] and data['dnFloodEl']:
	# 		upFloodEl = round((data['upFloodEl']) * shiftRatioY, 5)
	# 		dnFloodEl = round((data['dnFloodEl']) * shiftRatioY, 5)
	#
	# 	tranformedDictItems = {'drawLength':drawLength, 'inv1':inv1, 'inv2':inv2, 'HGL1':HGL1, 'HGL2':HGL2, 'upFloodEl':upFloodEl, 'dnFloodEl':dnFloodEl}
	#
	#
	# 	#coordPairDict.update(tranformedDictItems)
	# 	data.update(tranformedDictItems)
	#
	#
	# print "new size X2 = " , modelSize
	# print "startingConduitID = " + startingConduitID
	# img = Image.new('RGB', (width, height), bgroundColor)
	# draw = ImageDraw.Draw(img)
	#
	# #draw conduits from the starting pipe
	# conduit = conduiteElevationDicts[startingConduitID]
	# #print conduit
	# x1 = 0
	# terminalFound = False
	#
	#
	# while not terminalFound:
	#
	# 	#loop through conduits, switching to each conduit via the "downID"
	# 	#stop when the t
	# 	length = conduit['drawLength']
	# 	inv1 = conduit['inv1']
	# 	inv2 = conduit['inv2']
	# 	HGL1 = conduit['HGL1']
	# 	HGL2 = conduit['HGL2']
	# 	upFloodEl = conduit['upFloodEl']
	# 	dnFloodEl = conduit['dnFloodEl']
	#
	# 	geom1 = float(conduit['geom1']) * shiftRatioY
	# 	x2 = length + x1 #du.getX2(inv1, inv2, length, x1)
	# 	invCoordPair = [(x1, inv1), (x2, inv2)] #coordPairs for the pipe invert
	# 	crwnCoordPair = [(x1, inv1-geom1), (x2, inv2-geom1)] #coordPairs for the pipe crown
	# 	HGLCoordPair = [(x1, HGL1), (x2, HGL2)] #coordPairs for the HGL
	# 	#print invCoordPair
	# 	draw.line(invCoordPair, fill = (200, 200, 200), width = 2)
	# 	draw.line(crwnCoordPair, fill = (200, 200, 200), width = 2)
	# 	draw.line(HGLCoordPair, fill = (10, 120, 250), width = 2)
	#
	# 	if upFloodEl and dnFloodEl:
	# 		floodElCoordPair = [(x1, inv1-upFloodEl), (x2, inv2-dnFloodEl)] #coordPairs for the pipe crown
	# 		draw.line(floodElCoordPair, fill = (30, 250, 130), width = 2)
	#
	#
	# 	nextConduitID = conduit['downID']
	# 	if nextConduitID:
	# 		#advance to next reach downstream, if a downID exists
	# 		x1 = x2 #increment the x starting point for the next conduit
	# 		#print str(conduit) + " to " + str([conduit['downID']])
	# 		conduit = conduiteElevationDicts[nextConduitID]
	# 	else:
	# 		terminalFound = True
	# 		#print "terminal" + str(conduit)
	#
	#
	# del draw
	#
	# newFile = os.path.join(imgDir, imgName) + ".png"
	# print newFile
	#
	#
	# #shrink for antialiasing niceness (though this blows up the file about 5x)
	# size = (int(width*0.5), int(height*0.5))
	# img.thumbnail(size, Image.ANTIALIAS)
	#
	# img.save(newFile)
	# os.startfile(newFile)
	# #return conduiteElevationDictss
