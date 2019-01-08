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
Simplified 'first-step' version where Admiration is automatic
"""

from time import sleep
from random import sample, randint, shuffle, random
from numpy.random import choice

import sys
sys.path.append('..')
sys.path.append('../../..')

#sys.setrecursionlimit(1500)

import Evolife.Ecology.Observer	as EO
import Evolife.Scenarii.Default_Scenario as ED
import Evolife.Ecology.Individual as EI
import Evolife.Ecology.Alliances as EA
import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.Ecology.Group as EG
import Evolife.Ecology.Population as EP

from Evolife.Tools.Tools import percent, chances, decrease

class Scenario(ED.Default_Scenario):

	def __init__(self):
		# Parameter values
		ED.Default_Scenario.__init__(self, CfgFile='_Params.evo')	# loads parameters from configuration file

	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
        """
		return [('SelfSacrifice')] 		# gene size is read from configuration

	def display_(self):
		return [('red', 'SelfSacrifice')]

	def deathProbability(self, indiv):
		"proba that an individual will self-sacrifice during a given year"
		maxvalue = 2 **	self.Parameter('GeneLength') - 1
		return indiv.gene_value('SelfSacrifice') / maxvalue

	def selfSacrifice(self, indiv):	#Individuals are genetically programmed to self-sacrifice at a certain age
		"an agent decides to make the ultimate sacrifice"
		p = self.deathProbability(indiv)
		bool = p > random()
		# binary alternative:
		# bool = p > 0 & indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))
		indiv.SelfSacrifice = bool
		return bool

	def parenthood(self, RankedCandidates, Def_Nb_Children):
		" Determines the number of children depending on rank "
		ValidCandidates = RankedCandidates[:]
		for Candidate in ValidCandidates:
			if Candidate.SelfSacrifice or Candidate.age < self.Parameter('AgeAdult'):
				ValidCandidates.remove(Candidate)	# Children and (dead) heroes cannot reproduce
		candidates = [[m,0] for m in ValidCandidates]
		# parenthood is distributed as a function of the rank
		# it is the responsibility of the caller to rank members appropriately
		# Note: reproduction_rate has to be doubled, as it takes two parents to beget a child
		for ParentID in enumerate(ValidCandidates):
			candidates[ParentID[0]][1] = chances(decrease(ParentID[0],len(RankedCandidates), self.Parameter('Selectivity')), 2 * Def_Nb_Children)
		return candidates


	def new_agent(self, child, parents):
		" initializes newborns - parents==None when the population is created"
		if parents:       #add newborns to parents' list of descendants
			parents[0].Descendants.append((child,1))
			parents[1].Descendants.append((child,1))
		return True
#todo later : add grandchildren etc

	def sacrifices(self, members):
		""" Self-sacrifice 'game':
			Heroes may self-sacrifice "for the good of the group"
			Simplified version: sacrifice reaps direct benefits to their descendants
		"""
		Heroes = members[:]
		shuffle(Heroes)
		for Coward in Heroes:
			if not self.selfSacrifice(Coward): Heroes.remove(Coward)
		#Heroes = sample(Heroes,min(self.Parameter('MaxSacrifiers'),len(Heroes)))
		#NbHeroes = 0
				# After a certain number of selfsacrifices, selfsacrifice is pointless
				# ALT (plus tard) : decroitre les benefices avec le nb de deja sacrifies...

		for (HeroNbr, Hero) in enumerate(Heroes):
			#NbHeroes += 1
			#Hero.score(+ self.Parameter('PatriotismValue'))	# should be useless
			for (Desc, gen) in Hero.Descendants:
				Desc.score(+ percent(self.Parameter('KinSelection'))**gen \
										* self.Parameter('PatriotismValue'))

	def choseHero(self, indiv, Heroes):
		return
#        for Hero in Heroes:
#            if Hero.Followers.present(indiv): return     #a complexifier
#        RandomHero = choice(Heroes)
#        indiv.Followers.F_follow(0, Hero, 0)
#        indiv.Followers.F_follow(indiv.gene_value['Honoring'], Hero, 0)
#        indiv.Followers.F_follow(indiv.gene_value['Honoring'], Hero, Hero.gene_value['SelfSacrifice'])

	def choseFriends(self, indiv, members):
		return

	def life_game(self, members):
		self.sacrifices(members)    #Heroes chose to self-sacrifice for the group
		Heroes = []
		for indiv in members:
			if indiv.SelfSacrifice: Heroes.append(indiv)

		for indiv in members:
			self.choseHero(indiv,Heroes)
			self.choseFriends(indiv, members)
			self.evaluation(indiv)
		self.lives(members)


class Individual(EI.EvolifeIndividual):
	"   class Individual: defines what an individual consists of "

	def __init__(self, Scenario, ID=None, Newborn=True):
		self.SelfSacrifice = False
		self.Descendants = []
