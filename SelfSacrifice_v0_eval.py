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
Simplified 'first-step' (base) version where Admiration is automatic
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
		return [('SelfSacrifice')] 		# gene length (in bits) is read from configuration

	def display_(self):
		return [('red', 'SelfSacrifice')]

	def deathProbability(self, indiv):
		" Converts an individual's genetic propensity to self-sacrifice into a probability "
		maxvalue = 2 **	self.Parameter('GeneLength') - 1
		return (indiv.gene_value('SelfSacrifice') / maxvalue)

	def selfSacrifice(self, indiv):
		""" An agent decides to make the ultimate sacrifice
			Self-Sacrifice is only a possibiltiy from a certain age (e.g. adulthood)
			and is controlled by the SelfSacrifice gene (see deathProbability)
		"""
		p = self.deathProbability(indiv)
		#bool = p > random()
		bool = p > random() and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))
		# binary alternative: (Individuals are programmed to self-sacrifice at a certain age)
		# bool = p > 0 and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))
		indiv.SelfSacrifice = bool
		return bool

	def parenthood(self, RankedCandidates, Def_Nb_Children):
		""" Determines the number of children depending on rank
		Note: when Selectivity is 0 (as is the default), number of children does not depend on rank
		Using Selectivity instead of SelectionPressure leads to much faster albeit perhaps less realistic convergence
		(as having 1001 points is much better than having 1000...)
		"""
		ValidCandidates = RankedCandidates[:]
		for Candidate in ValidCandidates:
			if Candidate.SelfSacrifice or Candidate.age < self.Parameter('AgeAdult'):
				ValidCandidates.remove(Candidate)	# Children and (dead) heroes cannot reproduce
		candidates = [[m,0] for m in ValidCandidates]
		# Parenthood is distributed as a function of the rank
		# It is the responsibility of the caller to rank members appropriately
		# Note: reproduction_rate has to be doubled, as it takes two parents to beget a child
		for ParentID in enumerate(ValidCandidates):
			candidates[ParentID[0]][1] = chances(decrease(ParentID[0],len(RankedCandidates), self.Parameter('Selectivity')), 2 * Def_Nb_Children)
		return candidates

	def sacrifices(self, members, max_heroes = 1):	# max_heroes will be a parameter
		""" Self-sacrifice 'game':
			Heroes may self-sacrifice "for the good of the group"
		"""
		for i in range(max_heroes):	# Cost of self-sacrifice is too elevated if anyone can be a hero every year
			Potential_Hero = choice(members)	# Potential_Hero is in a position of acting like a hero
			self.selfSacrifice(Potential_Hero)
		return

	def directSpillover(self, Hero, social_admiration = 0, kin_transfer = 0.5):
		""" A hero's descendants directly benefit from his or her sacrifice
			through social admiration of that hero (which 'spillsover' to them)
		"""
		for (Desc, gen) in Hero.Descendants:
			weight = kin_transfer ** gen		# More admiration is 'spilled over' to children than to grand-children, etc.
			Desc.score(+ weight * social_admiration)

#	def sacrifices(self, members):
#		""" Self-sacrifice 'game':	Heroes may self-sacrifice "for the good of the group"
#			Simplified version: sacrifice reaps direct benefits to their descendants,
#			as heroes and their descendants are admired (exogenously)
#		"""
#		Heroes = []
#		for Hero in members:
#			if self.selfSacrifice(Hero): Heroes.append(Hero)
		# In comments(#): alternative where benefits are a decreasing function of the number of heroes
		# shuffle(Heroes)
		# Decreasing_Admiration = self.Parameter('Admiration')
#		for (HeroNbr, Hero) in enumerate(Heroes):
			# if Hero_Nb < len(Heroes): Decreasing_Admiration = Decreasing_Admiration / 2.0
						# Sacrifice value decreases as others have already self-sacrificed (sum to self.Parameter('Admiration'))
#			for (Desc, gen) in Hero.Descendants:	# Children receive more admiration than grand-children, etc.
#				Desc.score(+ percent(self.Parameter('KinSelection'))**gen \
#										* self.Parameter('Admiration'))
				#Desc.score(+ percent(self.Parameter('KinSelection'))**gen \
				#						* Decreasing_Admiration)
				# The share that a heroic family gets depends on how early their ascendant sacrificed

	def prepare(self, indiv):
		""" Defines what is to be done at the individual level before interactions
			occur - Used in 'start_game'
		"""
		indiv.score(0, FlagSet = True)	# Sets score to 0

	def start_game(self, members):
		""" Defines what is to be done at the group level each year
			before interactions occur - Used in 'life_game'
		"""
		for indiv in members:	self.prepare(indiv)

	def evaluation(self, indiv):
		""" Implements the computation of individuals' scores - Used in 'life_game'
		"""
		if indiv.SelfSacrifice:
			self.directSpillover(indiv, self.Parameter('Admiration', Default = 0), percent(self.Parameter('KinSelection', Default = 50)))

	def lives(self, members):
		" Converts scores into life points - used in 'life_game'"
		if self.Parameter('SelectionPressure') == 0:
			return	# 'Selectivity mode' : outcomes depend on relative ranking
		if len(members) == 0:
			return
		BestScore = max([i.score() for i in members])
		MinScore = min([i.score() for i in members])
		if BestScore == MinScore:	return
		for indiv in members:
			if indiv.SelfSacrifice:
				indiv.LifePoints = -1	# Individual dies
			else:		# Translating scores to Lifepoints above zero
				indiv.LifePoints = (self.Parameter('SelectionPressure') \
								* (indiv.score() - MinScore))/float(BestScore - MinScore)
		return

	def partner(self, indiv, members):
		""" Decides whom to interact with - Used in 'life_game'
			By default, a partner is randomly chosen
		"""
		# By default, a partner is randomly chosen
		partners = members[:]
		partners.remove(indiv)
		if partners != []:
			return choice(partners)
		else:
			return None

	def interaction(self, indiv, partner):
		""" Nothing by default - Used in 'life_game'
			To be overwritten
		"""
		pass

	def life_game(self, members):
		""" Defines one year of play (outside of reproduction)
			This is where individual's acquire their score
		"""
		# First: make initializations
		self.start_game(members)
		# Then: play multipartite game
		self.sacrifices(members, self.Parameter('MaxHeroes', Default=1))
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
		# Scores are translated into life points, which affect individual's survival
		self.lives(members)


