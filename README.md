# SWMMIO

SWMMIO is a set of python tools aiming to provide efficient means for version control and visualizing results from the EPA Stormwater Management Model (SWMM). These tools are being developed specifically for the application of flood risk management.


### Prerequisites
SWMMIO functions primarily by interfacing with .inp and .rpt (input and report) files produced by SWMM. Functions within the `run_models` module rely on a SWMM5 engine which can be downloaded [here](https://www.epa.gov/water-research/storm-water-management-model-swmm). To optionally visualize basemap data, arcpy is required (which requires a license from [ESRI](http://www.esri.com/)).


### Dependencies
*  [pillow](http://python-pillow.org/): 3.0.0
*  [matplotlib](http://matplotlib.org/)
*  [numpy](http://www.numpy.org/)
*  [pandas](https://github.com/pydata/pandas)
*  [pyshp](https://github.com/GeospatialPython/pyshp)


### Installation:
Before installation, it's recommended to first activate a [virtualenv](https://github.com/pypa/virtualenv) to not crowd your system's package library. If you don't use any of the dependencies listed above, this step is less important. SWMMIO can be installed via pip in your command line:

```bash
#on Windows:
python -m pip install swmmio

#on Unix-type systems, i do this:
pip install swmmio
```

### Basic Usage
The `swmmio.Model()` class provides the basic endpoint for interfacing with SWMM models. To get started, save a SWMM5 model (.inp) in a directory with its report file (.rpt). A few examples:   
```python
from swmmio import swmmio

#instantiate a swmmio model object
mymodel = swmmio.Model('/path/to/directory with swmm files')

#export node data to a csv
mymodel.export_to_csv()

#access specific elements by element ID
mynode = mymodel.node('MY_NODE_ID')
print mynode.runoff_upstream_cf #accumulated runoff from upstream nodes
print mynode.drainage_area_upstream #accumulated drainage area from upstream nodes
```
Create an image (.png) visualization of the model. By default, pipe stress and node flood duration is visualized.
Many options can be passed to control how and what data is visualized.

```python
from swmmio.graphics import swmm_graphics as sg
sg.drawModel(mymodel)
```

Create an animated gif of a model's response to a storm. Again many options can be passed.
```
sg.animateModel(mymodel, startDtime='JAN-01-1990 11:59:00', endDtime='JAN-01-1990 12:01:00')
```

### SWMM Model Version Control  

TO BE CONTINUED... 

### Acknowledgments
For use in generating animations of SWMM models, thanks to [images2gif.py](https://gist.github.com/jonschoning/7216290)
