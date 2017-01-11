#!/usr/bin/env python
#coding:utf-8

import random
from time import gmtime, strftime
import re
import os
import numpy
import pandas as pd
import parcels
import pickle
from .utils import swmm_utils as su
import glob
import csv
from .utils import text as txt
from .utils.dataframes import create_dataframeINP, create_dataframeRPT

class Model(object):

	#Class representing a complete SWMM model incorporating its INP and RPT
	#files and data

	def __init__(self, in_file_path):

		#can init with a directory containing files, or the specific inp file
		"""
		initialize a swmmio.Model object by pointing it to a directory containing
		a single INP (and optionally an RPT file with matching filename) or by
		pointing it directly to an .inp file.
		"""

		inp_path = None
		if os.path.isdir(in_file_path):
			#a directory was passed in
			#print 'is dir = {}'.format(in_file_path)
			inps_in_dir = glob.glob1(in_file_path, "*.inp")
			if len(inps_in_dir) == 1:
				#there is only one INP in this directory -> good.
				inp_path = os.path.join(in_file_path, inps_in_dir[0])
				#print 'only 1 inp found = {}'.format(inp_path)

		elif os.path.splitext(in_file_path)[1] == '.inp':
			#an inp was passed in
			inp_path = in_file_path
			#print 'is inp path = {}'.format(in_file_path)

		if inp_path:
			wd = os.path.dirname(inp_path) #working dir
			name = os.path.splitext(os.path.basename(inp_path))[0] #basename
			self.name = name
			self.inp = inp(inp_path) #inp object
			self.rpt = None #until we can confirm it initializes properly
			#slots to hold processed data
			self.organized_node_data = None
			self.organized_conduit_data = None
			self.bbox = None #to remember how the model data was clipped

			#try to initialize a companion RPT object
			rpt_path = os.path.join(wd, name + '.rpt')
			if os.path.exists(rpt_path):
				try:
					self.rpt = rpt(rpt_path)
				except:
					print '{}.rpt failed to initialize'.format(name)

			self._nodes_df = None
			self._conduits_df = None

	def conduits(self, bbox=None, subset=None):

		"""
		collect all useful and available data related model conduits and
		organize in one dataframe.
		"""

		#check if this has been done already and return that data accordingly
		if self._conduits_df is not None  and bbox==self.bbox:
			return self._conduits_df

		#parse out the main objects of this model
		inp = self.inp
		rpt = self.rpt

		#create dataframes of relevant sections from the INP
		conduits_df = create_dataframeINP(inp.path, "[CONDUITS]", comment_cols=False)
		xsections_df = create_dataframeINP(inp.path, "[XSECTIONS]", comment_cols=False)
		conduits_df = conduits_df.join(xsections_df)
		coords_df = create_dataframeINP(inp.path, "[COORDINATES]") #unuesed

		#concatenate the node DFs and keep only relevant cols
		if self._nodes_df is None:
			storages_df = create_dataframeINP(inp.path, "[STORAGE]")
			junctions_df = create_dataframeINP(inp.path, "[JUNCTIONS]")
			outfalls_df = create_dataframeINP(inp.path, "[OUTFALLS]")
			all_nodes = pd.concat([junctions_df, outfalls_df, storages_df])
			cols =['InvertElev', 'MaxDepth', 'SurchargeDepth', 'PondedArea']
			all_nodes = all_nodes[cols]
		else:
			print 'loading nodes'
			all_nodes_df = self._nodes_df

		if rpt:
			#create a dictionary holding data from an rpt file, if provided
			link_flow_df = create_dataframeRPT(rpt.path, "Link Flow Summary")
			conduits_df = conduits_df.join(link_flow_df)



		self._conduits_df =conduits_df

		return conduits_df

	def organizeConduitData (self, bbox=None, subset=None, extraData=None):

		#creates a dictionary of dictionaries containing relevant data
		#for conduits within a SWMM model. Upstream and downstream node data is attributed to the

		#check if this has been done already and return that data accordingly
		if self.organized_conduit_data and bbox==self.bbox:
			return self.organized_conduit_data

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

		reachLength = 0.00 #used for tranform
		maxEl = 0.00 #used for tranform
		minEl = 999999 #used for transform
		#errCount = 0

		for conduit_id, conduit_data in conduitsDict.iteritems():

			#try:
			upstreamNodeID = conduit_data[0]
			downstreamNodeID = conduit_data[1]
			inletoffset = float(conduit_data[4])
			outletoffset = float(conduit_data[5])
			length = float(conduit_data[2])
			upstreamXY = coordsDict[upstreamNodeID]
			upstreamXY = [float(i) for i in upstreamXY] #convert to floats
			downstreamXY = coordsDict[downstreamNodeID]
			downstreamXY = [float(i) for i in downstreamXY] #convert to floats
			geom1 = float(xsectionsDict[conduit_id][1]) #conduit diameter / height
			geom2 = xsectionsDict[conduit_id][2] #conduit width (sometimes a curve ref)

			if bbox and (not su.pointIsInBox(bbox, upstreamXY) and not su.pointIsInBox(bbox, downstreamXY)):
				#skip conduits who are not within a given boudning box. This includes conduits who are partially in the box.
				continue

			#downstream pipe id: the pipe whose upstream id equals downstreamNodeID
			conduit = Link(conduit_id, [upstreamXY, downstreamXY], geom1, geom2, inletoffset, outletoffset)
			conduit.length = length
			conduit.upNodeID = upstreamNodeID
			conduit.downNodeID = downstreamNodeID

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

		output = {'conduit_objects': conduit_objects}

		#remember this stuff for later
		self.organized_conduit_data = output
		self.bbox = bbox

		return output

	def nodes(self, bbox=None, subset=None):

		"""
		collect all useful and available data related model nodes and organize
		in one dataframe.
		"""

		#check if this has been done already and return that data accordingly
		if self._nodes_df is not None and bbox==self.bbox:
			return self._nodes_df

		#parse out the main objects of this model
		inp = self.inp
		rpt = self.rpt

		#create dataframes of relevant sections from the INP
		juncs_df = create_dataframeINP(inp.path, "[JUNCTIONS]")
		outfalls_df = create_dataframeINP(inp.path, "[OUTFALLS]")
		storage_df = create_dataframeINP(inp.path, "[STORAGE]")
		coords_df = create_dataframeINP(inp.path, "[COORDINATES]")

		#concatenate the DFs and keep only relevant cols
		all_nodes = pd.concat([juncs_df, outfalls_df, storage_df])
		cols =['InvertElev', 'MaxDepth', 'SurchargeDepth', 'PondedArea']
		all_nodes = all_nodes[cols]

		if rpt:
			#add results data if a rpt file was found
			depth_summ = create_dataframeRPT(rpt.path, "Node Depth Summary")
			flood_summ = create_dataframeRPT(rpt.path, "Node Flooding Summary")

			#join the rpt data (index on depth df, suffixes for common cols)
			rpt_df = depth_summ.join(flood_summ,lsuffix='_depth',rsuffix='_flood')
			all_nodes = all_nodes.join(rpt_df) #join to the all_nodes df

		all_nodes = all_nodes.join(coords_df[['X', 'Y']])

		#lookup the subcatchment data directly draining to each node
		subcats_df = create_dataframeINP(inp.path, "[SUBCATCHMENTS]")[['Outlet', 'Area']]
		subcats_df['subcat_id'] = subcats_df.index
		subcats_df = subcats_df.set_index('Outlet')
		all_nodes = all_nodes.join(subcats_df)

		self._nodes_df = all_nodes

		return all_nodes


	def organizeNodeData(self, bbox=None, subset=None):

		#creates a dictionary of dictionaries containing relevant data
		#per node within a SWMM model.

		#check if this has been done already and return that data accordingly
		if self.organized_node_data and bbox==self.bbox:
			return self.organized_node_data

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

		if rpt:
			#create a dictionary holding data from an rpt file, if provided
			nodesDepthSummaryDict = rpt.createDictionary("Node Depth Summary")
			nodesFloodSummaryDict = rpt.createDictionary("Node Flooding Summary")


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
			try:
			    n.maxDepth = float(allNodesDict[node][1])
			except ValueError:
			    pass #not a float, probably a 'FIXED' tag at that index on a outfall node


			if rpt and (node in nodesDepthSummaryDict):
				#if the up and downstream nodes are also found in the node depth summary dictionary,
				#grab the relevant data and store a little dictionary
				NDA = nodesDepthSummaryDict[node] #upstream node depth array

				n.maxHGL = float(NDA[3])
				#n.maxDepth = float(NDA[2])
				maxEl = max(n.maxHGL, maxEl) #increase the max elevation observed with the HGL

			if rpt and (node in nodesFloodSummaryDict):
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

		#save for later use. save the bbox instance so we refresh this attributed
		#whenever the bbox is changed (so we don't leave elements out)
		self.organized_node_data = output
		self.bbox = bbox

		return output

	def node(self, node, conduit=None):

		#method for provide information about specific model elements
		#returns a node object given its ID
		if not self.organized_node_data:
			self.organized_node_data = self.organizeNodeData()

		n = self.organized_node_data['node_objects'][node]
		subcats_inp = self.inp.createDictionary("[SUBCATCHMENTS]")
		subcats_rpt = self.rpt.createDictionary('Subcatchment Runoff Summary')

		n.nodes_upstream = su.traceFromNode(self, node, mode='up')['nodes']
		n.subcats_direct = [k for k,v in subcats_inp.items() if v[1]==node]
		n.subcats_upstream = [k for k,v in subcats_inp.items() if v[1] in n.nodes_upstream]


		n.drainage_area_direct = sum([float(x) for x in [v[2] for k,v in subcats_inp.items() if k in n.subcats_direct]])
		n.drainage_area_upstream = sum([float(x) for x in [v[2] for k,v in subcats_inp.items() if k in n.subcats_upstream]])

		n.runoff_upstream_mg = sum([float(x) for x in [v[5] for k,v
								in subcats_rpt.items() if k in n.subcats_upstream]])
		n.runoff_upstream_cf = n.runoff_upstream_mg*1000000/7.48
		return n

	def list_objects(self,element_type='node', bbox=None, subset=None):
		"""
		return a dictionary of element obects of the type specified, with
		keys equal to the element ID.
		"""
		#organize the data -> dictionary of objects
		if element_type == 'node':
			data = self.organizeNodeData(bbox, subset=subset)
			dicts = data['node_objects']
		elif element_type == 'conduit':
			data = self.organizeConduitData(bbox, subset=subset)
			dicts = data['conduit_objects']
		elif element_type =='parcel':
			data = parcels.parcel_flood_duration(self, 'PWD_PARCELS_SHEDS', threshold=0)
			dicts =data['parcels']
		else:
			return "incorrect data type specified"

		return dicts

	def export_geojson(self, bbox=None, crs=None, filename=None):
		"""
		export model as a geojson object
		"""
		import geojson
		try:
			import pyproj
		except ImportError:
			raise ImportError('pyproj module needed. get this package here: ',
							'https://pypi.python.org/pypi/pyproj')

		from geojson import Point, LineString, Feature, GeometryCollection

		if crs is None:
			#default coordinate system (http://spatialreference.org/ref/epsg/2272/):
			#NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet
			crs =  {"type": "name","properties": {"name": "EPSG:2272"}}

		pa_plane = pyproj.Proj(init='epsg:2272', preserve_units=True)
		wgs = pyproj.Proj(proj='latlong', datum='WGS84', ellps='WGS84') #google maps, etc


		geometries = [] #array of features
		#collect the nodes
		for k,v in self.list_objects('node', bbox).items():
			props = {'flood_duration':v.flood_duration, 'id':v.id}
			lat,lng = pyproj.transform(pa_plane, wgs, *v.coordinates)
			geometry = Point((lat,lng), properties=props)
			geometries.append(geometry)

		#collect the links
		for k,v in self.list_objects('conduit', bbox).items():
			props = {'MaxQPercent':v.maxQpercent,
			        'id':v.id,
			        'lifecycle':v.lifecycle,
			        'geom1':v.geom1,
					'geom2':v.geom2,}

			latlngs = [pyproj.transform(pa_plane, wgs, *xy) for xy in v.coordinates]
			geometry = LineString(latlngs, properties=props)
			geometries.append(geometry)

		# points = []
		# for k, v in node_dicts.items():
		# 	xy = v.coordinates
		# 	points.append((xy[0], xy[1]))
		if filename is None:
			return GeometryCollection(geometries, crs=crs)
		else:
			with open(filename, 'wb') as f:
				f.write(geojson.dumps(GeometryCollection(geometries, crs=crs)))
				#f.write(geojson.dumps(FeatureCollection(nodefeatures, crs=crs)))


	def export_to_shapefile(self, element_type='node', filename=None, bbox=None, subset=None):
		"""
		export the model data into a shapefile. element_type dictates which type
		of data will be included.
		"""
		import shapefile
		import shutil

		#organize the data -> dictionary of objects
		dicts = self.list_objects(element_type, bbox, subset=subset)

		#grab first object in list to structure the dataframe
		ref_object = dicts[dicts.keys()[0]]
		fields = ref_object.__slots__
		data = [[getattr(v,j) for j in fields] for k,v in dicts.items()]

		#create a shp file writer object of geom type 'point'
		if element_type == 'node':
			w = shapefile.Writer(shapefile.POINT)
		elif element_type == 'conduit':
			w = shapefile.Writer(shapefile.POLYLINE)

		#use the helper mode to ensure the # of records equals the # of shapes
		#(shapefile are made up of shapes and records, and need both to be valid)
		w.autoBalance = 1

		#add the fields
		for fieldname in fields:
			w.field(fieldname, "C")

		#add the data
		for k, v in dicts.items():

			#add the coordinates
			xy = v.coordinates

			if element_type == 'node':
				w.point(xy[0], xy[1])
			elif element_type == 'conduit':
				w.line(parts = [xy])


			#add the record, by accessing each object attribute's data
			w.record(*[getattr(v,j) for j in fields])
			#print [getattr(v,j) for j in fields]
			#print '{}:  {} - {}'.format(v.id, xy[0], xy[1])

		w.save(filename)

		#save the projection data
		currentdir = os.path.dirname(__file__)
		prj_filepath = os.path.splitext(filename)[0] + '.prj'
		shutil.copy(os.path.join(currentdir, 'defs/default.prj'), prj_filepath)

	def export_to_csv(self,  element_type='node', filename=None, bbox=None, openfile=True):

		"""
		exports the organized SWMM data into a csv table
		"""

		#organize the data -> dictionary of objects
		dicts = self.list_objects(element_type, bbox)

		#grab first object in list to structure the dataframe
		ref_object = dicts[dicts.keys()[0]]
		data = [[getattr(v,j) for j in ref_object.__slots__] for k,v in dicts.items()]
		df = pd.DataFrame(data, columns = ref_object.__slots__)

		#save to file csv
		if not filename: filename = self.inp.name + "_" + element_type + 's_'
		csvfilepath = os.path.join(self.inp.dir, filename) + '.csv'
		df.to_csv(csvfilepath)

		if openfile:
			os.startfile(csvfilepath)

