"""
OLD JUNKY CODE, KEPT FOR HERE REFERENCE FOR A BIT. WILL BE REMOVED FROM REPO
IN FUTURE RELEASES
"""


def drawParcels(draw, parcel_flooding_results,  options={}, bbox=None, width=1024, shiftRatio=None):

	parcels_pixels = su.shape2Pixels("PWD_PARCELS_SPhila_ModelSpace", where=None,
									cols = ["PARCELID", "SHAPE@"], targetImgW=width,
									shiftRatio=shiftRatio, bbox=bbox)

	#if 'parcels' in parcel_flooding_results:
	#	parcel_flooding_results = parcel_flooding_results['parcels'] #HACKKK
	threshold = options['threshold']
	newflood = moreflood = floodEliminated= floodlowered= 0
	for PARCELID, parcel in parcel_flooding_results.iteritems():
		fill = lightgrey #default
		try:
			if parcel.is_delta:
				#we're dealing with "compare" dictionary
				if parcel.delta_type == 'increased_flooding':
					#parcel previously flooded, now floods more
					fill = red
					moreflood += 1

				if parcel.delta_type == 'new_flooding':
					#parcel previously did not flood, now floods in proposed conditions
					fill = purple
					newflood += 1

				if parcel.delta_type == 'decreased_flooding':
					#parcel flooding problem decreased
					fill = lightblue #du.lightgrey
					floodlowered += 1

				if parcel.delta_type == 'eliminated_flooding':
					#parcel flooding problem eliminated
					fill = lightgreen
					floodEliminated += 1

			elif parcel.flood_duration > threshold:
				fill = gradient_color_red(parcel.flood_duration + 0.5, 0, 3)

			parcel_pix = parcels_pixels['geometryDicts'][PARCELID]
			draw.polygon(parcel_pix['draw_coordinates'], fill=fill, outline=options['outline'])
		except:
			pass

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


def elementChange(elementData, parameter='maxflow'):

	#with a joined dictionary item, returns change from existing to proposed

	proposedVal = elementData['proposed'].get(parameter, 0.0)
	existingVal = elementData['existing'].get(parameter, 0.0)

	return proposedVal - existingVal


def drawNode(node, draw, options, rpt=None, dTime=None, xplier=1):

	color = (210, 210, 230) #default color
	radius = 0 #aka don't show this node by default
	outlineColor = None
	xy = node.draw_coordinates #(node.X_px, node.Y_px)
	threshold = options['threshold']
	type = options['type']
	if dTime:

		data = rpt.returnDataAtDTime(node.id, dTime, sectionTitle="Node Results")
		q = abs(float(data[2])) #absolute val because backflow
		floodingQ = float(data[3])
		HGL = float(data[5])

		if type=='flood':

			#node params
			if floodingQ > 1:
				radius = q/2
				color = red #greenRedGradient(HGLup, 0, 15) #color

	elif node.is_delta:
		#we're dealing with "compare" object
		#floodDurationChange = elementChange(node, parameter='floodDuration')

		if node.flood_duration > 0 :
			#Flood duration increases
			radius = node.flood_duration*20
			color = red

		#if nodeData['existing'].get('floodDuration', 0) == 0 and nodeData['proposed'].get('floodDuration', 0) > 0:
		if node.delta_type == 'new_flooding':
			#new flooding found
			radius = node.flood_duration*20
			color = purple #purple
			outlineColor = (90, 90, 90)

	else:
		floodDuration = node.flood_duration
		maxDepth = node.maxDepth
		maxHGL = node.maxHGL

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
	draw.ellipse(circleBBox(xy, radius), fill =color, outline=outlineColor)

def drawConduit(conduit, draw, options, rpt=None, dTime = None, xplier = 1, highlighted=None):

	#Method for drawing (in plan view) a single conduit, given its RPT results

	#default fill and size
	fill = (120, 120, 130)
	drawSize = 1
	should_draw = True #boolean that can prevent a draw based on params
	coordPair = conduit.draw_coordinates
	type = options['type']
	#general method for drawing one conduit
	if rpt:
		#if an RPT is supplied, collect the summary data
		maxQPercent = conduit.maxQpercent
		q =  conduit.maxflow

		if maxQPercent !=0:
			capacity = q / maxQPercent
		else:
			capacity = 1
		stress = q / capacity

		if dTime:
			#if a datetime is provided, grab the specif flow data at this time
			data = rpt.returnDataAtDTime(conduit.id, dTime) #this is slow
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

	elif conduit.is_delta:
		#we're dealing with "compare" dictionary
		qChange = 	conduit.maxflow #elementChange(conduitData, parameter='maxflow')
		maxQperc = 	conduit.maxQpercent #elementChange(conduitData, parameter='maxQpercent')

		#default draw behavoir = draw grey lines proportional to geom1
		drawSize = min(7, conduit.geom1*0.7)
		fill = du.mediumgrey
		# #FIRST DRAW NEW OR CHANGED CONDUITS IN A CLEAR WAY
		# if conduit.lifecycle == 'new':
		# 	fill = blue
		# if conduit.lifecycle == 'changed':
		# 	fill = green #blue
			#drawSize = min(10, conduit.geom1)

		#IF THE CONDUITS IS 'EXISTING', DISPLAY SYMBOLOGY ACCORDINGLY (how things changed, etc)
		if conduit.lifecycle == 'existing':

			if type == 'proposed_simple':
				#drawSize = 0 #don't draw, only print the proposed infrastructure
				#fill = red
				#should_draw = False
				pass
			if type == 'compare_flow':
				drawSize = options['draw_size'](abs(qChange*options['xplier']), options['exp'])
				if qChange > 0:
					fill = du.greyRedGradient(qChange+15, 0, 20)
					#drawSize = int(round(math.pow(qChange, 0.67)))

				if qChange <= 0:
					fill = du.greyGreenGradient(abs(qChange)+15, 0, 20)
					#drawSize = int(round(math.pow(abs(qChange), 0.67)))

			if type == 'compare_hgl':

				avgHGL = (conduit.maxHGLUpstream + conduit.maxHGLDownstream) / 2.0
				drawSize = options['draw_size'](abs(avgHGL*options['xplier']), options['exp'])
				if avgHGL > 0:
					fill = du.red #du.greyRedGradient(avgHGL+15, 0, 20)
					#drawSize = int(round(math.pow(avgHGL, 1)))

				if avgHGL <= 0:
					fill = du.green_bright #du.greyGreenGradient(abs(avgHGL)+15, 0, 20)
					#drawSize = int(round(math.pow(avgHGL, 1)))


	#if highlighted list is provided, overide any symbology for the highlighted conduits
	if highlighted and conduit.id in highlighted:
		fill = blue
		drawSize = 3
	#FIRST DRAW NEW OR CHANGED CONDUITS IN A CLEAR WAY
	if conduit.lifecycle == 'new':
		fill = blue
	if conduit.lifecycle == 'changed':
		fill = green #blue
	drawSize = int(drawSize*xplier)


	if should_draw:
		#draw that thing
		draw.line(coordPair, fill = fill, width = drawSize)
		if pipeLengthPlanView(coordPair[0], coordPair[1]) > drawSize*0.75:
			#if length is long enough, add circles on the ends to smooth em out
			#this check avoids circles being drawn for tiny pipe segs
			draw.ellipse(du.circleBBox(coordPair[0], drawSize*0.5), fill =fill)
			draw.ellipse(du.circleBBox(coordPair[1], drawSize*0.5), fill =fill)



"""
FROM THE OLD draw_utils.py module
"""
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
