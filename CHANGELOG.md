## Version 0.8.0 (2025/01/05)

### What's Changed
* Overhaul of the documentation that better organizes the API reference documentation, adds a User Guide with examples (including some silly examples), and provides a more concise introduction [PR235](https://github.com/pyswmm/swmmio/pull/235)
* Added ability to instantiate a swmmio.Model object with a url to a INP file somewhere on the network
* Upgrades and loosens the pyshp dependency in requiements.txt and setup.py, respectively. [PR236](https://github.com/pyswmm/swmmio/pull/236)

## Version 0.7.3 (2024/12/02)

### What's Changed
* Added coverage for the [OUTLETS] INP section. Now we can get a dataframe of the OUTLETS section in models with model.inp.outlets. The higher level API now also include outlets in the model.links accessor. [PR229](https://github.com/pyswmm/swmmio/pull/229)
* handled all future warnings from Pandas and a few warnings from pytest [PR230](https://github.com/pyswmm/swmmio/pull/230)
* Revised setup.py to allow networkx>3, provided by @barneydobson [PR232](https://github.com/pyswmm/swmmio/pull/232)

## Version 0.7.2 (2024/11/27)

### What's Changed
* Handle several Pandas FutureWarnings, provided by @dirwin5 [PR224](https://github.com/pyswmm/swmmio/pull/224)
* Fix docs build process and update docs layout and theme [PR220](https://github.com/pyswmm/swmmio/pull/220)
* Fixed typos in the README [226](https://github.com/pyswmm/swmmio/pull/226)


## Version 0.7.1 (2024/08/19)

### What's Changed
* Handle depreciated delim_whitespace warnings, provided by @bowguy [PR222](https://github.com/pyswmm/swmmio/pull/222)


## Version 0.7.0 (2024/04/21)

### What's Changed
* Added inp coverage for CONTROLS and PATTERNS, provided by @kaklise [PR219](https://github.com/pyswmm/swmmio/pull/219)
* Made progress on [#57](https://github.com/aerispaha/swmmio/issues/57), read/write interface to all INP sections 
* PR [#218](https://github.com/pyswmm/swmmio/pull/218) bump pillow version from 10.2.0 to 10.3.0
* PR [#216](https://github.com/pyswmm/swmmio/pull/216) bump pillow version from 10.2.0 to 10.3.0

## Version 0.6.11 (2023/12/07)

### What's Changed
* PR [#213](https://github.com/pyswmm/swmmio/pull/213) bump pillow version, drop Python 3.7 support, add 3.11 support

## Version 0.6.10 (2023/11/22)

### What's Changed
* PR [#154](https://github.com/pyswmm/swmmio/pull/154) Added model summary property and RPT warning function, by @everettsp
* Fixed [#210](https://github.com/pyswmm/swmmio/issues/210) causing readthedocs builds to fail.

## Version 0.6.9 (2023/10/19)

### What's Changed
* Fixed [#204](https://github.com/pyswmm/swmmio/issues/204) causing negative offset elevations to be handled incorrectly in profile plot.

## Version 0.6.8 (2023/09/28)

### What's Changed
* fixed that written polygon shapefile may be not correctly loaded in ArcGIS [#205](https://github.com/pyswmm/swmmio/pull/205)

## Version 0.6.7 (2023/05/19)

### What's Changed
* draw_model should include all links, not just conduits [#196](https://github.com/pyswmm/swmmio/pull/196)
* include all links in draw_model, optionally return html in create_map [#197](https://github.com/pyswmm/swmmio/pull/197)

## Version 0.6.6 (2023/05/15)

### What's Changed
* Added inp coverage for LID_USAGE, provided by @asselapathirana [PR193](https://github.com/pyswmm/swmmio/pull/193)
* Made progress on [#57](https://github.com/aerispaha/swmmio/issues/57), read/write interface to all INP sections
* updated AUTHORS, fixed issue causing not all contributors included in AUTHORS file [#190](https://github.com/pyswmm/swmmio/issues/190), read/write interface to all INP sections

## Version 0.6.5 (2023/05/02)

### What's Changed
* Added inp coverage for DIVIDERS, LOSSES, AQUIFERS, and GROUNDWATER [PR192](https://github.com/aerispaha/swmmio/pull/192)
* Made progress on [#57](https://github.com/aerispaha/swmmio/issues/57), read/write interface to all INP sections

## Version 0.6.4 (2023/04/28)

### What's Changed
* Added coverage for STREETS, INLETS, and INLET_USAGE in [PR186](https://github.com/aerispaha/swmmio/pull/186)
* Made progress on [#57](https://github.com/aerispaha/swmmio/issues/57), read/write interface to all INP sections 
* added AUTHORS, provided by @bemmcdonnel and @aerispaha in [PR183](https://github.com/aerispaha/swmmio/pull/183)

## Version 0.6.3 (2023/04/26)

### What's Changed
* Added coverage for TAGS, provided by @BuczynskiRafal in [PR186](https://github.com/aerispaha/swmmio/pull/186)
* Code simplification in Model.conduits [PR189](https://github.com/aerispaha/swmmio/pull/189)

## Version 0.6.2 (2023/02/02)

### What's Changed
* Profile wrapup by @bemcdonnell in https://github.com/aerispaha/swmmio/pull/173
* minor tweaks for pep8 code style enforcement by @aerispaha in https://github.com/aerispaha/swmmio/pull/178
* drop appveyor and release with GitHub Actions by @aerispaha in https://github.com/aerispaha/swmmio/pull/179
* write_inp_section changes - don't change the Polygons header by @BuczynskiRafal in https://github.com/aerispaha/swmmio/pull/182

## New Contributors
* @BuczynskiRafal made their first contribution in https://github.com/aerispaha/swmmio/pull/182

**Full Changelog**: https://github.com/aerispaha/swmmio/compare/v0.6.0...v0.6.2

## Version 0.6.1 (2023/01/05)

### Issues Closed

* [Issue 175](https://github.com/aerispaha/swmmio/issues/175) - Drop Appveyor, leverage GitHub Actions for deploy logic
* [Issue 172](https://github.com/aerispaha/swmmio/issues/172) - Improvements to Profile Plotter feature

In this release 2 issues were closed, 2 PRs were merged.

## Version 0.6.0 (2022/12/29)

### Issues Closed

* [Issue 75](https://github.com/aerispaha/swmmio/issues/75) - Update and unit test the run_models module
* [Issue 153](https://github.com/aerispaha/swmmio/issues/153) - Add Profile Plotter
* [PR 165](https://github.com/aerispaha/swmmio/pull/165) - Add profile plotter and pyswmm integration
* [PR 170](https://github.com/aerispaha/swmmio/pull/170) - Add INP sections to model.inp properties
  * raingages 
  * evaporation 
  * pollutants 
  * rdii 
  * hydrographs 
  * buildup 
  * washoff 
  * coverages 
  * loadings 
  * landuses

In this release 2 issues were closed, 2 PRs were merged, and a lot of progress was 
made on [Issue 57](https://github.com/aerispaha/swmmio/issues/57). 


## Version 0.5.3 (2022/12/21)

### Issues Closed

* [Issue 162](https://github.com/aerispaha/swmmio/issues/162) - fix version number in readthedocs title

In this release 1 issues was closed.

## Version 0.5.2 (2022/12/20)

### Issues Closed

* [Issue 159](https://github.com/aerispaha/swmmio/issues/159) - Drop travis CI from the build pipeline
* [Issue 157](https://github.com/aerispaha/swmmio/issues/157) - Configure GitHub Actions test matrix
* [Issue 141](https://github.com/aerispaha/swmmio/issues/141) - model.inp.headers gives "UnboundLocalError: local variable 'h' referenced before assignment"
* Include core.py doctests in GitHub Actions and Appveyor build tests

In this release 3 issues were closed.

## Version 0.5.1 (2022/12/08)

### Issues Closed

* [Issue 151](https://github.com/aerispaha/swmmio/issues/151) - Model.nodes.geojson coordinates are improperly structured

In this release 1 issues were closed.

## Version 0.5.0 (2022/12/08)

### Issues Closed

* [Issue 150](https://github.com/aerispaha/swmmio/issues/150) - add DWF to inp module
* [Issue 148](https://github.com/aerispaha/swmmio/issues/148) - pyproj>=3.0.0 needed in setup.py
* Update test environment to Python 3.8

In this release 2 issues were closed.

## Version 0.4.13 (2022/12/07)

### Issues Closed

* [Issue 108](https://github.com/aerispaha/swmmio/issues/108) - rpt.node_flooding_summary fails when no nodes are flooded
* [Issue 146](https://github.com/aerispaha/swmmio/issues/146) - add optional custom basemap to create_map function

In this release 2 issues were closed.

## Version 0.4.12 (2022/12/05)

### Issues Closed

* [Issue 142](https://github.com/aerispaha/swmmio/issues/142) - fails to parse RPT when generated with Open Water Analytics SWMM

In this release 1 issues were closed.

## Version 0.4.11 (2022/12/04)

### Issues Closed

* [Issue 134](https://github.com/aerispaha/swmmio/issues/134) - update export_to_shapefile to handle changes to pyshp API

In this release 1 issues were closed.


## Version 0.4.10 (2022/09/22)

### Issues Closed

* [Issue 130](https://github.com/aerispaha/swmmio/issues/130) - model.inp.infiltration yielding IndexError: list index out of range
* [Issue 131](https://github.com/aerispaha/swmmio/issues/131) - KeyError 'Horton' while extracting data
* [Issue 132](https://github.com/aerispaha/swmmio/issue/132) - Weir Dataframe Problem

In this release 3 issues were closed.

## Version 0.4.9 (2022/02/22)

### Issues Closed

* [Issue 128](https://github.com/aerispaha/swmmio/issues/128) - Docs build fails due to m2r dependency
* [PR 127](https://github.com/aerispaha/swmmio/pull/127) - Define max_columns option as a display option
* [PR 117](https://github.com/aerispaha/swmmio/pull/117) - Speeding up lookup of inp sections and bracketed words

In this release 3 issues was closed.

## Version 0.4.8 (2021/05/05)

### Issues Closed

#### Bugs fixed

* [Issue 121](https://github.com/aerispaha/swmmio/issues/121) - Errors when overwrite the [OPTIONS] Sections

In this release 1 issue was closed.

## Version 0.4.7 (2021/01/06)

### Issues Closed

#### Bugs fixed

* [Issue 118](https://github.com/aerispaha/swmmio/issues/118) - pyproj.transform is depreciated 
* [Issue 111](https://github.com/aerispaha/swmmio/issues/111) - Setter property mismatch

In this release 2 issues were closed.

### Pull Requests Merged

* [PR 113](https://github.com/aerispaha/swmmio/pull/113) - Read/write timeseries section of inp, by [@jackieff](https://github.com/jackieff)
* [PR 112](https://github.com/aerispaha/swmmio/pull/112) - Fixing setter references, by [@jackieff](https://github.com/jackieff)

In this release 2 pull requests were closed.


## Version 0.4.6 (2020/10/05)

### Issues Closed

#### Bugs fixed

* [Issue 106](https://github.com/aerispaha/swmmio/issues/106) - model.subcatchments fails to merge rpt data when subcatchments have numeric names

In this release 1 issue was closed.


## Version 0.4.5 (2020/09/28)

### Issues Closed

#### Bugs fixed

* [Issue 103](https://github.com/aerispaha/swmmio/issues/103) - coords column is not updated in subcatchment dataframe in ModelSection object when index is integer instead of string ([PR 105](https://github.com/aerispaha/swmmio/pull/105))
* [Issue 102](https://github.com/aerispaha/swmmio/issues/102) - IndexError when parsing certain .rpt files ([PR 105](https://github.com/aerispaha/swmmio/pull/105))

In this release 2 issues were closed.

### Pull Requests Merged

* [PR 105](https://github.com/aerispaha/swmmio/pull/105) - Address issue #103 and #102 ([103](https://github.com/aerispaha/swmmio/issues/103), [102](https://github.com/aerispaha/swmmio/issues/102))

In this release 1 pull request was closed.


## Version 0.4.4 (2020/06/02)

### Issues Closed

#### Bugs fixed

* [Issue 100](https://github.com/aerispaha/swmmio/issues/100) - ModelSection fails when a section has all numeric element IDs

In this release 1 issue was closed.

## Version 0.4.3 (2020/05/14)

### Issues Closed

#### Enhancements

* [Issue 93](https://github.com/aerispaha/swmmio/issues/93) - dataframe_from_rpt fails if more than one element is provided in the section

#### Bugs fixed

* [Issue 94](https://github.com/aerispaha/swmmio/issues/94) - remove obsolete swmmio.graphics.animate module

In this release 2 issues were closed.

## Version 0.4.2 (2020/05/06)

### Issues Closed

#### Bugs fixed

* [Issue 90](https://github.com/aerispaha/swmmio/issues/90) - changing an inp section removes all subsequent sections during model.inp.save()
* [Issue 87](https://github.com/aerispaha/swmmio/issues/87) - Model.subcacthments() fails in models with no subcatchments

In this release 2 issues were closed.

## Version 0.4.1 (2020/05/05)

### Issues Closed

#### Enhancements

* [Issue 85](https://github.com/aerispaha/swmmio/issues/85) - provide access to model.subcatchments.geojson

#### Bugs fixed

* [Issue 82](https://github.com/aerispaha/swmmio/issues/82) - "vc_dir" artifact lingers after some unit tests
* [Issue 81](https://github.com/aerispaha/swmmio/issues/81) - FileNotFoundError: [Errno 2] inp_sections.yml

In this release 3 issues were closed.


## Version 0.4.0 (2020/04/29)

### Issues Closed

#### Enhancements

* [Issue 77](https://github.com/aerispaha/swmmio/issues/77) - add node inflow report into nodes dataframe
* [Issue 65](https://github.com/aerispaha/swmmio/issues/65) - Add auto release logic to appveyor.yml
* [Issue 50](https://github.com/aerispaha/swmmio/issues/50) - Support for adding/joining models 
* [Issue 38](https://github.com/aerispaha/swmmio/issues/38) - Add readthedocs  ([PR 42](https://github.com/aerispaha/swmmio/pull/42))
* [Issue 36](https://github.com/aerispaha/swmmio/issues/36) - Optionally specify which attributes to return in model.conduits() ?
* [Issue 31](https://github.com/aerispaha/swmmio/issues/31) - Return GeoJSON representation of Model
* [Issue 18](https://github.com/aerispaha/swmmio/issues/18) - considered using GeoPandas for spatial functions?

#### Bugs fixed

* [Issue 64](https://github.com/aerispaha/swmmio/issues/64) - Pandas 0.25.x drops support for Python 2.7
* [Issue 61](https://github.com/aerispaha/swmmio/issues/61) - error "no module named swmmio" ([PR 63](https://github.com/aerispaha/swmmio/pull/63))
* [Issue 59](https://github.com/aerispaha/swmmio/issues/59) - parsing fails when TITLE section has commas
* [Issue 45](https://github.com/aerispaha/swmmio/issues/45) - future warning from pandas 

In this release 11 issues were closed.

### Pull Requests Merged

* [PR 63](https://github.com/aerispaha/swmmio/pull/63) - Update __main__.py ([61](https://github.com/aerispaha/swmmio/issues/61))
* [PR 42](https://github.com/aerispaha/swmmio/pull/42) - Adds basic readthedocs configuration ([38](https://github.com/aerispaha/swmmio/issues/38))

In this release 2 pull requests were closed.

## Version 0.3.7 (2019/10/25)

### Issues Closed

#### Bugs fixed

* [Issue 74](https://github.com/aerispaha/swmmio/issues/74) - drop support of Python 2.7  ([PR 73](https://github.com/aerispaha/swmmio/pull/73))
* [Issue 72](https://github.com/aerispaha/swmmio/issues/72) - update pillow dependency ([PR 73](https://github.com/aerispaha/swmmio/pull/73))
* [Issue 71](https://github.com/aerispaha/swmmio/issues/71) - require networkx >2.4  ([PR 73](https://github.com/aerispaha/swmmio/pull/73))

In this release 3 issues were closed.

### Pull Requests Merged

* [PR 73](https://github.com/aerispaha/swmmio/pull/73) - Update networkx, autorelease to PyPi ([74](https://github.com/aerispaha/swmmio/issues/74), [72](https://github.com/aerispaha/swmmio/issues/72), [71](https://github.com/aerispaha/swmmio/issues/71))

In this release 1 pull request was closed.

## Version 0.3.6 (2019/06/19)

### Issues Closed

#### Completed

* [Issue 24](https://github.com/aerispaha/swmmio/issues/24) - Assumed column data-type of elements with all numeric values causes conflicts ([PR 56](https://github.com/aerispaha/swmmio/pull/56))
* [Issue 16](https://github.com/aerispaha/swmmio/issues/16) - problem with ImageFont.py ([PR 54](https://github.com/aerispaha/swmmio/pull/54))
* [Issue 9](https://github.com/aerispaha/swmmio/issues/9) - options in swmmio.graphics ([PR 54](https://github.com/aerispaha/swmmio/pull/54))
* [Issue 8](https://github.com/aerispaha/swmmio/issues/8) - version_control module fails in directories with spaces in the path ([PR 56](https://github.com/aerispaha/swmmio/pull/56))

#### Enhancements

* [Issue 53](https://github.com/aerispaha/swmmio/issues/53) - include test models in package distribution
* [Issue 47](https://github.com/aerispaha/swmmio/issues/47) - Set and reproject a model's coordinate reference system ([PR 48](https://github.com/aerispaha/swmmio/pull/48))
* [Issue 44](https://github.com/aerispaha/swmmio/issues/44) - Alleviate Pandas .ix indexing depreciation warning ([PR 48](https://github.com/aerispaha/swmmio/pull/48))
* [Issue 12](https://github.com/aerispaha/swmmio/issues/12) - Standardize the organization of the main and submodules ([PR 48](https://github.com/aerispaha/swmmio/pull/48))
* [Issue 9](https://github.com/aerispaha/swmmio/issues/9) - options in swmmio.graphics ([PR 54](https://github.com/aerispaha/swmmio/pull/54))

#### Bugs fixed

* [Issue 51](https://github.com/aerispaha/swmmio/issues/51) - invalid import in swmmio.utils.modify_model
* [Issue 49](https://github.com/aerispaha/swmmio/issues/49) - Some coordinates are being rounded
* [Issue 24](https://github.com/aerispaha/swmmio/issues/24) - Assumed column data-type of elements with all numeric values causes conflicts ([PR 56](https://github.com/aerispaha/swmmio/pull/56))
* [Issue 16](https://github.com/aerispaha/swmmio/issues/16) - problem with ImageFont.py ([PR 54](https://github.com/aerispaha/swmmio/pull/54))
* [Issue 8](https://github.com/aerispaha/swmmio/issues/8) - version_control module fails in directories with spaces in the path ([PR 56](https://github.com/aerispaha/swmmio/pull/56))

In this release 14 issues were closed.

### Pull Requests Merged

* [PR 56](https://github.com/aerispaha/swmmio/pull/56) - Refactoring graphics, build instructions tests and bug fix ([9](https://github.com/aerispaha/swmmio/issues/9), [8](https://github.com/aerispaha/swmmio/issues/8), [24](https://github.com/aerispaha/swmmio/issues/24), [16](https://github.com/aerispaha/swmmio/issues/16))
* [PR 54](https://github.com/aerispaha/swmmio/pull/54) - Refactoring swmmio graphics ([9](https://github.com/aerispaha/swmmio/issues/9), [16](https://github.com/aerispaha/swmmio/issues/16))
* [PR 48](https://github.com/aerispaha/swmmio/pull/48) - Improved import pattern, coordinate ref system support ([47](https://github.com/aerispaha/swmmio/issues/47), [45](https://github.com/aerispaha/swmmio/issues/45), [45](https://github.com/aerispaha/swmmio/issues/45), [44](https://github.com/aerispaha/swmmio/issues/44), [12](https://github.com/aerispaha/swmmio/issues/12))

In this release 3 pull requests were closed.
