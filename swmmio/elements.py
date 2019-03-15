"""
Objects encapsulating model elements
"""
import swmmio
from swmmio.utils.dataframes import create_dataframeINP, create_dataframeRPT, get_link_coords
from swmmio.tests.data import MODEL_FULL_FEATURES__NET_PATH
from swmmio.defs import HEADERS
from swmmio.utils.spatial import coords_series_to_geometry


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
        self.config = HEADERS[section_name.lower()]

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
                df = create_dataframeINP(self.inp.path, sect, comment_cols=False)
            else:
                df_other = create_dataframeINP(self.inp.path, sect, comment_cols=False)
                df = df.join(df_other)

        if self.rpt:
            for rpt_sect in self.config['rpt_sections']:
                df = df.join(create_dataframeRPT(self.rpt.path, rpt_sect))

        # add conduit coordinates
        xys = df.apply(lambda r: get_link_coords(r, self.inp.coordinates, self.inp.vertices), axis=1)
        df = df.assign(coords=xys.map(lambda x: x[0]))

        # make inlet/outlet node IDs string type
        df.InletNode = df.InletNode.astype(str)
        df.OutletNode = df.OutletNode.astype(str)

        return df

