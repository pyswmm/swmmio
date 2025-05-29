# swmmio
*v0.8.1 (2025/05/29)*

_Programmatic pre and post processing for EPA Stormwater Management Model (SWMM)_


![workflow status](https://github.com/aerispaha/swmmio/actions/workflows/python-app.yml/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/swmmio/badge/?version=latest)](https://swmmio.readthedocs.io/en/latest/?badge=latest)


![image](docs/_static/img/flooded_anno_example.png)


## Introduction
`swmmio` is a Python tool for engineers and hydrologists who need to supercharge their ability to modify and analyze EPA SWMM models and results. Using a familiar Pandas interface, users can replace manual procesess that used to live in spreadsheets with scripts and automation.

The core `swmmio.Model` object provides accessors to related elements in the INP and RPT. For example, `swmmio.Model.subcatchments` provides a DataFrame (or GeoDataFrame) joining data from the `[SUBCATCHMENTS]` and `[SUBAREAS]` tables in the model.inp file and, if available, the `Subcatchment Runoff Summary` from the model.rpt file. 

Additionally, `swmmio` provides a lower-level API for reading and writing (almost) all of the sections of the model.inp file which is useful for programmatically modifying EPA SWMM models.


## Installation
```bash
pip install swmmio
``` 

For documentation and tutorials, see our [documentation](https://swmmio.readthedocs.io/). 