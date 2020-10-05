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
