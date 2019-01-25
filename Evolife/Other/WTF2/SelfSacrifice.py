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


""" Study of the possibility of self-sacrifice being an ESS
"""

# TODO : limiter le nombre de fana d'un heros ?

#from time import sleep
#from random import sample, randint, shuffle, random
#from numpy.random import choice

import sys

import Base
sys.path.append('..')
sys.path.append('../../..')

# import Evolife.Other.SelfSacrifice.SelfSacrifice-v0 as Base
import Evolife.Ecology.Alliances as EA
import Evolife.Ecology.Observer	as EO
import Evolife.QtGraphics.Evolife_Window as EW
from Evolife.Tools.Tools import percent, powerlaw

class Scenario(Base.Scenario):

	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
        """
		return [('SelfSacrifice'), ('Honoring')] 		# gene size is read from configuration

	def display_(self):
		return [('red', 'SelfSacrifice'), ('blue', 'Honoring')]

	def sacrifices(self, members):
		""" Self-sacrifice 'game':
			Heroes may self-sacrifice "for the good of the group"
		"""
		for Hero in members:
			self.selfSacrifice(Hero)
		return

	def spillOver(self, Hero, kin_transfer = 0.5):
		""" A hero's descendants indirectly benefit from his or her sacrifice,
			proportionally to how much he or she is honored
			and depending on how close they are to the hero in the family tree
		"""
		tot_benef = percent(Hero.Offerings * self.Parameter('SacrificeHeredity'))	# Not all offerings translate into benefits for kin
		tot_weights = 0
		for (Desc, gen) in Hero.Descendants:
			tot_weights += (kin_transfer)**gen
		for (Desc, gen) in Hero.Descendants:
			share = (kin_transfer)**gen	# share is coefficient of relatedness by default (depends on the 'KinSelection' parameter)
			Desc.score(+ share / tot_weights * tot_benef)

	def honor(self, indiv, Hero):
		" An individual honors a fallen hero"
		offering = indiv.gene_value('Honoring')
		# an individual gives (his time, a valuable object, a goat...) proportionally to his or her genes
		indiv.score(- offering)
		Hero.Offerings += offering
		# Offering is a signal to others (for friendship links)
		indiv.SignalLevel += offering
		return

	def friendship(self, indiv, partner):
		# new interaction puts previous ones into question
		if indiv.follows(partner):	indiv.end_friendship(partner)	# symmetrical splitting up

		# TODO modifier
		indiv.get_friend(indiv.SignalLevel, partner, partner.SignalLevel)
		#partner.get_friend(indiv.SignalLevel)


	def interaction(self, indiv, partner):
		if partner.SelfSacrifice: self.honor(indiv, partner)
		else: self.friendship(indiv, partner)

#        for Hero in Heroes:
#            if Hero.Followers.present(indiv): return     #a complexifier
#        RandomHero = choice(Heroes)
#        indiv.Followers.F_follow(0, Hero, 0)
#        indiv.Followers.F_follow(indiv.gene_value['Honoring'], Hero, 0)
#        indiv.Followers.F_follow(indiv.gene_value['Honoring'], Hero, Hero.gene_value['SelfSacrifice'])

	def evaluation(self, indiv):
		if indiv.SelfSacrifice:
			self.spillOver(indiv, self.Parameter('KinSelection'))
		" You gain points according to your friends true value "
		#for Friend in indiv.friends:
		for Friend in indiv.followers:
		#for friend in self.members:
		#	if friend.follows(indiv):
			if friend.Patriotism < 10: # Friend is a traitor who sells you out
				indiv.score(- self.Parameter('FriendshipValue'))
			if friend.Patriotism > 90: # Friend is a true patriot who can vouch for you
				#friend_value = powerlaw( 100 - Friend.Patriotism, self.Parameter('FriendshipValue')) # a moduler
				#indiv.score(+ friend_value)
				indiv.score(- self.Parameter('FriendshipValue'))
		print(indiv.ID)
		print(indiv.score)


class Patriotic_Individual(Base.Individual, EA.Follower):
	"   Individuals now also have a patriotism phenotype "

	def __init__(self, Scenario, ID, maxPatriotism = 100, Newborn=True):
		#self.Patriotism = (100.0 * ID) / maxPatriotism
		self.Patriotim = 0
		Base.Individual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
		self.Offerings = 0		# represents how much one is honored after self-sacrifice (should stay at 0 whilst alive)
		self.SignalLevel = 0
		self.BestSIgnal = 0
		EA.Follower.__init__(self, self.Parameter('MaxFriends'), self.Parameter('MaxFriends'))

	def Signal(self, Feature=None, Transparent=False):
		" returns the actual quality of an individual or its displayed version "
		# TODO modif
		if Transparent:	return self.Patriotism
		#BC = Gbl.Param('BottomCompetence')
		#Comp = percent(100-BC) * self.Patriotism + BC
		VisiblePatriotism = percent(self.Patriotism * self.gene_value('Honoring'))
		#return self.Limitate(VisibleCompetence, 0, 100)
		return VisiblePatriotism

	# TODO : + update / display ---> rpz graphique 2d avec Patriotism

class Group(Base.Group):
	" In each group, patriotism ranges from 0 to group size (simplification) "

	def __init__(self, Scenario, ID=1, Size=100):
		Base.Group.__init__(self, Scenario, ID, Size)

	def createIndividual(self, ID=None, Newborn=True):
		# calling local class 'Individual'
		Indiv = Patriotic_Individual(self.Scenario, ID=self.free_ID(), maxPatriotism = self.size, Newborn=Newborn)
		# Individual creation may fail if there is no room left
		self.Scenario.new_agent(Indiv, None)  # let scenario know that there is a newcomer (unused)
		#if Indiv.location == None:	return None
		return Indiv

	def reproduction(self):
		""" reproduction within the group
			reproduction_rate is expected in %
		"""
		# The function 'couples' returns as many couples as children are to be born
		# The probability of parents to beget children depends on their rank within the group
		self.update_(flagRanking=True)   # updates individual ranks
		#self.adoptRanking()
		for C in self.Scenario.couples(self.ranking):
			# making of the child
			child = Patriotic_Individual(self.Scenario,ID=self.free_ID(), maxPatriotism = self.size, Newborn=True)
			if child:
				child.hybrid(C[0],C[1]) # child's DNA results from parents' DNA crossover
				child.mutate()
				child.update()  # computes the value of genes, as DNA is available only now
				if self.Scenario.new_agent(child, C):  # let scenario decide something about the newcomer (not used here)
					self.updateDescendants(C[0], child)
					self.updateDescendants(C[1], child)
					self.receive(child) # adds child to the group


#### HEROES utile ou pas ????
###########
class Population(Base.Population):
	" defines the population of agents "

	def __init__(self, Scenario, Observer):
		" creates a population of agents "
		Base.Population.__init__(self, Scenario, Observer)

		self.Scenario = Scenario
		self.Heroes = []

	def createGroup(self, ID=0, Size=0):
		return Group(self.Scenario, ID=ID, Size=Size)


if __name__ == "__main__":
	print(__doc__)


	#############################
	# Global objects			#
	#############################
	Gbl = Scenario()
	Observer = EO.EvolifeObserver(Gbl)	  # Observer contains statistics
	Pop = Population(Gbl, Observer)

	#Observer.recordInfo('Background', 'white')
	#Observer.recordInfo('FieldWallpaper', 'white')

	EW.Start(Pop.one_year, Observer, Capabilities='PCG')

	print("Bye.......")



__author__ = 'Dessalles'
