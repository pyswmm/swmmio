#parcels class object
import swmm_utils as su
import os
import pickle

class Parcel(object):
	
	#object representing a swmm node object
	
	__slots__ = ('id', 'flood_duration', 'avg_flood_duration', 
				'nodes', 'sheds', 'delta_type', 'is_delta')
	
	def __init__(self, id):

		#assign the header list
		self.id = id
		self.flood_duration = 0
		self.avg_flood_duration = 0
		self.nodes = []
		self.sheds = []
		self.is_delta = None
		self.delta_type = None #whether this object's data represents a change between two parent models
		
		
def parcel_flood_duration(model, parcel_features, threshold=0.083,  bbox=None, 
							gdb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb', 
							export_table=False,anno_results={}):
	
	#return a dictionary of each parcel ID with averagre flood duration
	
	#check if a parcel to node association dicitonary exists, load if possible
	parcel_to_nodes_filename = os.path.join(model.inp.dir, 'parcel_nodes_dict.txt')
	if not os.path.isfile(parcel_to_nodes_filename):
		
		#this is a heavy operation, allow a few minutes
		print "generating parcel/node association dictionary..."
		parcel_to_nodes_dict = parcel_to_nodes_dictionary(parcel_features, gdb=gdb, bbox=bbox) 
		
		#save for later use
		with open(parcel_to_nodes_filename, 'w') as dictSaveFile:
			pickle.dump(parcel_to_nodes_dict, dictSaveFile)
	else:
		print "loading parcel/node association dictionary..."
		parcel_to_nodes_dict = pickle.load( open(parcel_to_nodes_filename, 'r') ) 
		print "WARNING: make sure this loaded parcel dict contains all parcels!"
	
	#grab the list of flooded nodes, and create the dictionary of parcels linked to node IDs
	flooded_nodes = su.subsetElements(model, min=threshold, bbox=bbox, pair_only=True)
	
	#parcels_dict = parcel_to_nodes_dictionary(parcel_features, where = None, gdb=gdb, bbox=bbox) #this is heavy
	
	#tally how many were flooded above set durations
	#{minutes : number of parcels with flooding greater than}
	duration_partition = {
				5:0, 10:0, 15:0,
				30:0, 45:0, 60:0,
				75:0, 90:0, 105:0,
				120:0
				}
	#calculate average flood duration for each parcel
	parcels_flooded_count = 0
	
	parcels = {}
	for id, parcel_data in parcel_to_nodes_dict.iteritems():
	
		associated_nodes = parcel_data['nodes'] #associated nodes
		
		
		
		if len(associated_nodes) > 0:
			
			total_parcel_flood_dur = 0.0
			flood_duration = 0.0
			for node in associated_nodes:
				
				#look up the flood duration
				node_duration = flooded_nodes.get(node, 0)
				total_parcel_flood_dur += node_duration #for avereage calculation
				
				#parcel flooding duration assumed to be the max of all adjacent node durations
				flood_duration = max(flood_duration, node_duration)  
			
			avg_flood_duration = total_parcel_flood_dur/len(associated_nodes)
			parcel_data.update({'avg_flood_duration':avg_flood_duration, 'flood_duration':flood_duration})
			
			if flood_duration >= threshold: 
				#we've found a parcel that is considered flooded 
				parcels_flooded_count += 1
				
			for duration, count in duration_partition.iteritems():
				if flood_duration >= float(duration)/60.0:
					count += 1
					duration_partition.update({duration:count})
	
	parcels_count = len(parcel_to_nodes_dict)
	parcels_flooded_fraction = float(parcels_flooded_count)/float(parcels_count)
	
	results = {
				'parcels_flooded_count':parcels_flooded_count, 
				'parcels_count':parcels_count,
				'parcels_flooded_fraction':parcels_flooded_fraction,
				'duration_partition':duration_partition
				}
	
	results_string = "{} ({}%) of {} total".format(results['parcels_flooded_count'], round(results['parcels_flooded_fraction']*100),results['parcels_count'])
	
	print results_string
	
	#partition (detailed) results string
	partitioned_results = "\n"
	for d in sorted(duration_partition):
		perc_of_tot = int(round( float(duration_partition[d]) / float(results['parcels_count']) * 100 ))
		partitioned_results += '>{}mins : {} ({}%)\n'.format(d, duration_partition[d], perc_of_tot)
		
	#track results for annotation
	anno_results.update({'Total Parcels':results['parcels_count'], '\nParcels Flooded':partitioned_results})
	
	#add in the actual list of parcels for drawing
	results.update({'parcels':parcel_to_nodes_dict})
	
	return results
	 
def parcel_to_nodes_dictionary(feature, cols = ["PARCELID", "OUTLET", "SUBCATCH", "SHAPE@"], bbox=None, gdb=r'C:\Data\ArcGIS\GDBs\LocalData.gdb'):
	
	#create dictionary with keys for each parcel, and sub array containing associated nodes
	features = os.path.join(gdb, feature)
	import arcpy
	parcels = {}
	for row in arcpy.da.SearchCursor(features, cols):
		
		#first check if parcel is in bbox
		jsonkey = 'rings' #for arc polygons
		geometrySections = json.loads(row[3].JSON)[jsonkey]
		parcel_in_bbox=True #assume yes first
		for i, section in enumerate(geometrySections):
			#check if part of geometry is within the bbox, skip if not
			if bbox and len ( [x for x in section if pointIsInBox(bbox, x)] ) == 0:
				parcel_in_bbox=False #continue #skip this section if none of it is within the bounding box
			
		if not parcel_in_bbox:
			continue #skip if not in bbox
		
		PARCELID = str(row[0])
		if PARCELID in parcels:
			#append to existing array
			parcels[PARCELID]['nodes'].append(row[1])
			parcels[PARCELID]['sheds'].append(row[2])
		else:
			#new parcel id found
			
			#parcels.update({ PARCELID:{'nodes':[row[1]], 'sheds':[row[2]] }} )
			parcels.update({ PARCELID:{'nodes':[row[1]], 'sheds':[row[2]] }} )
			
	return parcels
	