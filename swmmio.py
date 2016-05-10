#sys.path.append(r"P:\Tools\swmmio")
#sys.path.append(r"P:\Tools")

import random
from time import gmtime, strftime
import re
import os
import numpy
from PIL import Image, ImageDraw, ImageFont
from images2gif import writeGif
import pickle
import swmm_utils as su
import swmm_headers
import glob
import csv

class Model(object):

	#Class representing a complete SWMM model incorporating its INP and RPT
	#files and data

	def __init__(self, file, modelName=None):

		#can init with a directory containing files, or the specific inp file

		fileParts = os.path.splitext(file)
		#check if input file is dir or inp
		if ".inp" in fileParts[1]:
			#input is a full path to an inp
			name = os.path.splitext(os.path.basename(file))[0]
			inpFile = file
			rptFile = fileParts[0] + ".rpt"
		elif ".rpt" in fileParts[1]:
			#input is a full path to an inp
			name = os.path.splitext(os.path.basename(file))[0]
			inpFile = fileParts[0]+ ".inp"
			rptFile = file

		else:
			#input is a directory
			#check that there is only one inp/rpt pair, otherwise break
			inpsInDir = glob.glob1(file, "*.inp")
			if len(inpsInDir) == 1:
				name = os.path.splitext(inpsInDir[0])[0]
				inpFile = os.path.join(file, inpsInDir[0])
				rptFile = os.path.join(file, name) + ".rpt"

		#file name and path variables
		self.inp = inp(inpFile)
		self.rpt = rpt(rptFile)

	def organizeConduitData (self, bbox=None, subset=None, extraData=None, findOrder=False):

		#creates a dictionary of dictionaries containing relevant data
		#for conduits within a SWMM model. Upstream and downstream node data is attributed to the

		#parse out the main objects of this model
		inp = self.inp
		rpt = self.rpt

		#creat dictionary of conduits and join dictionaries of all nodes
		conduitsDict = inp.createDictionary("[CONDUITS]")
		xsectionsDict = inp.createDictionary("[XSECTIONS]")
		if subset:
			conduitsDict = { key:value for key,value in conduitsDict.items() if key in subset }
			xsectionsDict = { key:value for key,value in xsectionsDict.items() if key in subset }
		storagesDict = inp.createDictionary("[STORAGE]")
		junctionsDict = inp.createDictionary("[JUNCTIONS]")
		outfallsDict = inp.createDictionary("[OUTFALLS]")
		coordsDict = inp.createDictionary("[COORDINATES]")

		#merge all the "node" type dictionaries (those that can be junctions between SWMM links)
		allNodesDict = su.merge_dicts(storagesDict, junctionsDict, outfallsDict)

		nodesDepthSummaryDict = {} # from rpt if one is supplied
		conduit_objects = {}
		#downstreamConduits = []
		if rpt:
			#create a dictionary holding data from an rpt file, if provided
			nodesDepthSummaryDict = rpt.createDictionary("Node Depth Summary")
			allLinksSummaryDict = rpt.createDictionary("Link Flow Summary")
			nodesFloodSummaryDict = rpt.createDictionary("Node Flooding Summary")
			print "created node and link summary dicts from " + rpt.fName

		reachLength = 0.00 #used for tranform
		maxEl = 0.00 #used for tranform
		minEl = 999999 #used for transform
		#errCount = 0
	
		for conduit_id, conduit_data in conduitsDict.iteritems():
			
			#try:
			upstreamNodeID = conduit_data[0]
			downstreamNodeID = conduit_data[1]
			length = float(conduit_data[2])
			upstreamXY = coordsDict[upstreamNodeID]
			upstreamXY = [float(i) for i in upstreamXY] #convert to floats
			downstreamXY = coordsDict[downstreamNodeID]
			downstreamXY = [float(i) for i in downstreamXY] #convert to floats
			geom1 = float(xsectionsDict[conduit_id][1]) #conduit diameter / height

			if bbox and (not su.pointIsInBox(bbox, upstreamXY) and not su.pointIsInBox(bbox, downstreamXY)):
				#skip conduits who are not within a given boudning box. This includes conduits who are partially in the box.
				continue

			#downstream pipe id: the pipe whose upstream id equals downstreamNodeID
			conduit = Link(conduit_id, [upstreamXY, downstreamXY], geom1)

			
			if rpt and (upstreamNodeID in nodesDepthSummaryDict) and (downstreamNodeID in nodesDepthSummaryDict):
				# #if the up and downstream nodes are also found in the node depth summary dictionary,
				# #grab the relevant data and store a little dictionary
				upNDA = nodesDepthSummaryDict[upstreamNodeID] #upstream node depth array
				dnNDA = nodesDepthSummaryDict[downstreamNodeID] #downstream node depth array
				upHGL = float(upNDA[3])
				dnHGL = float(dnNDA[3])
				conduit.maxHGLDownstream = dnHGL
				conduit.maxHGLUpstream = upHGL
			

			if rpt and conduit_id in allLinksSummaryDict:
				#if the conduit is found in the link summary dictionary,
				#grab the link flow smmary data and store a little dictionary
				lsa = allLinksSummaryDict[conduit_id] #link summary array
				#lsa = [float(i) for i in lsa] #convert to floats
				if lsa[0] == "CONDUIT":
					
					conduit.maxflow = float(lsa[1])
					conduit.maxQpercent = float(lsa[5])
					

			#append data to the overall dictionary
			conduit_objects.update({conduit_id:conduit})

			#except Exception (e):
			#	print str(e)

		output = {
			'conduit_objects': conduit_objects
			#'boundingBox':modelSize,
			#'startingConduit':startingConduit
			#'downstreamConduits':downstreamConduits
			# 'maxEl':maxEl,
			# 'minEl':minEl,
			# 'reachLength':reachLength
			}

		return output

	def organizeNodeData (self, bbox=None, subset=None):

		#creates a dictionary of dictionaries containing relevant data
		#per node within a SWMM model.

		#parse out the main objects of this model
		inp = self.inp
		rpt = self.rpt

		#creat dictionary of all nodes from the INP and join dictionaries
		storagesDict = inp.createDictionary("[STORAGE]")
		junctionsDict = inp.createDictionary("[JUNCTIONS]")
		outfallsDict = inp.createDictionary("[OUTFALLS]")
		coordsDict = inp.createDictionary("[COORDINATES]")
		allNodesDict = su.merge_dicts(storagesDict, junctionsDict, outfallsDict)

		if subset:
			allNodesDict = { key:value for key,value in allNodesDict.items() if key in subset }

		#create a dictionary holding data from an rpt file
		nodesDepthSummaryDict = rpt.createDictionary("Node Depth Summary")
		nodesFloodSummaryDict = rpt.createDictionary("Node Flooding Summary")
		print "created node summary dicts from " + rpt.fName

		maxEl = 0.00 #used for tranform
		minEl = 999999 #used for transform
		#errCount = 0
		node_objects = {}
		for node in allNodesDict:

			if not allNodesDict[node] or not node in coordsDict:
				continue

			#if the conduit's upstream & downstream nodes are
			# found in the allNodesDict look up it's data
			#try:
			invert = 	float(allNodesDict[node][0])
			xy = [float(i) for i in coordsDict[node]]#convert to floats
			
			if bbox and (not su.pointIsInBox(bbox, xy)):
				#skip nodes who are not within a given boudning box.
				continue
			
			n = Node(node, invert, xy)
			
			if (node in nodesDepthSummaryDict):
				#if the up and downstream nodes are also found in the node depth summary dictionary,
				#grab the relevant data and store a little dictionary
				NDA = nodesDepthSummaryDict[node] #upstream node depth array
				
				n.maxHGL = float(NDA[3])
				n.maxDepth = float(NDA[2])
				maxEl = max(n.maxHGL, maxEl) #increase the max elevation observed with the HGL
				
			if (node in nodesFloodSummaryDict):
				#if the up and downstream nodes are also found in the node flooding summary dictionary,
				#grab the relevant data and store a little dictionary
				NFA = nodesFloodSummaryDict[node] #upstream node flooding array
				n.flood_duration = float(NFA[0])
				#nodeDict.update({'floodDuration':floodDuration})
				
			#append data to the overall dictionary
			node_objects.update({node:n})

			maxEl = max(n.maxDepth, n.maxHGL, maxEl) #inverts plus the geom1 (pipe dimension)
			minEl = min(invert, minEl)

			#except:
				#errors occured when nodes aren't found in COORDINATES table
			#	print 'problem with ', node

		output = {
			'node_objects': node_objects,
			'maxEl':maxEl,
			'minEl':minEl,
			}

		return output

	def exportData(self, fname=None, type='node', bbox=None, openfile=True):
		
		#this is broken since using objects for nodes/links
		#exports the organized SWMM data into a csv table

		#organize the data
		if type == 'node':
			data = self.organizeNodeData(bbox)
			dicts = data['nodeDictionaries']
		elif type == 'conduit':
			data = self.organizeConduitData(bbox)
			dicts = data['conduitDictionaries']
		elif type =='parcels':
			data = su.parcel_flood_duration(self, 'PWD_PARCELS_SHEDS', threshold=0)
			dicts =data['parcels']
		else:
			return "incorrect data type specified"

		#make first header column hold the node ID
		#have to hack the dictionary a bit:
		keys = dicts[dicts.keys()[0]].keys() #accesses the keys of the first node ID
		keys.reverse()
		keys.append('id')
		keys.reverse() #reverse to append the id key to the front of the keys list

		if not fname: fname = self.inp.name + "_" + type + 's_' + su.randAlphaNum(5)
		csvfilepath = os.path.join(self.inp.dir, fname) + '.csv'
		with open(csvfilepath, 'wb') as file:
			fieldnames = keys
			writer = csv.DictWriter(file, fieldnames=fieldnames)
			writer.writeheader()

			for id, data in dicts.iteritems():

				therowdict = {'id':id}
				therowdict.update(data)

				writer.writerow(therowdict)

		if openfile:
			os.startfile(csvfilepath)

