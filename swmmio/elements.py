"""
Objects encapsulating model elements
"""
import pandas as pd
import swmmio
from swmmio.utils.dataframes import dataframe_from_rpt, get_link_coords, dataframe_from_inp, nodexy
from swmmio.tests.data import MODEL_FULL_FEATURES__NET_PATH
from swmmio.utils.spatial import coords_series_to_geometry, write_geojson
from swmmio.utils.text import get_inp_sections_details

__all__ = ['Links', 'Nodes', 'ModelSection']


class ModelSection(object):
    """
    Base class of a group of model elements.

    :param model: swmmio.Model object
    :param inp_sections: list of node-related sections from the inp file to concatenate in the object
    :param join_sections: list of node-related sections from the inp file to join to the object
    :param rpt_sections: list of node-related sections from the rpt file to join to the object
    :param columns: optional subset of columns used to exclude unwanted columns in the resulting object
    :param geomtype: type of geometry for section [point, linestring, polygon]
    """
    def __init__(self, model, inp_sections, join_sections=None, rpt_sections=None, columns=None,
                 geomtype='point'):
        self.model = model
        self.inp = self.model.inp
        self.rpt = self.model.rpt
        self.inp_sections = inp_sections
        self.join_sections = join_sections if join_sections is not None else []
        self.rpt_sections = rpt_sections if rpt_sections is not None else []
        self.columns = columns
        self.geomtype = geomtype
        self._df = None

    @property
    def dataframe(self):
        """
        Return a Pandas.Dataframe representation of the group

        :return: pd.Dataframe
        """
        return self.__call__()

    @property
    def geojson(self):
        """
        Return a GeoJSON representation of the group

        :return: GeoJSON string
        """
        return write_geojson(self.dataframe, geomtype=self.geomtype)

    @property
    def geodataframe(self):
        """
        Return a GeoPandas.GeoDataFrame representation of the group

        :return: GeoPandas.GeoDataFrame
        """
        # uses GeoPandas
        try:
            import geopandas as gp
        except ImportError:
            raise ImportError('geopandas module needed. Install GeoPandas with conda: ',
                              'conda install geopandas')

        df = self.__call__()
        df['geometry'] = coords_series_to_geometry(df['coords'], geomtype=self.geomtype, dtype='shape')
        df = df.drop(['coords'], axis=1)
        return gp.GeoDataFrame(df, crs=self.model.crs)

    def __call__(self):

        """
        collect all useful and available data related to the conduits and
        organize in one dataframe.
        >>> model = swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)
        >>> conduits_section = ModelSection(model, 'conduits')
        >>> conduits_section()
        """

        # concat inp sections with unique element IDs
        headers = get_inp_sections_details(self.inp.path)
        dfs = [dataframe_from_inp(self.inp.path, sect) for sect in self.inp_sections if sect.upper() in headers]

        # return empty df if no inp sections found
        if len(dfs) == 0:
            return pd.DataFrame()

        df = pd.concat(dfs, axis=0, sort=False)

        # confirm index name is string
        df = df.rename(index=str)

        # join to this any sections with matching IDs (e.g. XSECTIONS)
        for sect in self.join_sections:
            rsuffix = f"_{sect.replace(' ', '_')}"
            df = df.join(dataframe_from_inp(self.inp.path, sect), rsuffix=rsuffix)

        if df.empty:
            return df

        # if there is an RPT available, grab relevant sections
        if self.rpt:
            for rpt_sect in self.rpt_sections:
                df = df.join(dataframe_from_rpt(self.rpt.path, rpt_sect))

        # add coordinates
        if self.geomtype == 'point':
            df = df.join(self.inp.coordinates[['X', 'Y']])
            xys = df.apply(lambda r: nodexy(r), axis=1)
            df = df.assign(coords=xys)

        elif self.geomtype == 'linestring':
            # add conduit coordinates
            xys = df.apply(lambda r: get_link_coords(r, self.inp.coordinates, self.inp.vertices), axis=1)
            df = df.assign(coords=xys.map(lambda x: x[0]))
            # make inlet/outlet node IDs string type
            df.InletNode = df.InletNode.astype(str)
            df.OutletNode = df.OutletNode.astype(str)

        elif self.geomtype == 'polygon':
            p = self.inp.polygons
            p.index = p.index.map(str)
            # take stacked coordinates and orient in list of tuples,
            xys = p.groupby(by=p.index).apply(lambda r: [(xy['X'], xy['Y']) for ix, xy in r.iterrows()])
            # copy the first point to the last position
            xys = xys.apply(lambda r: r + [r[0]])
            df = df.assign(coords=xys)

        # trim to desired columns
        if self.columns is not None:
            df = df[[c for c in self.columns if c in df.columns]]

        self._df = df
        return df