#		self.Friends = EA.Friend(self.Parameter('MaxFriends'))  #symettrical friendship links
#		self.Followers = EA.Followers(self.Parameter('MaxHeroes'), self.Parameter('MaxFollowers'))        #assymetrical follower links
#        EA.Friend.__init__()
#        EA.Follower.__init__(
		EI.EvolifeIndividual.__init__(self, Scenario, ID=ID, Newborn=Newborn)

	def isDesc(self, Indiv):
		if Indiv in self.Descendants: return True
		return False

class Group(EG.EvolifeGroup):
	# The group is a container for individuals. (For now the population only has one)
	# Individuals are stored in self.members

	def __init__(self, Scenario, ID=1, Size=100):
		EG.EvolifeGroup.__init__(self, Scenario, ID, Size)

	def createIndividual(self, ID=None, Newborn=True):
		# calling local class 'Individual'
		Indiv = Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
		# Individual creation may fail if there is no room left
		self.Scenario.new_agent(Indiv, None)  # let scenario know that there is a newcomer
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
			child = Individual(self.Scenario,ID=self.free_ID(), Newborn=True)
			if child:
				child.hybrid(C[0],C[1]) # child's DNA results from parents' DNA crossover
				child.mutate()
				child.update()  # computes the value of genes, as DNA is available only now
				if self.Scenario.new_agent(child, C):  # let scenario decide something about the newcomer
					self.receive(child) # adds child to the group

			#Future fonction petits enfants+ a inserer ici



###########
class Population(EP.EvolifePopulation):
	" defines the population of agents "

	def __init__(self, Scenario, Observer):
		" creates a population of agents "
		EP.EvolifePopulation.__init__(self, Scenario, Observer)

		self.Scenario = Scenario
		#self.Ranking = []
		self.Heroes = []
		#self.Year = -1
#	def update(self, FlagRanking = False, Display = False):
#		for Indiv in self.Pop:
#			Indiv.update(FlagRanking, Display)

#	def display(self):
#		if self.Observer.Visible() # statistis for display
#		self.Observer.record()
#		self.Observer.curve('SelfSacrifice', , 'Red', Legend = None)

	def createGroup(self, ID=0, Size=0):
		return Group(self.Scenario, ID=ID, Size=Size)

#	def season(self, year):
#		" This function is called at the beginning of each year "
#		#self.Year += 1
#		self.Observer.season()	# increments year
#		self.Scenario.season(year, self.Pop)
###### Ca avance la ?? -> pb a faire aller-retour avec Scenario ?

#	def statistics(self, Complete = True, Display = False):
		" Updates statistics about the population"
#		self.update(Display = Display)	# updates facts
#		self.Observer.reset()
#		if Complete:
#			self.Observer.open_()
#			self.Examiner.reset()
#			self.Examiner.open_(self.PopSize)
#			for agent in self.Pop:
#				agent.observation(self.Examiner)
#			self.Examiner.close_()
#			self.Observer.close_()	# computes statistics in Observer

#	def free_ID(self, Prefix=''):
#		" returns an available ID "
#		IDs = [m.ID for m in self.members]
#		for ii in range(100000):
#			if Prefix:	ID = '%s%d' % (Prefix, ii)
#			else:		ID = '%d_%d' % (self.ID, ii)	# considering group number as prefix
#			if ID not in IDs:	return ID
#		return -1

#	def receive(self, newcomer):
#		" accepts a new member in the group "
#		if newcomer:
#			self.Pop.append(newcomer)
#			self.size += 1

#	def limit(self):
#		" randomly kills individuals until size is reached "
#		self.update()
#		while self.PopSize > self.Scenario.Parameter('PopulationSize'):
#			Unfortunate = choice(self.Pop)
#			self.Pop.pop(Unfortunate)
#			self.PopSize -= 1
#		self.update(display=True)

#	def ranking(self):				# hypo: points also earn adoption rights
#		self.Ranking = self.Pop[:]	  # duplicates the list, not the elements
#		for indiv in self.Ranking:
#			if not indiv.adult():
#				self.Rankingg.remove(indiv)	# children cannot reproduce
#		shuffle(self.Ranking)			# so as to randomize among individuals with the same number of points
#		self.Ranking.sort(key=lambda x: x.score(),reverse=True)


#	def geneAvg(self, gene):
#		Avg = 0
#		for indiv in self.Pop: Avg += indiv.gene_value(gene)
#		if self.Pop: Avg /= len(self.Pop)
#		return Avg

#	def display(self):
#		Colours = ['red', 'blue', 'brown']
#		C = 0
#		for gene in self.Scenario.GeneMap:
#			self.Observer.curve(gene, self.geneAvg(gene), Color = Colours[C])
#			C += 1

#	def one_run(self):
#		self.season(self.Year)
		#self.Scenario.display_()
		#self.display()

#		self.reproduction() 	# reproduction depends on scores

#		self.Scenario.life_game(self.Pop)		# where individuals earn their scores
		#self.statistics()

		#Gene = self
		#self.Observer.curve(self.)
#		return True

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
