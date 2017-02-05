from definitions import ROOT_DIR
import geojson
import json
import pandas as pd
from geojson import Point, LineString, Polygon, FeatureCollection, Feature
import os, shutil


def create_geojson(df, inproj='epsg:2272', geomtype='linestring', filename=None):

    try: import pyproj
    except ImportError:
        raise ImportError('pyproj module needed. get this package here: ',
                        'https://pypi.python.org/pypi/pyproj')

    #SET UP THE TO AND FROM COORDINATE PROJECTION
    pa_plane = pyproj.Proj(init=inproj, preserve_units=True)
    wgs = pyproj.Proj(proj='latlong', datum='WGS84', ellps='WGS84') #google maps, etc

    #CONVERT THE DF INTO JSON
    records = json.loads(df.to_json(orient='records'))

    #ITERATE THROUGH THE RECORDS AND CREATE GEOJSON OBJECTS
    features = []
    for rec in records:

        coordinates =rec['coords']
        del rec['coords'] #delete the coords so they aren't in the properties

        #transform to the typical 'WGS84' coord system
        latlngs = [pyproj.transform(pa_plane, wgs, *xy) for xy in coordinates]
        if geomtype == 'linestring':
            geometry = LineString(latlngs)
        elif geomtype == 'point':
            geometry = Point(latlngs)
        elif geomtype == 'polygon':
            geometry = Polygon([latlngs])

        feature = Feature(geometry=geometry, properties=rec)
        features.append(feature)

    if filename is not None:
        with open(filename, 'wb') as f:
            f.write(json.dumps(FeatureCollection(features)))
        return filename

    else:
        return FeatureCollection(features)

def write_shapefile(df, filename, geomtype='line', prj=None):

    """
    create a shapefile given a pandas Dataframe that has coordinate data in a
    column called 'coords'.
    """

    import shapefile
    df['Name'] = df.index

    #create a shp file writer object of geom type 'point'
    if geomtype == 'point':
        w = shapefile.Writer(shapefile.POINT)
    elif geomtype == 'line':
        w = shapefile.Writer(shapefile.POLYLINE)

    #use the helper mode to ensure the # of records equals the # of shapes
    #(shapefile are made up of shapes and records, and need both to be valid)
    w.autoBalance = 1

    #add the fields
    for fieldname in df.columns:
        w.field(fieldname, "C")

    for k, row in df.iterrows():
        w.record(*row.tolist())
        w.line(parts = [row.coords])

    w.save(filename)

    #add projection data to the shapefile,
    if prj is None:
        #if not sepcified, the default, projection is used (PA StatePlane)
        prj = os.path.join(ROOT_DIR, 'swmmio/defs/default.prj')
    prj_filepath = os.path.splitext(filename)[0] + '.prj'
    shutil.copy(prj, prj_filepath)

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
