#module to contain general function pertaining to graphics, (colors, PIL stuff, constants, and options)
#drawing options
import math
from swmmio.graphics import config
from definitions import PARCEL_FEATURES, GEODATABASE
#COLOR DEFS
red = 		(250, 5, 5)
blue = 		(5, 5, 250)
lightblue = (184, 217, 242)
shed_blue = (0,169,230)
white =		(250,250,240)
black = 	(0,3,18)
mediumgrey = (190, 190, 180)
lightgrey = (235, 235, 225)
grey = 		(100,95,97)
park_green = (115, 178, 115)
green = 	(115, 220, 115)
green_bright= (23, 191, 23)
lightgreen = (150,212,166)
water_grey = (130, 130, 130)
purple = (250, 0, 250)


def basemap_options(**kwargs):
	basemap_options = {
    'gdb': GEODATABASE,
    'features': [
		#this is an array so we can control the order of basemap layers
        # {
            # 'feature': 'D68_Dissolve',
            # 'fill': None,
            # 'outline': su.shed_blue,
            # 'featureDict': None,
            # 'cols': ["OBJECTID", "SHAPE@"]
		# },
        # {
            # 'feature': 'PWD_PARCELS_SPhila_ModelSpace',
            # 'fill': su.lightgrey,
            # 'outline': None,
            # 'featureDict': None,
            # 'cols': ["OBJECTID", "SHAPE@"]
		# },
		# {
            # 'feature': 'SouthPhilaModelExtents',
            # 'fill': su.shed_blue,
            # 'outline': None,
            # 'featureDict': None,
            # 'cols': ["OBJECTID", "SHAPE@"]
		# },
		# {
            # 'feature': 'detailedsheds',
            # 'fill': None,
            # 'outline': su.red,
            # 'featureDict': None,
            # 'cols': ["OBJECTID", "SHAPE@"]
		# },

		{
            'feature': 'PhiladelphiaParks',
            'fill': park_green,
            'outline': None,
            'featureDict': None,
            'cols': ["OBJECTID", "SHAPE@"]
		},
        {
            'feature': 'HydroPolyTrim',
            'fill':water_grey,
            'outline': None,
            'featureDict': None,
            'cols': ["OBJECTID", "SHAPE@"]
		},
        {
            'feature': 'Streets_Dissolved5_SPhilly',
            'fill': lightgrey,
            'width': 0,
            'fill_anno': grey,
            'outline': None,
            'featureDict': None,
            'cols': ["OBJECTID", "SHAPE@", "ST_NAME"]
		}
      ],
	}
	feats = []
	for key, value in kwargs.iteritems():
		basemap_options.update({key:value})

	return basemap_options
def conduit_options(type, **kwargs):
	#drawing options for conduits
	conduit_def_symbologies = {
		'stress': {
			'title': 'Condiut Stress',
			'description': 'Shows how taxed conduits are based on their flow (peak flow) with respect to their full-flow capacity',
			'threshold': 1,#fraction used
			'type': 'stress',
			'fill':greyRedGradient,
			'draw_size':line_size,
			'exp':0.8,
			'xplier':10
		},
		'compare_flow': {
			'title': 'Flow Comparison',
			'description': 'Shows the change in peak flows in conduits between a baseline and proposed model',
			'type': 'compare_flow',
			'fill':greyRedGradient,
			'draw_size':line_size,
			'exp':0.67,
			'xplier':1
		},
		'compare_hgl': {
			'title': 'HGL Comparison',
			'description': 'Shows the change in HGL in conduits between a baseline and proposed model',
			'type': 'compare_hgl',
			'fill':greyRedGradient,
			'draw_size':line_size,
			'exp':1,
			'xplier':10
		},
		'proposed_simple': {
			'title': 'Proposed Infrastructure',
			'description': 'Shows the new infrastructure only',
			'type': 'proposed_simple',
			'fill':blue
		},
		'capacity_remaining': {
			'title': 'Remaining Capacity',
			'description': 'Shows the amount of full flow capacity remaining in conduits',
			'type': 'capacity_remaining',
			'fill':blue,
			'draw_size':line_size,
			'exp':0.75,
			'xplier':1
		},
		'flow': {
			'title': 'Condiut Flow',
			'description': 'Shows the flow in conduits with proportional ine weight',
			'type': 'flow',
			'fill':blue,
			'draw_size':line_size,
			'exp':0.67,
			'xplier':1
		},
		'flow_stress': {
			'title': 'Condiut Flow & Stress',
			'description': 'Shows the flow in conduits with line weight and color based on "stress" (flow/full-flow capacity)',
			'type': 'flow_stress',
			'fill':greenRedGradient,
			'draw_size':line_size,
			'exp':0.67,
			'xplier':1
		},
		'trace': {
			'title': 'Trace Upstream',
			'description': '',
			'type': 'trace'
		}
	}

	selected_ops = conduit_def_symbologies[type]
	for key, value in kwargs.iteritems():
		selected_ops.update({key:value})

	return selected_ops
