#graphical functions for SWMM files
from definitions import *
from swmmio.utils import swmm_utils as su
from swmmio.damage import parcels as pdamage
from swmmio.graphics import draw_utils as du
from swmmio.graphics import config, options
from swmmio.graphics.constants import * #constants
from swmmio.graphics.utils import px_to_irl_coords,circle_bbox,read_shapefile,clip_to_box
from swmmio.graphics.drawing import draw_node, draw_conduit, draw_parcel
from swmmio import parcels
import pandas as pd
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

def draw_basemap(draw, img=None, featureDicts=None, options={}, bbox=None,
					shiftRatio=None, width=1024, xplier=1):

	if not featureDicts:
		#generate the dict containing drawable data
		#will return None if probs finding data
		featureDicts = createFeaturesDict(options,  bbox=bbox,
											shiftRatio=shiftRatio,
											width=width)

	anno_streets = []
	#for feature, data in features.iteritems():
	for feature in featureDicts:
		featureDict = feature['featureDict']
		for poly, polyData in featureDict['geometryDicts'].iteritems():
			if polyData['geomType'] == 'polygon':
				draw.polygon(polyData['draw_coordinates'],
							fill=feature['fill'], outline=feature['outline'])

			elif polyData['geomType'] == 'polyline':
				w = int(feature['width']*xplier)
				draw.line(polyData['draw_coordinates'],
							fill=feature['fill'], width=w)
				if 'ST_NAME' in polyData:
					su.annotateLine(img, polyData, annoKey='ST_NAME',
									labeled = anno_streets)

def draw_model(model, img_name=None, bbox=None, px_width=2048.0):
	"""
	create a png rendering of the model and model results
	"""

	#gather the nodes and conduits data
	nodes = model.nodes()
	conduits = model.conduits()

	#antialias X2
	xplier=1
	xplier *= px_width/1024 #scale the symbology sizes
	px_width = px_width*2

	#compute draw coordinates, and the image dimensions (in px)
	conduits, bb, h, w, shift_ratio = px_to_irl_coords(conduits, bbox=bbox, px_width=px_width)
	nodes = px_to_irl_coords(nodes, bbox=bb, px_width=px_width)[0]

	#create the PIL image and draw objects
	img = Image.new('RGB', (w,h), white)
	draw = ImageDraw.Draw(img)

	#draw the basemap if required
	if config.include_basemap is True:
		draw_basemap(draw, img, options=options.basemap_options,
						width=px_width, bbox=bb, shiftRatio=shift_ratio,
						xplier=xplier)

	if config.include_parcels is True:
		par_flood = pdamage.flood_duration(nodes, r"F:\models\SPhila\MasterModels_170104\CommonData\pennsport_sheds_parcels_join_SAMPLE.csv")
		par_shp = read_shapefile(PARCELS_SHAPEFILE)
		par_px = px_to_irl_coords(par_shp, bbox=bb, shift_ratio=shift_ratio, px_width=px_width)[0]
		parcels = pd.merge(par_flood, par_px, right_on='PARCELID', left_index=True)
		parcels.apply(lambda row: draw_parcel(row, draw), axis=1)

	#start the draw fest, mapping draw methods to each row in the dataframes
	conduits.apply(lambda row: draw_conduit(row, draw), axis=1)
	nodes.apply(lambda row: draw_node(row, draw), axis=1)

	#SAVE IMAGE TO DISK
	saveImage(img, model, img_name, imgDir=None)
	# del draw, img
	return conduits