class SWMMIOFile(object):

	defaultSection = "Link Flow Summary"

	def __init__(self, file_path):

		#file name and path variables
		self.path = file_path
		self.name = os.path.splitext(os.path.basename(file_path))[0]
		self.dir = os.path.dirname(file_path)
		self.file_size = os.path.getsize(file_path)


	def findByteRangeOfSection(self, startStr):

		#returns the start and end "byte" location of substrings in a text file

		with open(self.path) as f:
			start = None
			end = None
			l = 0 #line bytes index
			for line in f:

				#if start and len(line) <= 3 and (l - start) > 100:
				if start and line.strip() == "" and (l - start) > 100:
					#LOGIC ^ if start exists (was found) and the current line length is 3 or
					#less (length of /n ) and we're more than 100 bytes from the start location
					#then we are at the first "blank" line after our start section (aka the end of the section)
					end = l
					break

				if (startStr in line) and (not start):
					start = l

				l += len(line) + len("\n") #increment length (bytes?) of current position

		return [start, end]

	def exportCSV(self, sectionTitle = defaultSection):
		#create CSV of section of choice in inp file

		outFilePath = self.dir + "\\" + self.name + "_" + sectionTitle.replace(" ", "") + ".csv"
		outFile = open(outFilePath, 'w') #create outfile
		preppedTempFilePath = txt.extract_section_from_file(self.path, sectionTitle)
		if not preppedTempFilePath:
			return None #if nothing was found, do nothing

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

		"""
		Help info about this method.
		"""

		#preppedTempFilePath = self.readSectionAndCleanHeaders(sectionTitle) #pull relevant section and clean headers
		preppedTempFilePath = txt.extract_section_from_file(self.path, sectionTitle)
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
		with open(self.path) as f:

			f.seek(startByte) #jump to section at byte
			#return f.read(printLength)

			if lookUpStr:
				for line in f:
					#l += len(line) + len("\n")
					if lookUpStr in line:
						f.seek(l)
						break
					l += len(line) + len("\n")

			print f.read(printLength)

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
			f.seek(self.file_size - 500) #jump to 500 bytes before the end of file
			for line in f:
				if "Analysis begun on" in line:
					date = line.split("Analysis begun on:  ")[1].replace("\n", "")

		self.dateOfAnalysis = date

		#assign the header list
		#self.headerList = swmm_headers.rptHeaderList
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
		with open(self.path) as f:

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

		with open(self.path) as f:

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
		#self.headerList = swmm_headers.inpHeaderList

	def replace_section(self, newdata, sectionheader='[FILES]'):

		"""
		replace a given section of the INP file with the contents of a passed
		dataframe object. Function creates a temporary copy of the original,
		rebuilds the entire inp, section by section, saves the temp file, then
		renames the temp file to the original file name.
		"""
		pass





