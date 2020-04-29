"""
Objects encapsulating model elements
"""
import math
import swmmio
from swmmio.utils.dataframes import dataframe_from_rpt, get_link_coords, dataframe_from_inp
from swmmio.tests.data import MODEL_FULL_FEATURES__NET_PATH
from swmmio.defs import COMPOSITE_OBJECTS
from swmmio.utils.spatial import coords_series_to_geometry, write_geojson
import pandas as pd

from swmmio.utils.text import get_inp_sections_details


def dataframe_from_composite(model, inp_sections, rpt_sections, geometry_type):

    for ix, sect in enumerate(inp_sections):
        if ix == 0:
            df = dataframe_from_inp(model.inp.path, sect)
        else:
            df_other = dataframe_from_inp(model.inp.path, sect)
            df = df.join(df_other)

    if df.empty:
        return df

    # if there is an RPT available, grab relevant sections
    if model.rpt:
        for rpt_sect in rpt_sections:
            df = df.join(dataframe_from_rpt(model.rpt.path, rpt_sect))

    # add conduit coordinates
    xys = df.apply(lambda r: get_link_coords(r, self.inp.coordinates, self.inp.vertices), axis=1)
    df = df.assign(coords=xys.map(lambda x: x[0]))

    # make inlet/outlet node IDs string type
    df.InletNode = df.InletNode.astype(str)
    df.OutletNode = df.OutletNode.astype(str)

    nodes = model.nodes(inp_sections='storage', rpt_sections='Node Inflow Summary')
    nodes.to_geojson('nodes.geojson')
    model.nodes.geojson()


class Links(object):
    def __init__(self, model, inp_sections, join_sections=None, rpt_sections=None, columns=None):

        self.model = model
        self.inp_sections = inp_sections
        self.join_sections = join_sections if join_sections is not None else []
        self.rpt_sections = rpt_sections if rpt_sections is not None else []
        self.columns = columns
        self._df = None

    @property
    def dataframe(self):
        return self.__call__()

    @property
    def geojson(self):
        return write_geojson(self.dataframe, geomtype='linestring')

    @property
    def geodataframe(self):
        # uses GeoPandas
        try:
            import geopandas as gp
        except ImportError:
            raise ImportError('geopandas module needed. Install GeoPandas with conda: ',
                              'conda install geopandas')

        df = self.__call__()
        df['geometry'] = coords_series_to_geometry(df['coords'], geomtype='linestring', format='shape')
        df = df.drop(['coords'], axis=1)
        return gp.GeoDataFrame(df, crs=self.model.crs)

    def __call__(self):

        model = self.model
        inp = model.inp
        inp_sections = self.inp_sections
        join_sections = self.join_sections
        rpt_sections = self.rpt_sections
        headers = get_inp_sections_details(inp.path)

        # concat inp sections with unique element IDs
        dfs = [dataframe_from_inp(inp.path, sect) for sect in inp_sections if sect.upper() in headers]
        df = pd.concat(dfs, axis=0, sort=False)

        # join to this any sections with matching IDs (e.g. XSECTIONS)
        for sect in join_sections:
            df = df.join(dataframe_from_inp(inp.path, sect))

        if df.empty:
            return df

        # if there is an RPT available, grab relevant sections
        if model.rpt:
            for rpt_sect in rpt_sections:
                df = df.join(dataframe_from_rpt(model.rpt.path, rpt_sect))

        # add conduit coordinates
        xys = df.apply(lambda r: get_link_coords(r, model.inp.coordinates, model.inp.vertices), axis=1)
        df = df.assign(coords=xys.map(lambda x: x[0]))

        # make inlet/outlet node IDs string type
        df.InletNode = df.InletNode.astype(str)
        df.OutletNode = df.OutletNode.astype(str)

        # trim to desired columns
        if self.columns is not None:
            df = df[[c for c in self.columns if c in df.columns]]

        self._df = df
        return df


