# SWMMIO

SWMMIO is a set of python tools aiming to provide efficient means for version control and visualizing results from the EPA Stormwater Management Model (SWMM). Command line tools are also provided for running models individually and in parallel via Python's `multiprocessing` module. These tools are being developed specifically for the application of flood risk management, though most functionality is applicable to SWMM modeling in general.


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

#Pandas dataframe with most useful data related to model nodes, conduits
nodes_df = mymodel.nodes()
conduits_df = mymodel.conduits()


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
![Kool Pic](docs/img/impact_of_option.png?raw=true "Impact of Option")
```

Create an animated gif of a model's response to a storm. Again many options can be passed.
```python
sg.animateModel(mymodel, startDtime='JAN-01-1990 11:59:00', endDtime='JAN-01-1990 12:01:00')
```

### Running Models
Using the command line tool, individual SWMM5 models can be run by invoking the swmmio module in your shell as such:
```
$ python -m swmmio --run path/to/mymodel.inp
```
If you have many models to run and would like to take advantage of your machine's cores, you can start a pool of simulations with the `--start_pool` (or `-sp`) command. After pointing `-sp` to one or more directories, swmmio will search for SWMM .inp files and add all them to a multiprocessing pool. By default, `-sp` leaves 4 of your machine's cores unused. This can be changed via the `-cores_left` argument.
```
$ #run all models in models in directories Model_Dir1 Model_Dir2
$ python -m swmmio -sp Model_Dir1 Model_Dir2  

$ #leave 1 core unused
$ python -m swmmio -sp Model_Dir1 Model_Dir2  -cores_left=1
```
<div class="warning">
    <p class="first admonition-title">Warning</p>
    <p class="last">Using all cores for simultaneous model runs can put your machine's CPU usage at 100% for extended periods of time. This probably puts stress on your hardware. Use at your own risk.</p>
</div>



### Flood Model Options Generation
swmmio can take a set of independent storm flood relief (SFR) alternatives and combine them into every combination of potential infrastructure changes. This lays the ground work for identifying the most-efficient implementation sequence and investment level.

Consider the simplified situaiton where a city is interested in solving a flooding issue by installing new relief sewers along Street A and/or Street B. Further, the city wants to decide whether they should be 1 or 2 blocks long. Engineers then decide to build SWMM models for 4 potential relief sewer options:
*  A1 -> One block of relief sewer on Street A
*  A2 -> Two blocks of relief sewer on Street A
*  B1 -> One block of relief sewer on Street B
*  B2 -> Two blocks of relief sewer on Street B

To be comprehensive, implementation scenarios should be modeled for combinations of these options; it may be more cost-effective, for example, to build releif sewers on one block of Street A and Street B in combination, rather than two blocks on either street independently.

swmmio aciheves this within the version_control module. The `create_combinations()` function builds models for every logical combinations of the segmented flood mitigation models. In the example above, models for the following scenarios will be created:
*  A1 with B1
*  A1 with B2
*  A2 with B1
*  A2 with B2

For the `create_combinations()` function to work, the model directory needs to be set up as follows:
```
├───Baseline
        baseline.inp
├───Combinations
└───Segments
    ├───A
    │   ├───A1
    │   │   A1.inp
    │   └───A2
    │       A2.inp
    └───B
        ├───B1
        │   B1.inp
        └───B2
            B2.inp
```
The new models will be built and saved within the Combinations directory. `create_combinations()` needs to know where these directories are and optionally takes version_id and comments data:

```python
#load the version_control module
from swmmio.version_control import version_control as vc

#organize the folder structure
baseline_dir = r'path/to/Baseline/'
segments_dir = r'path/to/Segments/'
target_dir = r'path/to/Combinations/'

#generate flood mitigation options
vc.create_combinations(
    baseline_dir,
    segments_dir,
    target_dir,
    version_id='initial',
    comments='example flood model generation comments')
```

The new models will be saved in subdirectories within the `target_dir`. New models (and their containing directory) will be named based on a concatenation of their parent models' names. It is recommended to keep parent model names as concise as possible such that child model names are manageable. After running `create_combinations()`, your project directory will look like this:
```
├───Baseline
├───Combinations
│   ├───A1_B1
│   ├───A1_B2
│   ├───A2_B1
│   └───A2_B2
└───Segments
    ├───A
    │   ├───A1
    │   └───A2
    └───B
        ├───B1
        └───B2

```

### SWMM Model Version Control
To add more segments to the model space, create a new segment directory and rerun the `create_combinations()` function. Optionally include a comment summarizing how the model space is changing:
```python
vc.create_combinations(
    baseline_dir,
    alternatives_dir,
    target_dir,
    version_id='addA3',
    comments='added model A3 to the scope')
```
The `create_combinations()` function can also be used to in the same way to propogate a change in an existing segment (parent) model to all of the children. Version information for each model is stored within a subdirectory called `vc` within each model directory. Each time a model is modified from the `create_combinations()` function, a new "BuildInstructions" file is generated summarizing the changes. BuildInstructions files outline how to recreate the model with respect to the baseline model.


TO BE CONTINUED...

### Acknowledgments
For use in generating animations of SWMM models, thanks to [images2gif.py](https://gist.github.com/jonschoning/7216290)
