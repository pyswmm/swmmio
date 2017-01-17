#graphical functions for SWMM files
from definitions import *
from swmmio.damage import parcels as pdamage
# from swmmio.graphics import draw_utils as du
from swmmio.graphics import config, options
from swmmio.graphics.constants import * #constants
from swmmio.graphics.utils import *
from swmmio.graphics.drawing import *
from swmmio.utils import spatial
# from swmmio import parcels
import pandas as pd
import re
import os
import numpy
from PIL import Image, ImageDraw, ImageFont
import datetime
from datetime import timedelta
from time import gmtime, strftime
import pickle


def _draw_basemap(draw, img, bbox, px_width, shift_ratio):

	for f in options.basemap_options['features']:

		shp_path = os.path.join(config.basemap_shapefile_dir, f['feature'])
		df = spatial.read_shapefile(shp_path)[f['cols']+['coords']]
		df = px_to_irl_coords(df, bbox=bbox, shift_ratio=shift_ratio,
								px_width=px_width)[0]

		if 'ST_NAME' in df.columns:
			#this is a street, draw a polyline accordingly
			df.apply(lambda r: draw.line(r.draw_coords, fill=f['fill']), axis=1)
			annotate_streets(df, img, 'ST_NAME')
		else:
			df.apply(lambda r: draw.polygon(r.draw_coords,
											fill=f['fill']), axis=1)


def draw_model(model=None, nodes=None, conduits=None, parcels=None,
				img_name=None, bbox=None, px_width=2048.0):
	"""
	create a png rendering of the model and model results
	"""

	#gather the nodes and conduits data if a swmmio Model object was passed in
	if model is not None:
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
		_draw_basemap(draw, img, bb, px_width, shift_ratio)

	if config.include_parcels is True:
		par_flood = pdamage.flood_duration(nodes, parcel_node_join_csv=config.parcel_node_join_data)
		par_shp = spatial.read_shapefile(config.parcels_shapefile)
		par_px = px_to_irl_coords(par_shp, bbox=bb, shift_ratio=shift_ratio, px_width=px_width)[0]
		parcels = pd.merge(par_flood, par_px, right_on='PARCELID', left_index=True)
		parcels.apply(lambda row: draw_parcel_risk(row, draw), axis=1)

	#start the draw fest, mapping draw methods to each row in the dataframes
	conduits.apply(lambda row: draw_conduit(row, draw), axis=1)
	nodes.apply(lambda row: draw_node(row, draw), axis=1)

	#SAVE IMAGE TO DISK
	return img
	# save_image(img, model, img_name, imgDir=None)
	# del draw, img
