#!/usr/bin/env python
#coding:utf-8

#this is fairly specific stuff and will only work given certain geospatial data
from .utils import swmm_utils as su
import os
import pickle
import json
from definitions import *

class Parcel(object):

	#object representing a swmm node object

	__slots__ = ('id', 'flood_duration', 'avg_flood_duration',
				'nodes', 'sheds', 'delta_type', 'is_delta')

	def __init__(self, id, nodes=[], sheds=[]):

		#assign the header list
		self.id = id
		self.flood_duration = 0
		self.avg_flood_duration = 0
		self.nodes = nodes
		self.sheds = sheds
		self.is_delta = False
		self.delta_type = 'flooding_unchanged' #whether this object's data represents a change between two parent models

def compareParcels(existing_elements, proposed_elements, parcel_features=PARCEL_FEATURES, bbox=None,
					floodthreshold=0.08333, delta_threshold=0.25, anno_results={}):

	#return a dict of node objects with the delta between models

	# existing_elements = parcel_flood_duration(model1, parcel_features=parcel_features,
	# 										bbox=bbox, anno_results=anno_results)['parcels']
	# proposed_elements = parcel_flood_duration(model2, parcel_features=parcel_features,
	# 										bbox=bbox, anno_results=anno_results)['parcels']


	#WARNING THIS CHANGES THE VALUES IN proposed_elements


	newflood = moreflood = floodEliminated = floodlowered = 0 #for documenting how things changed
	for id, proposed in proposed_elements.iteritems():

		existing = existing_elements.get(id, {})

		if id in existing_elements:

			flood_duration_delta = proposed.flood_duration - existing.flood_duration

			if existing.flood_duration >= floodthreshold and proposed.flood_duration >= floodthreshold:
				#parcel still floods, check how it changed:
				if flood_duration_delta > delta_threshold:
					#flooding duration increased (more than delta_threhold)
					proposed.delta_type = 'increased_flooding'
					moreflood += 1

				elif flood_duration_delta < -delta_threshold:
					#flooding duration decreased (more than delta_threhold)
					proposed.delta_type = 'decreased_flooding'
					floodlowered += 1

			elif existing.flood_duration < floodthreshold and proposed.flood_duration >= floodthreshold and abs(flood_duration_delta) >= delta_threshold:
				#flooding occurs where it perviously did not
				proposed.delta_type = 'new_flooding'
				newflood += 1

			elif existing.flood_duration >= floodthreshold and proposed.flood_duration < floodthreshold and abs(flood_duration_delta) >= delta_threshold:
				#parcel that previously flooded no longer does
				proposed.delta_type = 'eliminated_flooding'
				floodEliminated += 1


			proposed.is_delta = True
			proposed.flood_duration = flood_duration_delta
			proposed.avg_flood_duration -= existing.avg_flood_duration


	#update annotation results
	impact_dict = {
				1:{'title':'New flooding','val':newflood},
				2:{'title':'Increased flooding','val':moreflood},
				3:{'title':'Decreased flooding','val':floodlowered},
				4:{'title':'Eliminated flooding','val':floodEliminated},
				}
	impacts_string = "\n"
	for i in sorted(impact_dict):
		title = impact_dict[i]['title']
		val = impact_dict[i]['val']
		impacts_string += '{} on {} parcels\n'.format(title, val)

	anno_title =  '\nImpact Of Alternative (dt >= {}m)'.format(int(round(delta_threshold*60)))
	anno_results.update({anno_title:impacts_string})
	results = {
				'parcels':proposed_elements,
				'increased_flooding':moreflood,
				'decreased_flooding':floodlowered,
				'new_flooding': newflood,
				'eliminated_flooding':floodEliminated
			}
	return results

