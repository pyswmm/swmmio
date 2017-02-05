SWMMIO
======

|Kool Pic| SWMMIO is a set of python tools aiming to provide a means for
version control and visualizing results from the EPA Stormwater
Management Model (SWMM). Command line tools are also provided for
running models individually and in parallel via Python’s
``multiprocessing`` module. These tools are being developed specifically
for the application of flood risk management, though most functionality
is applicable to SWMM modeling in general.

Prerequisites
~~~~~~~~~~~~~

SWMMIO functions primarily by interfacing with .inp and .rpt (input and
report) files produced by SWMM. Functions within the ``run_models``
module rely on a SWMM5 engine which can be downloaded `here`_.

Dependencies
~~~~~~~~~~~~

-  `pillow`_: 3.0.0
-  `matplotlib`_
-  `numpy`_
-  `pandas`_
-  `pyshp`_

Installation:
~~~~~~~~~~~~~

Before installation, it’s recommended to first activate a `virtualenv`_
to not crowd your system’s package library. If you don’t use any of the
dependencies listed above, this step is less important. SWMMIO can be
installed via pip in your command line:

.. code:: bash

    #on Windows:
    python -m pip install swmmio

    #on Unix-type systems, i do this:
    pip install swmmio

Basic Usage
~~~~~~~~~~~

The ``swmmio.Model()`` class provides the basic endpoint for interfacing
with SWMM models. To get started, save a SWMM5 model (.inp) in a
directory with its report file (.rpt). A few examples:

.. code:: python

    from swmmio import swmmio

    #instantiate a swmmio model object
    mymodel = swmmio.Model('/path/to/directory with swmm files')

    #Pandas dataframe with most useful data related to model nodes, conduits
    nodes = mymodel.nodes()
    conduits = mymodel.conduits()

    #enjoy all the Pandas functions
    nodes.head()

.. raw:: html

   <table border=1 class=dataframe>

.. raw:: html

   <thead>

.. raw:: html

   <tr style=text-align:right>

.. raw:: html

   <th>

.. raw:: html

   <th>

InvertElev

.. raw:: html

   <th>

MaxDepth

.. raw:: html

   <th>

SurchargeDepth

.. raw:: html

   <th>

PondedArea

.. raw:: html

   <th>

Type

.. raw:: html

   <th>

AvgDepth

.. raw:: html

   <th>

MaxNodeDepth

.. raw:: html

   <th>

MaxHGL

.. raw:: html

   <th>

MaxDay\_depth

.. raw:: html

   <th>

MaxHr\_depth

.. raw:: html

   <th>

HoursFlooded

.. raw:: html

   <th>

MaxQ

.. raw:: html

   <th>

MaxDay\_flood

.. raw:: html

   <th>

MaxHr\_flood

.. raw:: html

   <th>

TotalFloodVol

.. raw:: html

   <th>

MaximumPondDepth

.. raw:: html

   <th>

X

.. raw:: html

   <th>

Y

.. raw:: html

   <th>

coords

.. raw:: html

   <tr>

.. raw:: html

   <th>

Name

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <th>

.. raw:: html

   <tbody>

.. raw:: html

   <tr>

.. raw:: html

   <th>

S42A\_10.N\_4

.. raw:: html

   <td>

13.506673

.. raw:: html

   <td>

6.326977

.. raw:: html

   <td>

5.0

.. raw:: html

   <td>

110.0

.. raw:: html

   <td>

JUNCTION

.. raw:: html

   <td>

0.69

.. raw:: html

   <td>

6.33

.. raw:: html

   <td>

19.83

.. raw:: html

   <td>

0

.. raw:: html

   <td>

12:01

.. raw:: html

   <td>

0.01

.. raw:: html

   <td>

0.20

.. raw:: html

   <td>

0.0

.. raw:: html

   <td>

11:52

.. raw:: html

   <td>

0.000

.. raw:: html

   <td>

6.33

.. raw:: html

   <td>

2689107.0

.. raw:: html

   <td>

227816.000

.. raw:: html

   <td>

[(2689107.0, 227816.0)]

.. raw:: html

   <tr>

.. raw:: html

   <th>

D70\_ShunkStreet\_Trunk\_43

.. raw:: html

   <td>

8.508413

.. raw:: html

   <td>

2.493647

.. raw:: html

   <td>

5.0

.. raw:: html

   <td>

744.0

.. raw:: html

   <td>

JUNCTION

.. raw:: html

   <td>

0.04

.. raw:: html

   <td>

0.23

.. raw:: html

   <td>

8.74

.. raw:: html

   <td>

0

.. raw:: html

   <td>

12:14

.. raw:: html

   <td>

NaN

.. raw:: html

   <td>

NaN

.. raw:: html

   <td>

NaN

.. raw:: html

   <td>

NaN

.. raw:: html

   <td>

NaN

.. raw:: html

   <td>

NaN

.. raw:: html

   <td>

2691329.5

.. raw:: html

   <td>

223675.813

.. raw:: html

   <td>

[(2691329.5, 223675.813)]

.. raw:: html

   <tr>

.. raw:: html

   <th>

TD61\_1\_2\_90

.. raw:: html

   <td>

5.150000

.. raw:: html

   <td>

15.398008

.. raw:: html

   <td>

0.0

.. raw:: html

   <td>

0.0

.. raw:: html

   <td>

JUNCTION

.. raw:: html

   <td>

0.68

.. raw:: html

   <td>

15.40

.. raw:: html

   <td>

20.55

.. raw:: html

   <td>

0

.. raw:: html

   <td>

11:55

.. raw:: html

   <td>

0.01

.. raw:: html

   <td>

19.17

.. raw:: html

   <td>

0.0

.. raw:: html

   <td>

11:56

.. raw:: html

   <td>

0.000

.. raw:: html

   <td>

15.40

.. raw:: html

   <td>

26984

.. _here: https://www.epa.gov/water-research/storm-water-management-model-swmm
.. _pillow: http://python-pillow.org/
.. _matplotlib: http://matplotlib.org/
.. _numpy: http://www.numpy.org/
.. _pandas: https://github.com/pydata/pandas
.. _pyshp: https://github.com/GeospatialPython/pyshp
.. _virtualenv: https://github.com/pypa/virtualenv

.. |Kool Pic| image:: docs/img/impact_of_option.png?raw=true
