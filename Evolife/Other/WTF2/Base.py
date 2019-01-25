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
Simplified 'first-step' version where Admiration is automatic
"""

from random import sample, shuffle, random, choice

import sys
sys.path.append('..')
sys.path.append('../../..')

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

#	def new_agent(self, child, parents, gen = 1):
#		" initializes newborns - parents==None when the population is created"
#		if parents:       #add newborns to parents' list of descendants
#			parents[0].Descendants.append((child,gen))
#			parents[1].Descendants.append((child,gen))
#		return True
# RMQ: descendands treated in Indiv and Group

	def sacrifices(self, members):
		""" Self-sacrifice 'game':
			Heroes may self-sacrifice "for the good of the group"
			Simplified version: sacrifice reaps direct benefits to their descendants
		"""
		Heroes = []
		for Hero in members:
			if self.selfSacrifice(Hero): Heroes.append(Hero)
		shuffle(Heroes)
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

	def partner(self, indiv, members):
		""" Decides whom to interact with - Used in 'life_game'
		"""
		# By default, a partner is randomly chosen
		partners = members[:]
		partners.remove(indiv)
		if partners != []:
			return choice(partners)
		else:
			return None

	def interaction(self, indiv, partner):
		" Nothing by default - Used in 'life_game' "
		pass

	def life_game(self, members):
		# First: chose heroes, that self-sacrifice for the group
		self.sacrifices(members)
		# Then: play multipartite game
		for play in range(self.Parameter('Rounds', Default=1)):
			players = members[:]	# ground copy
			shuffle(players)
			# Individuals engage in several interactions successively
			for indiv in players:
				Partner = self.partner(indiv, players)
				if Partner is not None:
					self.interaction(indiv, Partner)
		# Last: work out final tallies
		for indiv in members:
			self.evaluation(indiv)
		# scores are translated into life points
		self.lives(members)


class Individual(EI.EvolifeIndividual):
	"   class Individual: defines what an individual consists of "

	def __init__(self, Scenario, ID=None, Newborn=True):
		self.SelfSacrifice = False
		self.Descendants = []

################################

		self.Offerings = 0		# represents how much one is honored after self-sacrifice (should stay at 0 whilst alive)
		self.SignalLevel = 0



#		self.Friends = EA.Friend(self.Parameter('MaxFriends'))  #symettrical friendship links
#		self.Followers = EA.Followers(self.Parameter('MaxHeroes'), self.Parameter('MaxFollowers'))        #assymetrical follower links
#        EA.Friend.__init__()
#        EA.Follower.__init__(
		EI.EvolifeIndividual.__init__(self, Scenario, ID=ID, Newborn=Newborn)

	def isDesc(self, Indiv, gen = 1):
		if (Indiv, g) in self.Descendants: return True
		return False

	def generationalGap(self, Desc):
		" returns the 'generational gap' (1 for a child) if Desc descends from Individual "
		for i in range(len(self.Descendants)):
			if self.Descendants[i][0] == Desc:
				return self.Descendants[i][1]
		return None

	#	if Indiv.Descendants:
##
#			gmax = Indiv.Descendants[0][1]		# descendants are sorted by descending generational gaps
#			for g in range(1, gmax + 1):
#				if isDesc(Desc, g):
#					return g
#		return None

	def addDescendant(self, descendant, gen = 1):
		" adds descendants coupled with the 'generational gap' (1 for a child)"
		self.Descendants.append((descendant, gen))

class Group(EG.EvolifeGroup):
	# The group is a container for individuals. (For now the population only has one)
	# Individuals are stored in self.members

	def __init__(self, Scenario, ID=1, Size=100):
		EG.EvolifeGroup.__init__(self, Scenario, ID, Size)

	def createIndividual(self, ID=None, Newborn=True):
		# calling local class 'Individual'
		Indiv = Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
		# Individual creation may fail if there is no room left
		self.Scenario.new_agent(Indiv, None)  # let scenario know that there is a newcomer (unused)
		#if Indiv.location == None:	return None
		return Indiv

	def updateDescendants(self, parent, child):
		""" updates descendants : when a parent recieves a child, his/her parents (Ascendant) receive a grand-child,
		 	their parents receive a great-grand child ...
		"""
		parent.addDescendant(child, 1)
		for Ascendant in self.members:
			g = Ascendant.generationalGap(parent)
			if g:
				Ascendant.addDescendant(child, g+1)

#	def new_agent(self, child, parents, gen = 1):
#		" initializes newborns - parents==None when the population is created"
#		if parents:       #add newborns to parents' list of descendants
#			parents[0].Descendants.append((child,gen))
#			parents[1].Descendants.append((child,gen))
#		return True

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
				if self.Scenario.new_agent(child, C):  # let scenario decide something about the newcomer (not used here)
					self.updateDescendants(C[0], child)
					self.updateDescendants(C[1], child)
					self.receive(child) # adds child to the group




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

	""" TODO: transformer en fonction appelable par le vrai """
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