class SWMMIOFile(object):

	defaultSection = "Link Flow Summary"

	def __init__(self, filePath):

		#file name and path variables
		self.filePath = filePath
		self.fName = os.path.basename(filePath)
		self.name = os.path.splitext(self.fName)[0]
		self.dir = os.path.dirname(filePath)
		self.fileSize = os.path.getsize(filePath)


	def findByteRangeOfSection(self, startStr):

		#returns the start and end "byte" location of substrings in a text file

		with open(self.filePath) as f:
			start = None
			end = None
			l = 0 #line bytes index
			for line in f:

				if start and len(line) <= 3 and (l - start) > 100:
					#LOGIC ^ if start exists (was found) and the current line length is 3 or
					#less (length of /n ) and we're more than 100 bytes from the start location
					#then we are at the first "blank" line after our start section (aka the end of the section)
					end = l
					break

				if (startStr in line) and (not start):
					start = l

				l += len(line) + len("\n") #increment length (bytes?) of current position

		return [start, end]

	def readSectionAndCleanHeaders(self, sectionTitle = defaultSection, outFile = None):

		#parse through a section of the file based on the location of bytes and cleaned up headers

		byteRange = self.findByteRangeOfSection(sectionTitle)
		if not byteRange[0]: return None #if nothing is found, return nothing

		numbytes = byteRange[1] - byteRange[0]
		outFilePath = self.dir + "\\" + self.name + "_section.txt"
		outFile = open(outFilePath, 'w')
		headerList = self.headerList #inpSectionHeaders.headerList #replace sloppy rpt file headers with these one-row headers (CSV ready)
		cleaned = None

		with open(self.filePath) as rptSection:

			rptSection.seek(byteRange[0]) #jump to the start location
			raw = rptSection.read(numbytes)
			byteRemovedFromHeaderCleaning = 0
			#clean up the headers
			for hPair in headerList:
				#maybe slow because we're scanning the file multiple times for each header pair
				raw = raw.replace(hPair[0], hPair[1])
				byteRemovedFromHeaderCleaning += len(hPair[0][0]) - len(hPair[0][1])

			cleaned = raw #.read(numbytes - byteRemovedFromHeaderCleaning) #now its cleaned
			outFile.write(cleaned)

		outFile.close()

		return outFilePath

	def exportCSV(self, sectionTitle = defaultSection):
		#create CSV of section of choice in inp file

		outFilePath = self.dir + "\\" + self.name + "_" + sectionTitle.replace(" ", "") + ".csv"
		outFile = open(outFilePath, 'w') #create outfile
		preppedTempFilePath = self.readSectionAndCleanHeaders(sectionTitle) #pull relevant section and clean headers

		with open(preppedTempFilePath) as rptFile:
			for line in rptFile:

				#if the line is blankish, break (chop off any junk at the end)
				if len(line) <=3: break
				if ";" in line: continue #don't include any comments
				#print line if there is stuff on it, CSV style
				line = ','.join(re.findall('\"[^\"]*\"|\S+', line))
				outFile.write("%s\n" % line)

		outFile.close()
		os.remove(preppedTempFilePath)

		return outFilePath

	def createDictionary (self, sectionTitle = defaultSection):
		preppedTempFilePath = self.readSectionAndCleanHeaders(sectionTitle) #pull relevant section and clean headers

		if not preppedTempFilePath:
			return None #if nothing was found, do nothing

		passedHeaders = False

		with open(preppedTempFilePath) as file:
			the_dict = {}
			for line in file:

				if len(line) <=3 and not ";" in line: break
				if not passedHeaders:
					passedHeaders = True
					continue
				
				#check if line is commented out (having a semicolon before anything else) and skip accordingly
				if ";" == line.replace(" ", "")[0]:
					continue #omit this entire line
				
				line = line.split(";")[0] #don't look at anything to right of a semicolon (aka a comment)
				
				line = ' '.join(re.findall('\"[^\"]*\"|\S+', line))
				rowdata = line.replace("\n", "").split(" ")
				the_dict[str(rowdata[0])] = rowdata[1:] #create dictionary row with key and array of remaing stuff on line as the value

		os.remove(preppedTempFilePath)

		return the_dict

	def printSectionOfFile(self, lookUpStr=None, startByte=0, printLength = 500):

		l = startByte #line byte location
		with open(self.filePath) as f:

			f.seek(startByte) #jump to section at byte
			#return f.read(printLength)

			if lookUpStr:
				for line in f:
					l += len(line) + len("\n")
					if lookUpStr in line:
						f.seek(l)

			return f.read(printLength)

	
	
