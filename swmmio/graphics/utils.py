#UTILITY/HELPER FUNCTOINS FOR DRAWING
import pandas as pd
import math
from swmmio.graphics import * #constants


def px_to_irl_coords(df, px_width=4096.0, bbox=None, shift_ratio=None):
	"""
	given a dataframe with element id (as index) and X1, Y1 columns (and
	optionally X2, Y2 columns), return a dataframe with the coords as pixel
	locations based on the targetImgW.
	"""

	df = df.loc[pd.notnull(df.coords)]

	if not bbox:
		xs = [xy[0] for verts in df.coords.tolist() for xy in verts]
		ys = [xy[1] for verts in df.coords.tolist() for xy in verts]
		xmin, ymin, xmax, ymax = (min(xs), min(ys), max(xs), max(ys))
		bbox = [(xmin, ymin),(xmax, ymax)]

	else:
		df = clip_to_box(df, bbox) #clip if necessary
		xmin = float(bbox[0][0])
		ymin = float(bbox[0][1])

	    #find the actual dimensions, use to find scale factor
	height = bbox[1][1] - bbox[0][1]
	width = bbox[1][0] - bbox[0][0]

	if not shift_ratio:
		#to scale down from coordinate to pixels
		shift_ratio = float(px_width / width)
		
	def shft_coords(row):
		#parse through coords (nodes, or link) and adjust for pixel space
		return [(int((xy[0] - xmin)*shift_ratio),
					int((height - xy[1] + ymin)*shift_ratio))
						for xy in row.coords]

	#copy the given df and insert new columns with the shifted coordinates
	draw_coords = df.apply(lambda row:shft_coords(row), axis=1)
	df = df.assign(draw_coords = draw_coords)
	return df, bbox, int(height*shift_ratio),int(width*shift_ratio),shift_ratio

def read_shapefile(shp_path):
	"""
	Read a shapefile into a Pandas dataframe with a 'coords' column holding
	the geometry information. This uses the pyshp package
	"""
	import shapefile

	#read file, parse out the records and shapes
	sf = shapefile.Reader(shp_path)
	fields = [x[0] for x in sf.fields][1:]
	records = sf.records()
	shps = [s.points for s in sf.shapes()]

	#write into a dataframe
	df = pd.DataFrame(columns=fields, data=records)
	df = df.assign(coords=shps)

	return df

def circle_bbox(coordinates, radius=5):
    """the bounding box of a circle given as centriod coordinate and radius"""

    x = coordinates[0]
    y = coordinates[1]
    r = radius

    return (x-r, y-r, x+r, y+r)

def clip_to_box(df, bbox):
	"""clip a dataframe with a coords column to a bounding box"""
	def any_xy_in_box(row, bbox):
		#because im confused with list comprehensions rn
	    return any([point_in_box(bbox, pt) for pt in row])

	coords = df.coords.tolist()
	result = [any_xy_in_box(p, bbox) for p in coords]
	return df.loc[result]


def point_in_box(bbox, point):
	"""check if a point falls with in a bounding box, bbox"""
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

def length_bw_coords(upstreamXY, downstreamXY):

    #return the distance (units based on input) between two points
    x1 = float(upstreamXY[0])
    x2 = float(downstreamXY[0])
    y1 = float(upstreamXY[1])
    y2 = float(downstreamXY[1])

    return math.hypot(x2 - x1, y2 - y1)
