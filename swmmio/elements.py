"""
Objects encapsulating model elements
"""
import swmmio
from swmmio.utils.dataframes import create_dataframeINP, create_dataframeRPT, get_link_coords
from swmmio.tests.data import MODEL_FULL_FEATURES__NET_PATH
import pandas as pd


class ModelSection(object):
    def __init__(self, model, section_name):
        """
        Base class of a group of model elements.
        :param model: swmmio.Model object
        :param section_name: name of section of model
        """
        self.model = model
        self.section_name = section_name

    # def to_geojson(self, target_path=None):
    #     """
    #     Return a GeoJSON representation of the group
    #     :param target_path: target of GeoJSON representation of elements
    #     :return: GeoJSON representation of elements
    #     """

    def __call__(self, data=None):

        """
        collect all useful and available data related to the conduits and
        organize in one dataframe.
        >>> model = swmmio.Model(MODEL_FULL_FEATURES__NET_PATH)
        >>> conduits_section = ModelSection(model, 'conduits')
        >>> conduits_section()
        """

        # parse out the main objects of this model
        inp = self.model.inp
        rpt = self.model.rpt

        # create dataframes of relevant sections from the INP
        conduits_df = create_dataframeINP(inp.path, "[CONDUITS]", comment_cols=False)
        xsections_df = create_dataframeINP(inp.path, "[XSECTIONS]", comment_cols=False)
        conduits_df = conduits_df.join(xsections_df)
        coords_df = create_dataframeINP(inp.path, "[COORDINATES]")  # .drop_duplicates()

        if rpt:
            # create a dictionary holding data from an rpt file, if provided
            link_flow_df = create_dataframeRPT(rpt.path, "Link Flow Summary")
            conduits_df = conduits_df.join(link_flow_df)

        # add conduit coordinates
        # the xys.map() junk is to unpack a nested list
        verts = create_dataframeINP(inp.path, '[VERTICES]')
        xys = conduits_df.apply(lambda r: get_link_coords(r, coords_df, verts), axis=1)
        df = conduits_df.assign(coords=xys.map(lambda x: x[0]))

        # add conduit up/down inverts and calculate slope
        elevs = self.model.nodes()[['InvertElev']]
        df = pd.merge(df, elevs, left_on='InletNode', right_index=True, how='left')
        df = df.rename(index=str, columns={"InvertElev": "InletNodeInvert"})
        df = pd.merge(df, elevs, left_on='OutletNode', right_index=True, how='left')
        df = df.rename(index=str, columns={"InvertElev": "OutletNodeInvert"})
        df['UpstreamInvert'] = df.InletNodeInvert + df.InletOffset
        df['DownstreamInvert'] = df.OutletNodeInvert + df.OutletOffset
        df['SlopeFtPerFt'] = (df.UpstreamInvert - df.DownstreamInvert) / df.Length

        df.InletNode = df.InletNode.astype(str)
        df.OutletNode = df.OutletNode.astype(str)

        self.model._conduits_df = df

        return df

