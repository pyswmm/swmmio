#Module is intended to provide high level access to post processing routines
#such that standard reporting and figures can be generated to report on the
#perfomance of given SFR alternatives/options
from swmmio.reporting.functions import conduits_cost_estimate
from swmmio.damage import parcels
from swmmio.graphics import swmm_graphics as sg
from swmmio.graphics import drawing
from swmmio.utils import spatial
from swmmio.version_control.inp import INPSectionDiff
from swmmio import swmmio
import math
import os
import pandas as pd
from swmmio.defs.config import BETTER_BASEMAP_PATH
from swmmio.defs.constants import d68d70, study_area
import geojson


class FloodReport(object):
    def __init__(self, model=None, parcel_node_df=None, parcel_node_join_csv=None,
                 threshold=0.0833):
        """
        Report of parcel flood duration of a given swmmio.Model object
        """
        self.total_parcel_count = None
        self.model = None
        self.scenario = None
        self.parcel_flooding = None
        self.cost_estimate = None
        self.new_conduits_geojson = None
        self.parcel_hrs_flooded = None
        self.parcel_vol_flooded = None

        if model is not None:
            if parcel_node_df is None:
                #read csv if df not provided
                parcel_node_df = pd.read_csv(parcel_node_join_csv)

            self.total_parcel_count = len(parcel_node_df.PARCELID.unique())
            self.model = model
            self.scenario = model.scenario
            self.parcel_flooding = parcels.flood_duration(model.nodes(),
                                                          parcel_node_df,
                                                          threshold=threshold)
            self.parcel_hrs_flooded = self.parcel_flooding.HoursFlooded.sum()
            subs = self.model.subcatchments()
            nodes = self.model.nodes()
            self.runoff_vol_mg = subs.RunoffMGAccurate.sum()
            self.flood_vol_mg = nodes.TotalFloodVol.sum()

    def __str__(self):
        """print friendly"""
        a = '{}\n'.format(self.model.name)
        b = self.duration_partition()
        c = '\nRunoff: {}MG'.format(round(self.runoff_vol_mg, 1))

        ffrac = round(self.flood_vol_mg / self.runoff_vol_mg *100, 1)
        d = 'Volume Flooded: {}MG ({}%)'.format(round(self.flood_vol_mg, 1), ffrac)

        return '\n'.join([a]+ b + [c, d])


    def duration_partition(self, partitions=[5, 10, 15, 30, 60, 120], raw=False):
        pflood = self.parcel_flooding
        pcount = self.total_parcel_count
        results = []
        for dur in partitions:
            n = len(pflood.loc[pflood.HoursFlooded > dur/60.0])
            frac = n/float(pcount)*100.0
            if raw:

                results.append(s)
            else:
                s = '{}mins: {} ({}%)'.format(dur, n, round(frac,1))
            results.append(s)
        return results