class Nodes(ModelSection):
    """
    Generalized nodes object for working with node-like SWMM objects.

    :param model: swmmio.Model object
    :param inp_sections: list of node-related sections from the inp file to concatenate in the object
    :param join_sections: list of node-related sections from the inp file to join to the object
    :param rpt_sections: list of node-related sections from the rpt file to join to the object
    :param columns: optional subset of columns used to exclude unwanted columns in the resulting object

    >>> from swmmio.examples import spruce
    >>> nodes = Nodes(
    ...     spruce,
    ...     inp_sections=['junctions'],
    ...     rpt_sections=['Node Depth Summary'],
    ...     columns=['InvertElev', 'MaxHGL', 'coords']
    ... )
    >>> nodes.dataframe
          InvertElev  MaxHGL                            coords
    Name
    J3         6.547    8.19  [(459.05800000000005, -113.145)]
    1         17.000   17.94              [(-77.021, -78.321)]
    2         17.000   17.00               [(-84.988, 43.833)]
    3         16.500   16.89     [(-18.6, -71.23899999999999)]
    4         16.000   16.87   [(-67.28399999999999, -37.603)]
    5         15.000   16.00               [(-56.662, 15.507)]
    J2        13.000   13.00               [(238.75, -53.332)]
    >>> # access data as geojson
    >>> nodes.geojson['features'][0]['geometry']
    {"coordinates": [[459.058, -113.145]], "type": "Point"}
    >>> nodes.geojson['features'][0]['properties']
    {'InvertElev': 6.547, 'MaxHGL': 8.19, 'Name': 'J3'}

    """
    def __init__(self, model, inp_sections, join_sections=None, rpt_sections=None, columns=None):
        super().__init__(model, inp_sections, join_sections, rpt_sections, columns,
                         geomtype='point')


class Links(ModelSection):
    """
    Generalized links object for working with link-like SWMM objects.

    :param model: swmmio.Model object
    :param inp_sections: list of link-related sections from the inp file to concatenate in the object
    :param join_sections: list of link-related sections from the inp file to join to the object
    :param rpt_sections: list of link-related sections from the rpt file to join to the object
    :param columns: optional subset of columns used to exclude unwanted columns in the resulting object

    >>> from swmmio.examples import spruce
    >>> conduits = Links(
    ...     spruce,
    ...     inp_sections=['conduits'],
    ...     rpt_sections=['Link Flow Summary'],
    ...     columns=['MaxQ', 'MaxQPerc', 'coords']
    ... )
    >>> conduits.dataframe
           MaxQ  MaxQPerc                                             coords
    Name
    C1:C2  2.45      1.32                    [(0.0, 0.0), (238.75, -53.332)]
    C2.1   0.00      0.00  [(238.75, -53.332), (295.63599999999997, -159....
    1      2.54      1.10  [(-77.021, -78.321), (-67.28399999999999, -37....
    2      2.38      1.03  [(-67.28399999999999, -37.603), (-56.662, 15.5...
    3      1.97      0.67                    [(-56.662, 15.507), (0.0, 0.0)]
    4      0.16      0.10  [(-18.6, -71.23899999999999), (-23.91099999999...
    5      0.00      0.00  [(-84.988, 43.833), (-85.87299999999999, 19.93...
    >>> # access data as geojson
    >>> conduits.geojson['features'][0]['geometry']
    {"coordinates": [[0.0, 0.0], [238.75, -53.332]], "type": "LineString"}
    >>> conduits.geojson['features'][0]['properties']
    {'MaxQ': 2.45, 'MaxQPerc': 1.32, 'Name': 'C1:C2'}
    """
    def __init__(self, model, inp_sections, join_sections=None, rpt_sections=None, columns=None):
        super().__init__(model, inp_sections, join_sections, rpt_sections, columns,
                         geomtype='linestring')

