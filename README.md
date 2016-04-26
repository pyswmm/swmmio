#SWMMIO

SWMMIO is a set of python tools for interacting with and visualizing results from EPA Stomwater Management Model input and output files (.inp and .rpt). These tools are being developed specifically for the application of flood risk management.


### Prerequisities
SWMMIO functions by processing .inp and .rpt (input and report) files produced by EPA SWMM5. In order for these tools for work properly, an associated pair of .inp and .rpt files should be located within the same directory. SWMMIO (I think) relies only on pre-installed Python 2.7 libraries. Images2Gif was copied within this project and one line was edited to work herein (I need to dig to remember which). 

###Usage:

```
#In IDLE, add the diretcory holding the SWMMIO python scripts 
#to your sys.path variable and import the modules:
import sys
sys.path.append('/path/to/swmmio/directory')

import swmmio
import swmm_graphics as sg
import swmm_utils as su
import swmm_compare as scomp

#intantiate a model object
model = swmmio.model('/directory containing SWMM .inp and .rpt files')

#create a image (.png) visualualization of the model
#by default, pipe stress and node flood duration is visualized
sg.drawModel("FileName", model)

``` 

### Acknowledgments
For use in generating animations of SWMM models, thanks to [images2gif.py](https://gist.github.com/jonschoning/7216290)
