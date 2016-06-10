#=================
#DEFINE INP HEADER TEST THAT SHOULD BE REPLACED
#=================


inp_header_dict = {
    '[TITLE]':'blob',
    '[OPTIONS]':'Name Value',
    '[CONDUITS]': 'Name InletNode OutletNode Length ManningN InletOffset OutletOffset InitFlow MaxFlow',
    '[COORDINATES]': 'Name X Y',
    '[JUNCTIONS]': 'Name InvertElev MaxDepth InitDepth SurchargeDepth PondedArea',
    '[ORIFICES]': 'Name InletNode OutletNode OrificeType CrestHeight DischCoeff FlapGate OpenCloseTime',
    '[OUTFALLS]': 'Name InvertElev OutfallType Timeseries TideGate',
    '[STORAGE]': 'Name InvertElev MaxD InitDepth StorageCurve Coefficient Exponent Constant PondedArea EvapFrac SuctionHead Conductivity InitialDeficit',
    '[VERTICES]': 'Name X Y',
    '[WEIRS]': 'Name InletNode OutletNode WeirType CrestHeight DischCoeff FlapGate EndCon EndCoeff',
    '[PUMPS]':'Name',
    '[XSECTIONS]':'Link Shape Geom1 Geom2 Geom3 Geom4 Barrels',
    '[Polygons]':'Name X-Coord Y-Coord',
    '[SUBCATCHMENTS]':'Name Raingage Outlet Area PercImperv Width PercSlope CurbLength SnowPack',
    '[SUBAREAS]':'Name N-Imperv N-Perv S-Imperv S-Perv PctZero RouteTo PctRouted',
    '[LOSSES]':'Link Inlet Outlet Average FlapGate',
    '[PUMPS]':'Name InletNode OutletNode PumpCurve InitStatus Depth ShutoffDepth',
    '[DWF]':'Node Parameter AverageValue TimePatterns',
    '[CURVES]':'Name Type X Y',
    '[RAINGAGES]':'Name RainType TimeIntrv SnowCatch DataSource'
}

junctionsOld = """[JUNCTIONS]
;;               Invert     Max.       Init.      Surcharge  Ponded
;;Name           Elev.      Depth      Depth      Depth      Area
;;-------------- ---------- ---------- ---------- ---------- ----------"""
junctionsNew = "Name InvertElev MaxDepth InitDepth SurchargeDepth PondedArea"

conduitsOld = """[CONDUITS]
;;               Inlet            Outlet                      Manning    Inlet      Outlet     Init.      Max.
;;Name           Node             Node             Length     N          Offset     Offset     Flow       Flow
;;-------------- ---------------- ---------------- ---------- ---------- ---------- ---------- ---------- ----------"""
conduitsNew = "Name InletNode OutletNode Length ManningN InletOffset OutletOffset InitFlow MaxFlow"

orificesOld = """[ORIFICES]
;;               Inlet            Outlet           Orifice      Crest      Disch.     Flap Open/Close
;;Name           Node             Node             Type         Height     Coeff.     Gate Time
;;-------------- ---------------- ---------------- ------------ ---------- ---------- ---- ----------"""
orificesNew = "Name InletNode OutletNode OrificeType CrestHeight DischCoeff FlapGate OpenCloseTime"

weirsOld = """[WEIRS]
;;               Inlet            Outlet           Weir         Crest      Disch.     Flap End      End
;;Name           Node             Node             Type         Height     Coeff.     Gate Con.     Coeff.
;;-------------- ---------------- ---------------- ------------ ---------- ---------- ---- -------- ----------"""
weirsNew = "Name InletNode OutletNode WeirType CrestHeight DischCoeff FlapGate EndCon EndCoeff"

coordinatesOld = """[COORDINATES]
;;Node           X-Coord            Y-Coord
;;-------------- ------------------ ------------------"""
coordinatesNew = "Name X Y"

verticiesOld = """[VERTICES]
;;Link           X-Coord            Y-Coord
;;-------------- ------------------ ------------------"""
verticiesNew = "Name X Y"

profilesOld = """[PROFILES]
;;Name           Links
;;-------------- ----------"""
profilesNew= "Name Links"

outfallsOld = """[OUTFALLS]
;;               Invert     Outfall    Stage/Table      Tide
;;Name           Elev.      Type       Time Series      Gate
;;-------------- ---------- ---------- ---------------- ----"""
outfallsNew = "Name InvertElev OutfallType Timeseries TideGate"

storageOld = """[STORAGE]
;;               Invert   Max.     Init.    Storage    Curve                      Ponded   Evap.
;;Name           Elev.    Depth    Depth    Curve      Params                     Area     Frac.    Infiltration Parameters
;;-------------- -------- -------- -------- ---------- -------- -------- -------- -------- -------- -----------------------"""
storageNew = "Name InvertElev MaxD InitDepth StorageCurve Coefficient Exponent Constant PondedArea EvapFrac SuctionHead Conductivity InitialDeficit"

inpHeaderList = [

	[junctionsOld, junctionsNew],
	[conduitsOld, conduitsNew],
	[orificesOld, orificesNew],
	[weirsOld, weirsNew],
	[coordinatesOld, coordinatesNew],
	[verticiesOld, verticiesNew],
	[outfallsOld, outfallsNew],
	[storageOld, storageNew]

]
def complete_inp_headers (inp):

    #create a dictionary with all the headers found in an INP file
    #and updates them based on the definitions in inp_header_dict
    #this ensure the list is comprehensive

    foundheaders= {}
    order = []
    #print inp_header_dict
    with open(inp.filePath) as f:
        for line in f:
            if '[' and ']' in line:
                h = line.strip()
                order.append(h)
                if h in inp_header_dict:
                    foundheaders.update({h:inp_header_dict[h]})
                else:
                    foundheaders.update({h:'blob'})


    #isolate which headers we have more data for, then update the found headers
    #this step prevents loopingthrough and searching for a defined inp_header_dict
    #thats not in the INP
    #updaters = {k:v for k,v in inp_header_dict.items() if k in foundheaders}
    #[d for d in foundheaders]
    #d = foundheaders.update(inp_header_dict)
    #foundheaders.update(updaters)
    #d = foundunmtchrs.update(foundmatchers)

    return {'headers':foundheaders, 'order':order}
