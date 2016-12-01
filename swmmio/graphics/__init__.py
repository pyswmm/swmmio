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
