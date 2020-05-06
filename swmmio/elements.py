"""
Objects encapsulating model elements
"""
import pandas as pd
import swmmio
from swmmio.utils.dataframes import dataframe_from_rpt, get_link_coords, dataframe_from_inp, nodexy
from swmmio.tests.data import MODEL_FULL_FEATURES__NET_PATH
from swmmio.utils.spatial import coords_series_to_geometry, write_geojson
from swmmio.utils.text import get_inp_sections_details


class ModelSection(object):
    def __init__(self, model, inp_sections, join_sections=None, rpt_sections=None, columns=None,
                 geomtype='point'):
        """
        Base class of a group of model elements.
        :param model: swmmio.Model object
        :param section_name: name of section of model
        """
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
        # uses GeoPandas
        try:
            import geopandas as gp
        except ImportError:
            raise ImportError('geopandas module needed. Install GeoPandas with conda: ',
                              'conda install geopandas')

        df = self.__call__()
        df['geometry'] = coords_series_to_geometry(df['coords'], geomtype=self.geomtype, format='shape')
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

            # take stacked coordinates and orient in list of tuples,
            xys = p.groupby(by=p.index).apply(lambda r: [(xy['X'], xy['Y']) for ix, xy in r.iterrows()])
            # copy the first point to the last position
            xys = xys.apply(lambda r: r + [r[0]])
            df = df.assign(coords=xys)

        # confirm index name is string
        df = df.rename(index=str)

        # trim to desired columns
        if self.columns is not None:
            df = df[[c for c in self.columns if c in df.columns]]

        self._df = df
        return df


class Nodes(ModelSection):
    def __init__(self, model, inp_sections, join_sections=None, rpt_sections=None, columns=None):

        super().__init__(model, inp_sections, join_sections, rpt_sections, columns,
                         geomtype='point')


class Links(ModelSection):
    def __init__(self, model, inp_sections, join_sections=None, rpt_sections=None, columns=None):
        super().__init__(model, inp_sections, join_sections, rpt_sections, columns,
                         geomtype='linestring')