#=================
#DEFINE RPT HEADER TEST THAT SHOULD BE REPLACED
#=================

subcatSummOld = """Subcatchment Summary
  ********************
  Name                      Area     Width   %Imperv    %Slope    Rain Gage            Outlet
  -------------------------------------------------------------------------------------------------------"""
subcatSumNew = "Name Area Width ImpervPerc SlopePerc RainGage Outlet"

nodeSummOld = """Node Summary
  ************
                                          Invert      Max.    Ponded    External
  Name                Type                 Elev.     Depth      Area    Inflow
  ------------------------------------------------------------------------------"""
nodeSummNew = "Name Type InvertEl MaxD PondedA ExternalInf"

linkSummOld = """Link Summary
  ************
  Name            From Node       To Node         Type            Length    %Slope Roughness
  ------------------------------------------------------------------------------------------"""
linkSummNew = "Name FromNode ToNode Type Length SlopePerc Roughness"

xSectionSummOld = """Cross Section Summary
  *********************
                                        Full     Full     Hyd.     Max.   No. of     Full
  Conduit          Shape               Depth     Area     Rad.    Width  Barrels     Flow
  ---------------------------------------------------------------------------------------"""
xSectionSummNew = "Name Shape DFull AreaFull HydRad MaxW NumBarrels FullFlow"

subcatRunoffSummOld = """Subcatchment Runoff Summary
  ***************************

  --------------------------------------------------------------------------------------------------------
                            Total      Total      Total      Total      Total       Total     Peak  Runoff
                           Precip      Runon       Evap      Infil     Runoff      Runoff   Runoff   Coeff
  Subcatchment                 in         in         in         in         in    10^6 gal      CFS
  --------------------------------------------------------------------------------------------------------"""
subcatRunoffSummNew = "Name TotalPrecip TotalRunon TotalEvap TotalInfil TotalRunoffIn TotalRunoffMG PeakRunoff RunoffCoeff"

nodeFloodingSummaryOld = """Node Flooding Summary
  *********************

  Flooding refers to all water that overflows a node, whether it ponds or not.
  --------------------------------------------------------------------------
                                                             Total   Maximum
                                 Maximum   Time of Max       Flood    Ponded
                        Hours       Rate    Occurrence      Volume     Depth
  Node                 Flooded       CFS   days hr:min    10^6 gal      Feet
  --------------------------------------------------------------------------"""
nodeFloodingSummaryNew = "Name HoursFlooded MaxQ MaxDay MaxHr TotalFloodVol MaximumPondDepth"

nodeInflowSummaryOld = """Node Inflow Summary
  *******************

  -------------------------------------------------------------------------------------
                                  Maximum  Maximum                  Lateral       Total
                                  Lateral    Total  Time of Max      Inflow      Inflow
                                   Inflow   Inflow   Occurrence      Volume      Volume
  Node                 Type           CFS      CFS  days hr:min    10^6 gal    10^6 gal
  -------------------------------------------------------------------------------------"""
nodeInflowSummaryNew = "Name Type MaxLatInflow MaxTotalInflow MaxDay MaxHr LatInflowV TotalInflowV"

nodeSurchargeSummaryOld = """Node Surcharge Summary
  **********************

  Surcharging occurs when water rises above the top of the highest conduit.
  ---------------------------------------------------------------------
                                               Max. Height   Min. Depth
                                   Hours       Above Crown    Below Rim
  Node                 Type      Surcharged           Feet         Feet
  ---------------------------------------------------------------------"""
nodeSurchargeSummaryNew = "Name Type Hours MaxH MinD"

nodeDepthSummaryOld = """Node Depth Summary
  ******************

  ---------------------------------------------------------------------
                                 Average  Maximum  Maximum  Time of Max
                                   Depth    Depth      HGL   Occurrence
  Node                 Type         Feet     Feet     Feet  days hr:min
  ---------------------------------------------------------------------"""
nodeDepthSummaryNew = "Name Type AvgDepth MaxNodeDepth MaxHGL MaxDay MaxHr"

linkFlowSummaryOld = """Link Flow Summary
  ********************

  -----------------------------------------------------------------------------
                                 Maximum  Time of Max   Maximum    Max/    Max/
                                  |Flow|   Occurrence   |Veloc|    Full    Full
  Link                 Type          CFS  days hr:min    ft/sec    Flow   Depth
  -----------------------------------------------------------------------------"""
linkFlowSummaryNew = 	"Name Type MaxQ MaxDay MaxHr MaxV MaxQPerc MaxDPerc"

rptHeaderList = [
	[subcatSummOld, subcatSumNew],
	[nodeSummOld, nodeSummNew],
	[linkSummOld, linkSummNew],
	[xSectionSummOld, xSectionSummNew],
	[subcatRunoffSummOld, subcatRunoffSummNew],
	[nodeFloodingSummaryOld, nodeFloodingSummaryNew],
	[nodeInflowSummaryOld, nodeInflowSummaryNew],
	[nodeSurchargeSummaryOld, nodeSurchargeSummaryNew],
	[nodeDepthSummaryOld, nodeDepthSummaryNew],
	[linkFlowSummaryOld, linkFlowSummaryNew]
]
