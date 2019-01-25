#!/usr/bin/env python
#!/usr/bin/env python
#!/usr/bin/env python
#!/usr/bin/env python
#!/usr/bin/env python3
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2018                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# Chaotic fractals                                                                                           #
##############################################################################

"""	Chaotic fractals
		Written by Felix Richart in 2017
"""



import sys
from time import sleep
import random
import re
import math
		
sys.path.append('..')
sys.path.append('../../..')
import Evolife.Scenarii.Parameters			as EPar
import Evolife.Ecology.Observer				as EO
import Evolife.QtGraphics.Evolife_Window	as EW
import Evolife.Tools.Tools					as ET


	
class Chaos_Observer(EO.Observer):
	""" Stores global variables for observation
	"""
	def __init__(self, Scenario):
		EO.Observer.__init__(self, Scenario)
		self.Trajectories = []	# stores temporary changes
		self.MsgLength = dict()

	def Trajectory_grid(self):
		" initial draw (see 'GraphicExample.py' for details) "
		# drawing an invisible diagonal to set the scale
		return [(0, 0, 0, 0, 100, 100, 0, 0),]
				# (100, 0, 'green', 0, 100, 100, 'green', 5),
				# (100, 100, 'green', 0	, 0, 100, 'green', 5),
				# (0, 100, 'green', 4, 0, 0, 'green', 5), ]		

	def recordChanges(self, Info, Slot='Positions'):
		# stores current changes
		# Info is a couple (InfoName, Position) and Position == (x, y) or a longer tuple
		if Slot == 'Trajectories':	self.Trajectories.append(Info)
		else:	ET.error('Hyperlinks Observer', 'unknown slot')

	def get_info(self, Slot, default=None):
		" this is called when display is required "
		if Slot == 'Trajectories':
			CC = self.Trajectories
			self.Trajectories = []
			return tuple(CC)
		else:	return EO.Observer.get_info(self, Slot, default=default)

class Fractal:
	"""	Defines a network as a graph
	"""
	def __init__(self, Observer, Shape=[(250, 490), (10, 10), (490, 10)], Coef=0.5, InitialPos=None, DotSize=1):
		self.Observer = Observer
		self.Shape = Shape
		self.DotSize = DotSize
		self.nbOfDots = 0
		self.Coef = 1 - Coef
		self.Dot = InitialPos if InitialPos is not None else [random.randint(10, 100), random.randint(10, 100),]
		for i in range(0, len(Shape)):
			Observer.recordChanges(('S%d' % i, (Shape[i][0], Shape[i][1], 'red', 8)), Slot='Trajectories')
		
	def addDot(self):
		self.Observer.season()
		Observer.recordChanges(('D%d' % self.nbOfDots, (self.Dot[0], self.Dot[1], 'green', self.DotSize)), Slot='Trajectories')
		self.nbOfDots += 1
		DotToFocus = self.Shape[random.randint(0, len(self.Shape)-1)]
		self.Dot[0] = self.Dot[0]+(DotToFocus[0]-self.Dot[0])*self.Coef
		self.Dot[1] = self.Dot[1]+(DotToFocus[1]-self.Dot[1])*self.Coef
		return True

if __name__ == "__main__":
	print(__doc__)

	#############################
	# Global objects	    #
	#############################
	Gbl = EPar.Parameters('_Params.evo')	# Loading global parameter values
	Observer = Chaos_Observer(Gbl)   # Observer contains statistics
	#[(10, 10), (490, 10), (490, 490), (10, 490)]
	Fractal0 = Fractal(Observer, Shape=Gbl.Parameter('InitialDots'), Coef=Gbl.Parameter('Coefficient'), DotSize=Gbl.Parameter('DotSize'))
	# Initial draw
	Observer.recordInfo('TrajectoriesWallpaper', 'yellow')
	Observer.recordInfo('TrajectoriesTitle', 'Chaotic fractals')
	Observer.recordInfo('DefaultViews', [('Trajectories', 600, 100, 800, 800)])
	EW.Start(Fractal0.addDot, Observer, Capabilities='RPT')

	print("Bye.......")

__author__ = 'Felix Richart'


#Questions : how to set depth (random or fixed)
#how to create graph (random order ?)
#fix number of hyperlinks per node or hyperlinks for the whole network
#how to plot
