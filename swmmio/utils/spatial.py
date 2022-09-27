from swmmio.defs.config import ROOT_DIR
from swmmio.tests.data import MODEL_FULL_FEATURES_XY
import json
import pandas as pd
from geojson import Point, LineString, Polygon, FeatureCollection, Feature
import os
import shutil


def change_crs(series, in_crs, to_crs):
    """
    Change the projection of a series of coordinates
    :param series:
    :param to_crs:
    :param in_crs:
    :return: series of reprojected coordinates
    >>> import swmmio
    >>> m = swmmio.Model(MODEL_FULL_FEATURES_XY)
    >>> proj4_str = '+proj=tmerc +lat_0=36.16666666666666 +lon_0=-94.5 +k=0.9999411764705882 +x_0=850000 +y_0=0 +datum=NAD83 +units=us-ft +no_defs' #"+init=EPSG:102698"
    >>> m.crs = proj4_str
    >>> nodes = m.nodes()
    >>> change_crs(nodes['coords'], proj4_str, "EPSG:4326")
    Name
    J3    [(39.236286854940964, -94.64346373821752)]
    1      [(39.23851590020802, -94.64756446847099)]
    2       [(39.2382157223383, -94.64468629488778)]
    3      [(39.23878251491925, -94.64640342340165)]
    4     [(39.238353081411915, -94.64603818939938)]
    5      [(39.23797714290924, -94.64589184224722)]
    J2     [(39.23702605103406, -94.64543916929885)]
    J4     [(39.23633648359375, -94.64190240294558)]
    J1     [(39.23723558954326, -94.64583338271147)]
    Name: coords, dtype: object
    """
    try:
        import pyproj
        from pyproj import Transformer
    except ImportError:
        raise ImportError('pyproj module needed. get this package here: ',
                          'https://pypi.python.org/pypi/pyproj')

    # SET UP THE TO AND FROM COORDINATE PROJECTION
    transformer = Transformer.from_crs(in_crs, to_crs, always_xy=True)

    # convert coords in coordinates, vertices, and polygons inp sections
    # transform to the typical 'WGS84' coord system
    def get_xys(xy_row):
        # need to reverse to lat/long after conversion
        return [transformer.transform(x, y) for x, y in xy_row]

    if isinstance(series, pd.Series):

        # unpack the nested coords
        xs = [xy[0][0] for xy in series.to_list()]
        ys = [xy[0][1] for xy in series.to_list()]

        # transform the whole series at once
        xs_trans, ys_trans = transformer.transform(xs, ys)

        # increase nest level and return pd.Series
        return pd.Series(index=series.index, data=[[coords] for coords in zip(xs_trans, ys_trans)])

    if isinstance(series, pd.DataFrame):
        # zipped_coords = list(zip(series.X, series.Y))
        xs_trans, ys_trans = transformer.transform(series.X, series.Y)
        df = pd.DataFrame(data=zip(xs_trans, ys_trans), columns=["X", "Y"], index=series.index)
        return df
    elif isinstance(series, (list, tuple)):
        if isinstance(series[0], (list, tuple)):
            # unpack the nested coords
            xs = [x for x, y in series]
            ys = [y for x, y in series]
            return list(zip(transformer.transform(xs, ys)))
        else:
            return transformer.transform(*series)


def coords_series_to_geometry(coords, geomtype='linestring', dtype='geojson'):
    """
    Convert a series of coords (list of list(s)) to a series of geometry objects.
    :param coords: series of lists of xy coordinates
    :param geomtype: geometry type of target 
    :param dtype: format of geometry objects to be created ('geojson', 'shapely')
    :return: series of geometry objects
    >>> import swmmio
    >>> model = swmmio.Model(MODEL_FULL_FEATURES_XY)
    >>> nodes = model.nodes()
    >>> geoms = coords_series_to_geometry(nodes['coords'], geomtype='point')
    >>> geoms.iloc[0]
    {"coordinates": [2748073.3060000003, 1117746.087], "type": "Point"}
    """

    # detect whether LineString or Point should be used
    geomtype = geomtype.lower()
    if geomtype == 'linestring':
        geoms = [LineString(latlngs) for latlngs in coords]
    elif geomtype == 'point':
        geoms = [Point(latlngs[0]) for latlngs in coords]
    elif geomtype == 'polygon':
        geoms = [Polygon([latlngs]) for latlngs in coords]

    if dtype.lower() == 'shape':
        # convert to shapely objects
        try:
            from shapely.geometry import shape
        except ImportError:
            raise ImportError('shapely module needed. Install it via GeoPandas with conda: ',
                              'conda install geopandas')
        geoms = [shape(g) for g in geoms]

    return pd.Series(index=coords.index, name='geometry', data=geoms)