class Nodes(object):
    def __init__(self, model, inp_sections, join_sections=None, rpt_sections=None, columns=None):

        self.model = model
        self.inp_sections = inp_sections
        self.join_sections = join_sections if join_sections is not None else []
        self.rpt_sections = rpt_sections if rpt_sections is not None else []
        self.columns = columns
        self._df = None

    @property
    def dataframe(self):
        return self.__call__()

    @property
    def geojson(self):
        return write_geojson(self.dataframe, geomtype='point')

    @property
    def geodataframe(self):
        # uses GeoPandas
        try:
            import geopandas as gp
        except ImportError:
            raise ImportError('geopandas module needed. Install GeoPandas with conda: ',
                              'conda install geopandas')

        df = self.__call__()
        df['geometry'] = coords_series_to_geometry(df['coords'], geomtype='point', format='shape')
        df = df.drop(['coords'], axis=1)
        return gp.GeoDataFrame(df, crs=self.model.crs)

    def __call__(self):

        model = self.model
        inp = model.inp
        inp_sections = self.inp_sections
        join_sections = self.join_sections
        rpt_sections = self.rpt_sections
        headers = get_inp_sections_details(inp.path)

        # concat inp sections with unique element IDs
        dfs = [dataframe_from_inp(inp.path, sect) for sect in inp_sections if sect.upper() in headers]
        df = pd.concat(dfs, axis=0, sort=False)

        # join to this any sections with matching IDs (e.g. XSECTIONS)
        for sect in join_sections:
            rsuffix = f"_{sect.replace(' ', '_')}"
            df = df.join(dataframe_from_inp(inp.path, sect), rsuffix=rsuffix)

        if df.empty:
            return df

        # if there is an RPT available, grab relevant sections
        if model.rpt:
            for rpt_sect in rpt_sections:
                df = df.join(dataframe_from_rpt(model.rpt.path, rpt_sect))

        # add coordinates
        def nodexy(row):
            if math.isnan(row.X) or math.isnan(row.Y):
                return None
            else:
                return [(row.X, row.Y)]

        df = df.join(model.inp.coordinates[['X', 'Y']])
        xys = df.apply(lambda r: nodexy(r), axis=1)
        df = df.assign(coords=xys)

        # confirm index name is string
        df = df.rename(index=str)

        # trim to desired columns
        if self.columns is not None:
            df = df[[c for c in self.columns if c in df.columns]]

        self._df = df
        return df


class ModelSection(object):
    def __init__(self, model, section_name):
        """
        Base class of a group of model elements.
        :param model: swmmio.Model object
        :param section_name: name of section of model
        """
        self.model = model
        self.inp = self.model.inp
        self.rpt = self.model.rpt
        self.section_name = section_name
        self.config = COMPOSITE_OBJECTS[section_name.lower()]

    # def to_geojson(self, target_path=None):
    #     """
    #     Return a GeoJSON representation of the group
    #     :param target_path: target of GeoJSON representation of elements
    #     :return: GeoJSON representation of elements
    #     """
    def to_gdf(self):
        # uses GeoPandas
        try:
            import geopandas as gp
        except ImportError:
            raise ImportError('geopandas module needed. Install GeoPandas with conda: ',
                              'conda install geopandas')

        df = self.__call__()
        df['geometry'] = coords_series_to_geometry(df['coords'], geomtype='linestring', format='shape')
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

        # create dataframes of relevant sections from the INP
        for ix, sect in enumerate(self.config['inp_sections']):
            if ix == 0:
                df = dataframe_from_inp(self.inp.path, sect)
            else:
                df_other = dataframe_from_inp(self.inp.path, sect)
                df = df.join(df_other)

        if df.empty:
            return df

        # if there is an RPT available, grab relevant sections
        if self.rpt:
            for rpt_sect in self.config['rpt_sections']:
                df = df.join(dataframe_from_rpt(self.rpt.path, rpt_sect))

        # add conduit coordinates
        xys = df.apply(lambda r: get_link_coords(r, self.inp.coordinates, self.inp.vertices), axis=1)
        df = df.assign(coords=xys.map(lambda x: x[0]))

        # make inlet/outlet node IDs string type
        df.InletNode = df.InletNode.astype(str)
        df.OutletNode = df.OutletNode.astype(str)

        return df