class ComparisonReport(object):
    def __init__(self, baseline_report, alt_report, additional_costs=None,
                 join_data=None):
        """
        Report object representing a comparison of a baseline report to another
        (proposed conditions) report
        """
        basemodel = baseline_report.model
        altmodel = alt_report.model
        baseline_flooding = baseline_report.parcel_flooding
        proposed_flooding = alt_report.parcel_flooding

        conduitdiff = INPSectionDiff(basemodel, altmodel, '[CONDUITS]')
        new_cond_ids = pd.concat([conduitdiff.added, conduitdiff.altered]).index

        self.baseline_report = baseline_report
        self.alt_report = alt_report

        #sort out the new and "altered" conduits
        self.newconduits = altmodel.conduits().loc[new_cond_ids]
        self.newconduits.loc[conduitdiff.altered.index, 'Category'] = 'Replaced'
        self.newconduits.loc[conduitdiff.added.index, 'Category'] = 'Proposed'
        self.new_ix = self.newconduits.index

        #human readable name
        self.name = '{} vs {} Report'.format(basemodel.name, altmodel.name)
        phase_diff = list(set(altmodel.name.split('_')) - set(basemodel.name.split('_')))
        phase_diff = ', '.join(phase_diff[:-1]) + ', and {}'.format(phase_diff[-1])
        self.description = 'Adding {} to {}'.format(phase_diff, basemodel.name)

        #calculate the proposed sewer mileage
        proposed_ft = self.newconduits.Length.sum()#conduitdiff.added.Length.sum() + conduitdiff.altered.Length.sum()
        self.sewer_miles_new = proposed_ft / 5280.0

        #ADD ANY ADDITIONAL DATA TO THE NEW CONDIUTS (FEASIBILITY, REAL GEOM etc)
        if join_data is not None:
            joindf = pd.read_csv(join_data, index_col=0)
            self.newconduits = self.newconduits.join(joindf)

        #COST ESTIMATION
        self.newconduits = conduits_cost_estimate(self.newconduits, additional_costs)
        self.cost_estimate = self.newconduits.TotalCostEstimate.sum() / math.pow(10, 6)

        #MEASURE THE FLOOD REDUCTION IMPACT
        self.flood_comparison = parcels.compare_flood_duration(baseline_flooding,
                                                               proposed_flooding)
        self.impact = self.flood_comparison.Category.value_counts()

        df = self.flood_comparison
        parcel_hours_reduction = df.loc[df.Category.isin(['decreased_flooding',
                                                          'eliminated_flooding']),
                                        'DeltaHours']

        parcel_hours_increased = df.loc[df.Category == 'increased_flooding','DeltaHours']
        parcel_hours_new = df.loc[df.Category == 'new_flooding','DeltaHours']
        self.parcel_hours_reduced = - sum(parcel_hours_reduction)
        self.parcel_hours_increased = sum(parcel_hours_increased)
        self.parcel_hours_new = sum(parcel_hours_new)

        self.summary_dict = {
            'parcel_hours_reduced':self.parcel_hours_reduced,
            'parcel_hours_increased':self.parcel_hours_increased,
            'parcel_hours_new':self.parcel_hours_new,
            'description':self.description,
            'cost_estimate':self.cost_estimate,
            'baseline_name':self.baseline_report.model.name,
            'alt_name':self.alt_report.model.name,
            'sewer_miles_new':self.sewer_miles_new,
        }



    def write(self, rpt_dir):
        #write cost per sewer segment spreadsheet
        self.newconduits.to_csv(os.path.join(rpt_dir,'cost_estimate.csv'))
        self.flood_comparison.to_csv(os.path.join(rpt_dir,'parcel_flood_comparison.csv'))

        #write parcel json files
        parcels = spatial.read_shapefile(sg.config.parcels_shapefile)
        parcels = parcels[['PARCELID', 'ADDRESS', 'OWNER1', 'coords']]
        flooded = self.flood_comparison
        flooded = flooded.loc[flooded.Category.notnull()] #parcels with significant flood delta
        flooded = pd.merge(flooded, parcels, right_on='PARCELID', left_index=True)
        colors = flooded.apply(lambda row:'#%02x%02x%02x' % drawing.parcel_draw_color(row, style='delta'), axis=1)
        flooded = flooded.assign(fill=colors)
        geoparcelpath = os.path.join(rpt_dir,'delta_parcels.json')
        spatial.write_geojson(flooded, filename=geoparcelpath, geomtype='polygon')

        #write new conduit json, shapefiles
        shpdir = os.path.join(os.path.dirname(rpt_dir), 'shapefiles')
        if not os.path.exists(shpdir):os.mkdir(shpdir)
        geocondpath = os.path.join(rpt_dir,'new_conduits.json')
        shpcondpath = os.path.join(shpdir, self.alt_report.model.inp.name + '_new_conduits.shp')
        spatial.write_geojson(self.newconduits, filename=geocondpath)
        spatial.write_shapefile(self.newconduits, filename=shpcondpath)

        #write node and conduit report csvs
        self.alt_report.model.nodes().to_csv(os.path.join(rpt_dir,'nodes.csv'))
        self.alt_report.model.conduits().to_csv(os.path.join(rpt_dir,'conduits.csv'))

        #write a html map
        with open (geocondpath, 'r') as f:
            geo_conduits = geojson.loads(f.read())


        proposed_flooded = self.alt_report.parcel_flooding
        proposed_flooded = pd.merge(proposed_flooded, parcels, right_on='PARCELID', left_index=True)
        geo_parcels = spatial.write_geojson(proposed_flooded)
        # with open (geoparcelpath, 'r') as f:
        #     geo_parcels = geojson.loads(f.read())

        with open(BETTER_BASEMAP_PATH, 'r') as bm:
            filename = os.path.join(os.path.dirname(geocondpath), self.alt_report.model.name + '.html')
            with open(filename, 'wb') as newmap:
                for line in bm:
                    if '//INSERT GEOJSON HERE ~~~~~' in line:
                        newmap.write('conduits = {};\n'.format(geojson.dumps(geo_conduits)))
                        newmap.write('nodes = {};\n'.format(0))
                        newmap.write('parcels = {};\n'.format(geojson.dumps(geo_parcels)))
                    else:
                        newmap.write(line)


        #create figures
    def generate_figures(self, rpt_dir, parcel_shp_df, bbox=d68d70):

        basemodel = self.baseline_report.model
        altmodel = self.alt_report.model
        files = '{}\n{}'.format(basemodel.inp.path, altmodel.inp.path)


        #SIMPLE PLAN VIEW OF OPTION (showing new conduits)
        conduits = altmodel.conduits()
        pth = os.path.join(rpt_dir, '00 Proposed Infrastructure.png')
        conduits['draw_color'] = '#bebeb4' #default color
        conduits['draw_size'] = conduits.Geom1
        conduits.loc[self.new_ix, 'draw_color'] = '#1414e6' #new cond col
        conduits.loc[self.new_ix,'draw_size'] = conduits.loc[self.new_ix,'Geom1']*2
        sg.draw_model(conduits=conduits, nodes=altmodel.nodes(), bbox=bbox,
                      title=self.name, annotation=files, file_path=pth)

        #EXISTING CONDITIONS PARCEL FLOOD DURATION
        pth = os.path.join(rpt_dir, '01 Existing Parcel Flood Duration.png')
        base_conduits = basemodel.conduits()
        base_conduits['draw_color'] = '#bebeb4' #default color
        base_conduits['draw_size'] = base_conduits.Geom1
        pars = self.baseline_report.parcel_flooding
        pars = pd.merge(pars, parcel_shp_df, right_on='PARCELID', left_index=True)
        comp_cols = pars.apply(lambda row: drawing.parcel_draw_color(row, 'risk'), axis=1)
        pars = pars.assign(draw_color=comp_cols)
        sg.draw_model(conduits=base_conduits, nodes=basemodel.nodes(), parcels=pars,
                      bbox=bbox,title=self.name, annotation=self.baseline_report.__str__(),
                      file_path=pth)

        #PROPOSED CONDITIONS PARCEL FLOOD DURATION
        pth = os.path.join(rpt_dir, '02 Proposed Parcel Flood Duration.png')
        pars = self.alt_report.parcel_flooding
        pars = pd.merge(pars, parcel_shp_df, right_on='PARCELID', left_index=True)
        comp_cols = pars.apply(lambda row: drawing.parcel_draw_color(row, 'risk'), axis=1)
        pars = pars.assign(draw_color=comp_cols)
        sg.draw_model(conduits=conduits, nodes=altmodel.nodes(), parcels=pars,
                      bbox=bbox,title=self.name, annotation=self.alt_report.__str__(),
                      file_path=pth)

        #IMPACT OF INFRASTRUCTURE
        pth = os.path.join(rpt_dir, '03 Impact of Option.png')
        pars = pd.merge(self.flood_comparison, parcel_shp_df, right_on='PARCELID', left_index=True)
        comp_cols = pars.apply(lambda row: drawing.parcel_draw_color(row, 'delta'), axis=1)
        pars = pars.assign(draw_color=comp_cols)
        annotation = self.alt_report.__str__() + '\n\n' + self.__str__()
        sg.draw_model(conduits=conduits, nodes=altmodel.nodes(), parcels=pars,
                      bbox=bbox,title=self.name, annotation=annotation,
                      file_path=pth)

        #IMPACT OF INFRASTRUCTURE OVERALL
        pth = os.path.join(rpt_dir, '04 Impact of Option - Overall.png')
        sg.draw_model(conduits=conduits, nodes=altmodel.nodes(), parcels=pars,
                      bbox=study_area,title=self.name, annotation=annotation,
                      file_path=pth)

    def __str__(self):
        """print friendly"""
        catz = [_f for _f in self.flood_comparison.Category.unique() if _f]
        a = ['{}: {}'.format(c, self.impact[c]) for c in catz]
        files = [self.baseline_report.model.inp.path,
                 self.alt_report.model.inp.path]
        return '{}\n{}'.format(self.name,'\n'.join(a+files))


def read_report_dir(rptdir, total_parcel_count=0):
    #rpt dir passed in, just read the preprossed report data
    rpt = FloodReport()
    rpt.total_parcel_count = total_parcel_count
    rpt.model = swmmio.Model(os.path.dirname(rptdir))
    rpt.scenario = rpt.model.scenario
    rpt.parcel_flooding = pd.read_csv(os.path.join(rptdir,
                                                   'parcel_flood_comparison.csv'))
    rpt.parcel_hrs_flooded = rpt.parcel_flooding.HoursFloodedProposed.sum()
    rpt.parcel_vol_flooded = rpt.parcel_flooding.TotalFloodVolProposed.sum()
    costcsv = os.path.join(rptdir, 'cost_estimate.csv')
    conduits_geojson_path = os.path.join(rptdir, 'new_conduits.json')

    if os.path.exists(costcsv):
        #calc the cost estimate total in millions
        cost_df =  pd.read_csv(costcsv)
        rpt.cost_estimate = cost_df.TotalCostEstimate.sum() / math.pow(10, 6)

    if os.path.exists(conduits_geojson_path):
        with open (conduits_geojson_path, 'r') as f:
            rpt.new_conduits_geojson = geojson.loads(f.read())

    return rpt
