"""
Functions to produce animations of SWMM results. Not working currently - need to
bring the Link / Node object usage up to speed
"""

from swmmio.graphics import swmm_graphics as sg
from swmmio.graphics import draw_utils as du
from swmmio.utils import swmm_utils as su
from swmmio.vendor.images2gif import writeGif
from PIL import Image, ImageDraw, ImageFont
import shutil
from datetime import datetime, timedelta
from time import strftime
import glob
import os
import pickle

def animateModel(model, startDtime=None, endDtime=None, **kwargs):

	"""
	FUNCTION NOT CURRENTLY SUPPORTED ! :(
	"""
	#unpack and update the options
	ops = du.default_draw_options()
	for key, value in kwargs.items():
		ops.update({key:value})
	#return ops
	width = ops['width']
	xplier = ops['xplier']
	bbox = ops['bbox']
	imgName = ops['imgName'] # for some reason saveImage() won't take the dict reference

	#for antialiasing, double size for now
	xplier *= width/1024 #scale the symbology sizes
	width = width*2

	#parse out the main object of this model
	inp = model.inp
	rpt = model.rpt

	#organize relavant data from SWMM files
	conduitData = model.organizeConduitData(bbox) #dictionary of overall model data, dimension, and the conduit dicts
	conduitDicts = conduitData['conduit_objects']
	pixelData = su.convertCoordinatesToPixels(conduitDicts, targetImgW=width, bbox=bbox)
	shiftRatio = pixelData['shiftRatio']
	imgSize = pixelData['imgSize']
	#node data
	nodeData = model.organizeNodeData(bbox)
	nodeDicts = nodeData['node_objects']
	su.convertCoordinatesToPixels(nodeDicts, targetImgW=width, bbox=bbox)

	#grab start and end simulation time if no range provided -> this will be huge if you're not careful!
	if not startDtime: startDtime = rpt.simulationStart
	if not endDtime: endDtime = rpt.simulationEnd

	#make sure dates are valid (within range)
	simStartDT = datetime.strptime(rpt.simulationStart, "%b-%d-%Y %H:%M:%S") #lower bound of time
	simEndDT = datetime.strptime(rpt.simulationEnd, "%b-%d-%Y %H:%M:%S") #upper bound of time
	if startDtime and endDtime:
		userStartDT = 	datetime.strptime(startDtime, "%b-%d-%Y %H:%M:%S")
		userEndDT = 	datetime.strptime(endDtime, "%b-%d-%Y %H:%M:%S")
		timeStepMod = userStartDT.minute % rpt.timeStepMin
		if userStartDT < simStartDT or userEndDT > simEndDT or timeStepMod != 0 or userEndDT < userStartDT:
			#user has entered fault date times either by not being within the
			#availble data in the rpt or by starting at something that doesn't fit the timestep
			print("PROBLEM WITH DATETIME ENTERED. Make sure it fits within data and start time rest on factor of timestep in minutes.")
			print("userStartDT = ", userStartDT, "\nuserEndDT = ", userEndDT, "\nsimStartDT = ", simStartDT, "\nsimEndDT = ", simEndDT, "\nTIMESTEP = ", rpt.timeStepMin)
			return None

	currentT = datetime.strptime(startDtime, "%b-%d-%Y %H:%M:%S") #SWMM dtime format needed
	endDtime = datetime.strptime(endDtime, "%b-%d-%Y %H:%M:%S") #SWMM dtime format needed
	delta = timedelta(minutes=rpt.timeStepMin) #SWMM reporting time step (or step to animate with)


	#use or create working dir
	if not os.path.exists( os.path.join(inp.dir, "img") ):
		os.makedirs(os.path.join(inp.dir, "img"))
	imgDir = os.path.join(inp.dir, "img")

	byteLocDictionaryFName = os.path.join(imgDir, inp.name) + "_rpt_key.txt"
	if not os.path.isfile(byteLocDictionaryFName):

		#this is a heavy operation, allow a few minutes
		print("generating byte dictionary...")
		#conduitByteLocationDict = rpt.createByteLocDict("Link Results")
		rpt.createByteLocDict("Link Results")
		rpt.createByteLocDict("Node Results")

		#save dict to disk
		dictSaveFile =  open (byteLocDictionaryFName, 'w')
		pickle.dump(rpt.elementByteLocations, dictSaveFile)
		dictSaveFile.close()

	else:
		#print "loading byte dict"
		rpt.elementByteLocations = pickle.load( open(byteLocDictionaryFName, 'r') )
		#rpt.byteLocDict = conduitByteLocationDict

	print("Started Drawing at " + strftime("%b-%d-%Y %H:%M:%S"))
	log = "Started Drawing at " + strftime("%b-%d-%Y %H:%M:%S") + "\n\nErrors:\n\n"
	drawCount = 0
	conduitErrorCount = 0

	font = ImageFont.truetype(su.fontFile, 30)
	basemapFeatureDicts = sg.createFeaturesDict(options=ops['basemap'],  bbox=bbox, shiftRatio=shiftRatio, width=width) #will be populated after first frame is produced
	while currentT <= endDtime:

		img = Image.new('RGB', imgSize, ops['bg'])
		draw = ImageDraw.Draw(img)
		currentTstr = currentT.strftime("%b-%d-%Y %H:%M:%S").upper()
		#print 'time =', currentTstr

		#DRAW THE BASEMAP
		if ops['basemap']:
			sg.draw_basemap(draw, img=img, options=ops['basemap'], width=width, bbox=bbox, featureDicts=basemapFeatureDicts, xplier = xplier)

		#DRAW THE CONDUITS
		if ops['conduitSymb']:
			for id, conduit in conduitDicts.items():
				#coordPair = coordPairDict['coordinates']
				if conduit.coordinates: #this prevents draws if no flow is supplied (RDII and such)

					su.drawConduit(conduit, coordPairDict, draw, options=ops['conduitSymb'],  rpt=rpt, dTime = currentTstr,
									xplier = xplier)

					drawCount += 1

				if drawCount > 0 and drawCount % 2000 == 0: print(str(drawCount) + " pipes drawn - simulation time = " + currentTstr)

		#DRAW THE NODES
		if ops['nodeSymb']:
			for id, node in nodeDicts.items():
				if node.coordinates: #this prevents draws if no flow is supplied (RDII and such)
					su.drawNode(node, nodeDict, draw, rpt=rpt, dTime=currentTstr, options=ops['nodeSymb'], xplier=xplier)
					drawCount += 1


		#DRAW THE ANNOTATION
		dtime = currentT.strftime("%b%d%Y_%H%M").upper()
		#su.drawAnnotation (draw, inp, rpt, imgWidth=width, title=None, currentTstr = currentTstr, fill=su.black)
		su.annotateMap (draw, model, options=ops, currentTstr = currentTstr)
		currentT += delta
		del draw


		#shrink for antialiasing niceness (though this blows up the file about 5x)
		tempImgDir = os.path.join(imgDir, "temp_frames")
		sg.saveImage(img, model, dtime, imgDir=tempImgDir, open=False, verbose=False)

	#WRITE THE GIF
	frames = []
	for image in glob.glob1(tempImgDir, "*.png"):
		imgPath = os.path.join(tempImgDir, image)
		frames.append(Image.open(imgPath))

	print("building gif with " + str(len(glob.glob1(tempImgDir, "*.png"))) + " frames...")
	if not imgName: imgName = inp.name
	gifFile = os.path.join(imgDir, imgName) + ".gif"
	frameDuration = 1.0 / float(ops['fps'])
	writeGif(gifFile, frames, duration=frameDuration)

	shutil.rmtree(tempImgDir) #delete temporary frames directory after succesful GIF

	log += "Completed drawing at " + strftime("%Y%m%d %H:%M:%S")
	with open(os.path.join(imgDir, "log.txt"), 'w') as logFile:
		logFile.write(log)

	print("Draw Count =" + str(drawCount))
	print("Video saved to:\n\t" + gifFile)

	os.startfile(gifFile)#this doesn't seem to work