def node_options(type='flood', **kwargs):

	#drawing options for conduits
	node_symbologies = {
		'flood': {
			'title': 'Node Flood Duration',
			'description': 'Shows the node duration proporationally in size',
			'threshold': 0.083,#minutes,
			'fill': red,
			'type': 'flood'
		},
		'flood_color': {
			'title': 'Node Flood Duration',
			'description': 'Shows the node duration via color gradient in size',
			'threshold': 0.083,#minutes,
			'fill':greenRedGradient,
			'type': 'flood_color'
		}
	}

	selected_ops = node_symbologies[type]
	for key, value in kwargs.iteritems():
		selected_ops.update({key:value})

	return selected_ops
def parcel_options(type='flood', **kwargs):

	#drawing options for conduits
	parcel_symbologies = {
		'flood': {
				'title': 'Parcel Flood Duration',
				'description': 'Shows the parcels flood duration severity based on color',
				'threshold': 0.08333,
				'delta_threshold':0.25,
				'fill': red,
				'outline': None,
				'type': 'flood',
				'feature':PARCEL_FEATURES,
				'gdb':GEODATABASE
				},
		'compare_flood': {
				'title': 'Parcel Flood Change',
				'description': 'Shows the parcels flood duration severity based on color',
				'threshold': 0.08333,
				'delta_threshold':0.25,
				'fill': red,
				'outline': None,
				'type': 'compare_flood',
				'feature':PARCEL_FEATURES,
				'gdb':GEODATABASE
				}
			}

	selected_ops = parcel_symbologies[type]
	for key, value in kwargs.iteritems():
		selected_ops.update({key:value})

	return selected_ops
def default_draw_options():
	
	if config.include_basemap:
		basemap_symbology = basemap_options()
	else:
		basemap_symbology = None

	if config.include_parcels:
		parcels_symbology = parcel_options('flood')
	else:
		parcels_symbology = None

	default_options = {
		'width': 2048,
		'bbox':None,
		'imgName':None,
		'imgDir':None,
		'nodeSymb': node_options('flood'),
		'conduitSymb': conduit_options('stress'),
		'basemap': basemap_symbology,
		'parcelSymb': parcels_symbology,
		'bg': white,
		'xplier': 1,
		'traceUpNodes': [],
		'traceDnNodes': [],
		'fps': 7.5,
		'title': None
	}
	return default_options


#DRAWING UTILITY FUNCTIONS
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
def line_size(q, exp=1):
	return int(round(math.pow(q, exp)))

#geometry related functions
def circleBBox(coordinates, radius):
	#returns the bounding box of a circle given as centriod coordinate and radius
	x = coordinates[0] #this indexing is because other elements haev more than on coordinate (ulgy pls fix)
	y = coordinates[1]
	r = radius

	return (x-r, y-r, x+r, y+r)

def getX2(y1, y2, length, x1=0):

	#return the x2 coordinate given y1, y2, the line segment length, and x0

	a = y2 - y1
	c = length
	return math.sqrt(c*c - a*a) + x1
