#!/usr/bin/env python
#coding:utf-8
# Author:  aerispaha
# Purpose: init
# Created: 05.02.2016
# License: MIT License
# Copyright (C) 2016  Adam Erispaha



from swmm_compare import comparisonReport, drawModelComparison
from swmm_graphics import drawModel, animateModel, drawProfile
from swmmio import Model
import swmmio


#CONSTANTS
sPhilaBox = 	((2683629, 220000), (2700700, 231000))
sPhilaSq =		((2683629, 220000), (2700700, 237071))
sPhilaSm1 = 	((2689018, 224343), (2691881, 226266))
sPhilaSm2 = 	((2685990, 219185), (2692678, 223831))
sPhilaSm3 = 	((2688842, 220590), (2689957, 221240))
sPhilaSm4 = 	((2689615, 219776), (2691277, 220738))
sPhilaSm5 = 	((2690303, 220581), (2690636, 220772))
sm6 = 			((2692788, 225853), (2693684, 226477))
chris = 		((2688798, 221573), (2702834, 230620))
nolibbox= 		((2685646, 238860),	(2713597, 258218))
mckean = 		((2691080, 226162),	(2692236, 226938))
d70 = 			((2694096, 222741),	(2697575, 225059))
ritner_moyamen =((2693433, 223967),	(2694587, 224737))
morris_10th = 	((2693740, 227260),	(2694412, 227693))
morris_12th = 	((2693257, 227422),	(2693543, 227614))
study_area = 	((2682005, 219180), (2701713, 235555))
dickenson_7th = ((2695378, 227948), (2695723, 228179))
packer_18th = 	((2688448, 219932), (2691332, 221857))
moore_broad = 	((2689315, 225537), (2695020, 228592))
