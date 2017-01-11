class _dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

"""
this allows module wide configuration of drawing methods. The dotdict allows for
convenient access.
Example:

    from swmmio import graphics
    from swmmio.graphics import swmm_graphics as sg

    #configure
    graphics.options.inlcude_parcels = True

    #draws the model with parcels
    sg.drawModel(swmmio.Model(/path/to/model), bbox=su.d68d70)

"""
_o = {
    'include_basemap':False,
    'include_parcels':False,
}

config = _dotdict(_o)


#CONSTANTS
red = 		(250, 5, 5)
blue = 		(5, 5, 250)
lightblue = (184, 217, 242)
shed_blue = (0,169,230)
white =		(250,250,240)
black = 	(0,3,18)
mediumgrey = (190, 190, 180)
lightgrey = (235, 235, 225)
grey = 		(100,95,97)
park_green = (115, 178, 115)
green = 	(115, 220, 115)
green_bright= (23, 191, 23)
lightgreen = (150,212,166)
water_grey = (130, 130, 130)
purple = (250, 0, 250)
