import os, shutil
import pandas as pd
from swmmio.version_control import inp
from definitions import *


def create_map(model1, model2=None, bbox=None, crs=None, filename=None, subset=None):

    """
    export model as a geojson object
    """

    import geojson
    from geojson import Point, LineString, Feature, GeometryCollection, FeatureCollection
    try: import pyproj
    except ImportError:
        raise ImportError('pyproj module needed. get this package here: ',
                        'https://pypi.python.org/pypi/pyproj')


    if model2 is not None:
        changes = inp.Change(model1, model2, section='[CONDUITS]')
        df = pd.concat([changes.added, changes.altered])
        subset = df.index.tolist()
        
    # else:
    #     model2 = model1 #stupid, for file path


    if crs is None:
        #default coordinate system (http://spatialreference.org/ref/epsg/2272/):
        #NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet
        crs =  {"type": "name","properties": {"name": "EPSG:2272"}}

    pa_plane = pyproj.Proj(init='epsg:2272', preserve_units=True)
    wgs = pyproj.Proj(proj='latlong', datum='WGS84', ellps='WGS84') #google maps, etc


    geometries = [] #array of features
    # # collect the nodes
    # for k,v in model1.list_objects('node', bbox).items():
    #     props = {'flood_duration':v.flood_duration, 'id':v.id}
    #     lat,lng = pyproj.transform(pa_plane, wgs, *v.coordinates)
    #     geometry = Point((lat,lng), properties=props)
    #     geometries.append(geometry)

    #collect the links
    for k,v in model2.list_objects('conduit', bbox, subset=subset).items():
        props = {
            'MaxQPercent':v.maxQpercent,
            'id':v.id,
            'lifecycle':v.lifecycle,
            'geom1':v.geom1,
            'geom2':v.geom2,
            }

        latlngs = [pyproj.transform(pa_plane, wgs, *xy) for xy in v.coordinates]
        geometry = LineString(latlngs, properties=props)
        geometries.append(geometry)


    if filename is None:
        filename = os.path.join(model2.inp.dir,
                                REPORT_DIR_NAME,
                                model2.name + '.html')

    #start writing that thing
    with open(BASEMAP_PATH, 'r') as bm:
        with open(filename, 'wb') as newmap:
            for line in bm:
                if 'SWMMIO DUMP JSON DATA HERE' in line:
                    newmap.write('data = ')
                    newmap.write(geojson.dumps(FeatureCollection(geometries, crs=crs)))
                else:
                    newmap.write(line)