class Node(object):

	#object representing a swmm node object

	__slots__ = ('id', 'invert', 'coordinates', 'nodes_upstream', 'subcats_direct', 'subcats_upstream',
				'drainage_area_direct', 'drainage_area_upstream',
				'runoff_upstream_cf', 'runoff_upstream_mg',
				'flood_duration', 'maxDepth',
				'maxHGL', 'draw_coordinates', 'lifecycle', 'delta_type', 'is_delta')

	def __init__(self, id, invert=None, coordinates=[]):

		#assign the header list
		self.id = id
		self.invert = invert
		self.coordinates = coordinates
		self.nodes_upstream = None
		self.subcats_direct = [] #subcatchment draining into this node, if any
		self.subcats_upstream = [] #all subcats upstream
		self.drainage_area_direct = None #only populated when needed
		self.drainage_area_upstream = None #only populated when needed
		self.runoff_upstream_cf = None #only populated when needed
		self.runoff_upstream_mg = None #only populated when needed
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
				'maxHGLDownstream', 'maxHGLUpstream', 'geom1', 'geom2', 'length','inletoffset', 'outletoffset',
				'draw_coordinates', 'lifecycle', 'delta_type', 'is_delta')


	def __init__(self, id, coordinates=[], geom1=None, geom2=None, inletoffset=0, outletoffset=0):

		#assign the header list
		self.id = id
		self.coordinates = coordinates
		self.maxflow = 0
		self.maxQpercent = 0
		self.maxHGLDownstream = 0
		self.maxHGLUpstream = 0
		self.inletoffset = inletoffset
		self.outletoffset = outletoffset
		self.upNodeID = None
		self.downNodeID = None
		self.geom1 = geom1 #faster to use zero as default?
		self.geom2 = geom2 #faster to use zero as default?
		self.length = None
		self.draw_coordinates = None
		self.lifecycle = 'existing'
		self.is_delta = None
		self.delta_type = None #whether this object's data represents a change between two parent models






#end