def write_geojson(df, filename=None, geomtype='linestring', drop_na=True):
    """
    convert dataframe with coords series to geojson format
    :param df: target dataframe
    :param filename: optional path of new file to contain geojson
    :param geomtype: geometry type [linestring, point, polygon]
    :param drop_na: whether to remove properties with None values
    :return: geojson.FeatureCollection

    >>> from swmmio.examples import philly
    >>> geoj = write_geojson(philly.links.dataframe, drop_na=True)
    >>> print(json.dumps(geoj['features'][0]['properties'], indent=2))
    {
      "InletNode": "J1-025",
      "OutletNode": "J1-026",
      "Length": 309.456216,
      "Roughness": 0.014,
      "InOffset": 0,
      "OutOffset": 0.0,
      "InitFlow": 0,
      "MaxFlow": 0,
      "Shape": "CIRCULAR",
      "Geom1": 1.25,
      "Geom2": 0,
      "Geom3": 0,
      "Geom4": 0,
      "Barrels": 1,
      "Name": "J1-025.1"
    }
    >>> print(json.dumps(geoj['features'][0]['geometry'], indent=2))
    {
      "type": "LineString",
      "coordinates": [
        [
          2746229.223,
          1118867.764
        ],
        [
          2746461.473,
          1118663.257
        ]
      ]
    }
    """

    # CONVERT THE DF INTO JSON
    df['Name'] = df.index  # add a name column (we wont have the index)
    records = json.loads(df.to_json(orient='records'))

    # ITERATE THROUGH THE RECORDS AND CREATE GEOJSON OBJECTS
    features = []
    for rec in records:

        coordinates = rec['coords']
        del rec['coords']  # delete the coords so they aren't in the properties
        if drop_na:
            rec = {k: v for k, v in rec.items() if v is not None}
        latlngs = coordinates

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

    # create a shp file writer object of geom type 'point'
    if geomtype == 'point':
        w = shapefile.Writer(filename, shapefile.POINT, autoBalance=True)
    elif geomtype == 'line':
        w = shapefile.Writer(filename, shapefile.POLYLINE, autoBalance=True)
    elif geomtype == 'polygon':
        w = shapefile.Writer(filename, shapefile.POLYGON, autoBalance=True)

    # add the fields
    for fieldname in df.columns:
        w.field(fieldname, "C")

    for k, row in df.iterrows():
        w.record(*row.tolist())
        if geomtype == 'line':
            w.line([row.coords])
        if geomtype == 'point':
            w.point(*row.coords[0])

    w.close()

    # add projection data to the shapefile,
    if prj is None:
        # if not sepcified, the default, projection is used (PA StatePlane)
        prj = os.path.join(ROOT_DIR, 'swmmio/defs/default.prj')
    prj_filepath = os.path.splitext(filename)[0] + '.prj'
    shutil.copy(prj, prj_filepath)


def read_shapefile(shp_path):
    """
        Read a shapefile into a Pandas dataframe with a 'coords' column holding
        the geometry information. This uses the pyshp package
        """
    import shapefile

    # read file, parse out the records and shapes
    sf = shapefile.Reader(shp_path)
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]

    # write into a dataframe
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)

    return df


def centroid_and_bbox_from_coords(coords):
    """
    return a bounding box that encapsulates all coordinates
    :param coords: pd.Series of coordinates
    :return: boudning list of coordinates
    """
    if isinstance(coords, pd.Series):
        # assume the series with coords format [(x1, y1), (x2, y2), ...]
        coords = coords.to_list()[0]
    elif isinstance(coords, pd.DataFrame):
        # assume dataframe with X, Y columns
        coords = list(zip(coords.X, coords.Y))

    xs = [xys[0] for xys in coords]
    ys = [xys[1] for xys in coords]

    # center
    xc = sum(xs) / len(xs)
    yc = sum(ys) / len(ys)

    # bbox
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)

    return (xc, yc), [x1, y1, x2, y2]