class Individual(EI.EvolifeIndividual):
	"   Defines what an individual consists of "

	def __init__(self, Scenario, ID=None, Newborn=True):
		self.SelfSacrifice = False
		self.Descendants = []
		EI.EvolifeIndividual.__init__(self, Scenario, ID=ID, Newborn=Newborn)

	def isDesc(self, Indiv, gen = 1):
		if (Indiv, g) in self.Descendants: return True
		return False

	def generationalGap(self, Desc):
		""" Returns the 'generational gap' (1 for a child) if Desc descends from Individual
			Used in 'updateDescendants'
		"""
		for i in range(len(self.Descendants)):
			if self.Descendants[i][0] == Desc:
				return self.Descendants[i][1]
		return None

	def addDescendant(self, descendant, gen = 1):
		""" Adds descendants coupled with the 'generational gap' (1 for a child)
			Used in 'updateChildren' or 'updateDescendants'
		"""

		self.Descendants.append((descendant, gen))

class Group(EG.EvolifeGroup):
	""" The group is a container for individual (By default the population only has one)
		It is also the level at which reproduction occurs
		Individuals are stored in self.members
	"""

	def __init__(self, Scenario, ID=1, Size=100):
		EG.EvolifeGroup.__init__(self, Scenario, ID, Size)

	def createIndividual(self, ID=None, Newborn=True):
		" Calling local class 'Individual'"
		Indiv = Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
		# Individual creation may fail if there is no room left
		self.Scenario.new_agent(Indiv, None)  # Let scenario know that there is a newcomer (unused)
		return Indiv

	def updateDescendants(self, parent, child):
		""" Updates descendants : when a parent recieves a child, his/her parents (Ascendant) receive a grand-child,
		 	their parents receive a great-grand child ...
			Not used by default (see 'updateChildren')
		"""
		parent.addDescendant(child, 1)
		for Ascendant in self.members:
			g = Ascendant.generationalGap(parent)
			if g:
				Ascendant.addDescendant(child, g+1)

	def updateChildren(self, parent, child):
		""" Simplified version of 'updateDescendants': only nuclear families are considered
			(people can only have children, not grand-children, etc.)
		"""
		parent.addDescendant(child, 1)

	def reproduction(self):
		""" reproduction within the group
			Uses 'parenthood' (above) and 'couples' (not reproduced here)
			'couples' returns as many couples as children are to be born
		"""
		# The probability of parents to beget children depends on their rank within the group
		# (By default, Selectivity = 0 and rank is random)
		self.update_(flagRanking=True)   # updates individual ranks
		for C in self.Scenario.couples(self.ranking):
			# Making of the child
			child = Individual(self.Scenario,ID=self.free_ID(), Newborn=True)
			if child:
				child.hybrid(C[0],C[1]) # Child's DNA results from parents' DNA crossover
				child.mutate()
				child.update()  # Computes the value of genes, as DNA is available only now
				if self.Scenario.new_agent(child, C):  # Let scenario decide something about the newcomer (not used here)
						# Simplified version: only nuclear families
					self.updateChildren(C[0], child)
					self.updateChildren(C[1], child)
						# Slightly more complex version including grand-children, etc.:
					# self.updateDescendants(C[0], child
					# self.updateDescendants(C[1], child)

					self.receive(child) # Adds child to the group


class Population(EP.EvolifePopulation):
	""" Defines the population of agents
		This is the level at which 'life_game' is played
	"""

	def __init__(self, Scenario, Observer):
		" Creates a population of agents "
		EP.EvolifePopulation.__init__(self, Scenario, Observer)
		self.Scenario = Scenario

	def createGroup(self, ID=0, Size=0):
		" Calling local class 'Group' "
		return Group(self.Scenario, ID=ID, Size=Size)


#def Start(Gbl = None, PopClass = Population, ObsClass = None, Capabilities = 'PCG'):
#	if Gbl == None: Gbl = Scenario()
#	if ObsClass == None: Observer = EO.EvolifeObserver(Gbl)	# Observer contains statistics
#	Pop = PopClass(Gbl, Observer)

#	EW.Start(Pop.one_year, Observer, Capabilities=Capabilities)

if __name__ == "__main__":
	print(__doc__)
	#""" TODO: transformer en fonction appelable par le vrai """
	#############################
	# Global objects			#
	#############################
	Gbl = Scenario()
	#Start(Gbl)
	Observer = EO.EvolifeObserver(Gbl)	  # Observer contains statistics
	Pop = Population(Gbl, Observer)

	#Observer.recordInfo('Background', 'white')
	#Observer.recordInfo('FieldWallpaper', 'white')

	EW.Start(Pop.one_year, Observer, Capabilities='PCG')

	print("Bye.......")


__author__ = 'Lie and Dessalles'