def parcel_flood_duration(model, parcel_features, threshold=0.083,  bbox=None,
							gdb=GEODATABASE,
							export_table=False,anno_results={}):
	"""
	this method includes the logic for calculating a flood duration (and avg
	duration) on the given parcels. Returned is a dictionary with each parcel ID
	and a Parcel object with the flooding data populated.
	"""

	#collect the parcels in a dictionary of Parcel objects
	parcel_objects = associate_parcels(model, parcel_features, gdb=gdb, bbox=bbox)

	#grab the list of flooded nodes, and create the dictionary of parcels linked to node IDs
	flooded_nodes = su.subsetElements(model, min=threshold, bbox=bbox, pair_only=True)

	#tally how many were flooded above set durations
	#{minutes : number of parcels with flooding greater than}
	duration_partition = {
				5:0, 10:0, 15:0,
				30:0, 60:0, 120:0
				}
	#calculate average flood duration for each parcel
	parcels_flooded_count = 0

	for id, parcel in parcel_objects.iteritems():

		if len(parcel.nodes) > 0:
			#parcel has nodes associated

			total_parcel_flood_dur = 0.0
			flood_duration = 0.0
			for node in parcel.nodes:

				#look up the flood duration
				node_duration = flooded_nodes.get(node, 0)
				total_parcel_flood_dur += node_duration #for avereage calculation

				#parcel flooding duration assumed to be the max of all adjacent node durations
				flood_duration = max(flood_duration, node_duration)

			avg_flood_duration = total_parcel_flood_dur/len(parcel.nodes)

			parcel.avg_flood_duration = avg_flood_duration
			parcel.flood_duration = flood_duration

			if flood_duration >= threshold:
				#we've found a parcel that is considered flooded
				parcels_flooded_count += 1

			for duration, count in duration_partition.iteritems():
				if flood_duration >= float(duration)/60.0:
					count += 1
					duration_partition.update({duration:count})

	parcels_count = len(parcel_objects)
	parcels_flooded_fraction = float(parcels_flooded_count)/float(parcels_count)

	results = {
				'parcels_flooded_count':parcels_flooded_count,
				'parcels_count':parcels_count,
				'parcels_flooded_fraction':parcels_flooded_fraction,
				'duration_partition':duration_partition
				}

	results_string = "{} ({}%) of {} total".format(parcels_flooded_count, round(parcels_flooded_fraction*100),parcels_count)

	#print results_string

	#partition (detailed) results string
	partitioned_results = "\n"
	for d in sorted(duration_partition):
		perc_of_tot = int(round( float(duration_partition[d]) / float(results['parcels_count']) * 100 ))
		partitioned_results += '>{}mins : {} ({}%)\n'.format(d, duration_partition[d], perc_of_tot)

	#track results for annotation
	anno_results.update({'Total Parcels':results['parcels_count'], '\nParcels Flooded':partitioned_results})

	#add in the actual list of parcels for drawing
	results.update({'parcels':parcel_objects})

	return results

def associate_parcels(model, feature=PARCEL_FEATURES,
						cols = ["PARCELID", "OUTLET", "SUBCATCH", "SHAPE@"],
						bbox=None, gdb=GEODATABASE):

	"""
	create dictionary with keys for each parcel, and sub array containing
	associated nodes. This method expects a shapefile that results from a spatial
	join (one to many) between the given model drainage areas and a parcels
	spatial dataset in the study area.

	Where parcels spatially fall within multiple sheds, they will be
	represented in multiple rows in this shapefile (one to many), with one row
	for each associated shed. given this, this function creates a list of unique
	parcels and arrays with their associated sheds
	"""

	#check if a parcel to node association dicitonary exists, load if possible
	parcel_to_nodes_filename = os.path.join(model.inp.dir, 'parcel_nodes_dict.txt')
	if not os.path.isfile(parcel_to_nodes_filename):
		print 'creating new parcel/node association dict'
		#build the dictionary of parcels, if this hasn't already been done
		features = os.path.join(gdb, feature)
		import arcpy
		parcels_dictionary = {}
		for row in arcpy.da.SearchCursor(features, cols):

			#first check if parcel is in bbox
			jsonkey = 'rings' #for arc polygons
			geometrySections = json.loads(row[3].JSON)[jsonkey]
			parcel_in_bbox=True #assume yes first
			for i, section in enumerate(geometrySections):
				#check if part of geometry is within the bbox, skip if not
				if bbox and len ( [x for x in section if su.pointIsInBox(bbox, x)] ) == 0:
					parcel_in_bbox=False #continue #skip this section if none of it is within the bounding box

			if not parcel_in_bbox:
				continue #skip if not in bbox

			PARCELID = str(row[0])
			if PARCELID in parcels_dictionary:
				#append to existing parcel object's arrays
				parcels_dictionary[PARCELID]['nodes'].append(row[1])
				parcels_dictionary[PARCELID]['sheds'].append(row[2])
			else:
				#new parcel id found. instantiate new object with initial
				#associated nodes and sheds
				#parcel = Parcel(PARCELID, nodes=[row[1]], sheds=[row[2]])
				parcels_dictionary.update({PARCELID:{'nodes':[row[1]], 'sheds':[row[2]]}}  )

		#save for later use
		#print 'writing new parcel/node association dict'
		with open(parcel_to_nodes_filename, 'w') as dictSaveFile:
			pickle.dump(parcels_dictionary, dictSaveFile)

	else:
		#print "loading parcel/node association dict: {}".format(parcel_to_nodes_filename)
		parcels_dictionary = pickle.load( open(parcel_to_nodes_filename, 'r') )
		#print "WARNING: make sure this loaded parcel dict contains all parcels!"


	#create a dictionary of parcel objects
	parcels = {}
	for id, parcel_data in parcels_dictionary.iteritems():
		parcel = Parcel(id, nodes = parcel_data['nodes'], sheds = parcel_data['sheds'])
		parcels.update({id:parcel})


	return parcels