class rpt(SWMMIOFile):

	#creates an accessible SWMM .rpt object, inherits from SWMMIO object
	defaultImageDir = r"P:\Tools\Pipe Capacity Graphics\Scripts\image"
	def __init__(self, filePath):

		SWMMIOFile.__init__(self, filePath) #run the superclass init

		with open (filePath) as f:
			for line in f:
				if "Starting Date" in line:
					simulationStart = line.split(".. ")[1].replace("\n", "")
				if "Ending Date" in line:
					simulationEnd = line.split(".. ")[1].replace("\n", "")
				if "Report Time Step ........." in line:
					timeStepMin = int(line.split(":")[1].replace("\n", ""))
					break

		self.simulationStart = simulationStart
		self.simulationEnd = simulationEnd
		self.timeStepMin = timeStepMin

		#grab the date of analysis
		with open (filePath) as f:
			f.seek(self.fileSize - 500) #jump to 500 bytes before the end of file
			for line in f:
				if "Analysis begun on" in line:
					date = line.split("Analysis begun on:  ")[1].replace("\n", "")

		self.dateOfAnalysis = date

		#assign the header list
		self.headerList = swmm_headers.rptHeaderList
		self.byteLocDict = None #populated if necessary elsewhere (LEGACY, can prob remove)
		self.elementByteLocations = {"Link Results":{}, "Node Results":{}} #populated if necessary elsewhere

	def createByteLocDict (self, sectionTitle = "Link Results"):

		#method creates a dictionary with Key = to SWMM element ID and
		#Value as the starting byte location of its time series in the rpt file
		#for rapidly accessing large rpt files

		#create set of other headers that are not the desired one, use to find end of section
		possibleNextSections = set(['Link Results', 'Node Results', 'Subcatchment Results']) - set([sectionTitle])

		print possibleNextSections

		startByte = self.findByteRangeOfSection(sectionTitle)[0] #+ len('\n  ************') #move past the first asterisks

		id_byteDict = {}
		with open(self.filePath) as f:

			f.seek(startByte) #jump to general area of file if we know it
			l = startByte
			for line in f:

				#if "<<<" in line and ">>>" in line:
				if "<<<" and ">>>" in line:	#cr
					#found the begining of a link's section
					lineCleaned = ' '.join(re.findall('\"[^\"]*\"|\S+', line))
					rowdata = lineCleaned.replace("\n", "").split(" ")

					#add to the dict
					id_byteDict.update({rowdata[2]:l})

				if any(header in line for header in possibleNextSections):
					#checks if line includes any of the other headers,
					#if so, we found next section, stop building dict
					break

				l += len(line) + len("\n") #increment length (bytes) of current position

		self.byteLocDict = id_byteDict
		self.elementByteLocations.update({sectionTitle:id_byteDict})
		return id_byteDict

	def returnDataAtDTime(self, id, dtime, sectionTitle="Link Results", startByte=0):

		#this is a slow ass function, when the file is big - can we improve this?
		byteLocDict = self.elementByteLocations[sectionTitle]
		if byteLocDict:
			startByte = byteLocDict[id]

		elif startByte == 0:
			startByte = self.findByteRangeOfSection(sectionTitle)[0]
			print 'startByte ' + str(startByte)

		with open(self.filePath) as f:

			f.seek(startByte) #jump to general area of file if we know it
			subsectionFound = False

			for line in f:
				if id in line: subsectionFound = True

				if subsectionFound and dtime in line:
					line = ' '.join(re.findall('\"[^\"]*\"|\S+', line))
					rowdata = line.replace("\n", "").split(" ")
					return rowdata

