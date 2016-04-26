SWMMIO is a set of python tools for interacting with and visualizing results from EPA Stomwater Management Model input and output files (.inp and .rpt). These tools are being developed specifically for the application of flood risk management.

Usage:
  
      #In IDLE, add the diretcory holding the SWMMIO python scripts to your sys.path variable and import the modules:
      
      import sys
      
      sys.path.append('/path/to/swmmio/directory')
      
      import swmmio
      
      import swmm_graphics as sg
      
      import swmm_utils as su
      
      import swmm_compare as scomp
      
      #intantiate a model object
      
      model = swmmio.model('/directory containing SWMM .inp and .rpt files')
      
  