class inp(SWMMIOFile):

	#creates an accessible SWMM .inp object
	#make sure INP has been saved in the GUI before using this

	def __init__(self, filePath):

		SWMMIOFile.__init__(self, filePath) #run the superclass init

		#assign the header list
		self.headerList = swmm_headers.inpHeaderList


class Node(object):
	
	#object representing a swmm node object
	
	__slots__ = ('id', 'invert', 'coordinates', 'flood_duration', 'maxDepth',
				'maxHGL', 'draw_coordinates', 'lifecycle', 'delta_type', 'is_delta')
	
	def __init__(self, id, invert=None, coordinates=[]):

		#assign the header list
		self.id = id
		self.invert = invert
		self.coordinates = coordinates
		self.flood_duration = 0
		self.maxDepth = 0
		self.maxHGL = 0
		self.draw_coordinates = None
		self.lifecycle = 'existing'
		self.is_delta = None
		self.delta_type = None #whether this object's data represents a change between two parent models
		
class Link(object):
	
	#object representing a swmm Link (conduit) object
	
	__slots__ = ('id', 'coordinates', 'maxflow', 'maxQpercent', 'upNodeID', 'downNodeID', 
				'maxHGLDownstream', 'maxHGLUpstream', 'geom1', 'length',
				'draw_coordinates', 'lifecycle', 'delta_type', 'is_delta')
	
	
	def __init__(self, id, coordinates=[], geom1=None):

		#assign the header list
		self.id = id
		self.coordinates = coordinates
		self.maxflow = 0
		self.maxQpercent = 0
		self.maxHGLDownstream = 0 
		self.maxHGLUpstream = 0 
		self.upNodeID = None
		self.downNodeID = None
		self.geom1 = geom1 #faster to use zero as default?
		self.length = None
		self.draw_coordinates = None
		self.lifecycle = 'existing'
		self.is_delta = None
		self.delta_type = None #whether this object's data represents a change between two parent models
		
		
		
		
		
		
#end
