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
Simplified 'first-step' (base) version where Admiration is automatic/exogenous
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

from Evolife.Tools.Tools import percent, chances, decrease, error

class Scenario(ED.Default_Scenario):

########################################
#### General initializations and visual display ####
########################################
	def __init__(self):
		# Parameter values
		ED.Default_Scenario.__init__(self, CfgFile='_Params.evo')	# loads parameters from configuration file

	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
        """
		return [('SelfSacrifice')] 		# gene length (in bits) is read from configuration

	def display_(self):
		return [('red', 'SelfSacrifice')]
		#return[('red','SelfSacrifice'), (('yellow', 'average'), ('black', 'best')]
		#Best and/or average scores can also be displayed

########################################
##### Life_game ####
########################################
	def life_game(self, members):
		""" Defines one year of play (outside of reproduction)
			This is where individual's acquire their score
		"""
		# First: make initializations (1)
		self.start_game(members)
		# Then: play multipartite game, composed of:
			# The sacrifices game (2):
		self.sacrifices(members, self.Parameter('MaxHeroes'))
			# Social interactions between the living (3)
		self.interactions(members, self.Parameter('Rounds'))
		# Last: work out final tallies (4)
		for indiv in members:
			self.evaluation(indiv)
		# Scores are translated into life points, which affect individual's survival
		self.lives(members)

#		for i in members:
#			print(i.score())
#			print(i.LifePoints)
#			print('\n')

########################################
##### Life_game #### (1) Initializations ####
########################################
	def prepare(self, indiv):
		""" Defines what is to be done at the individual level before interactions
			occur - Used in 'start_game'
		"""
		indiv.score(0, FlagSet = True)	# Sets score to 0
		indiv.Admiration = 0
		indiv.SelfSacrifice = False

	def start_game(self, members):
		""" Defines what is to be done at the group level each year
			before interactions occur - Used in 'life_game'
		"""
		for indiv in members:	self.prepare(indiv)

########################################
##### Life_game #### (2) Self-sacrifices ####
########################################
			## (2a) Individual propensity to self-sacrifice
	def deathProbability(self, indiv):
		""" Converts an individual's genetic propensity to self-sacrifice into a probability
			Used in 'selfSacrifice'
		"""
		maxvalue = 2 **	self.Parameter('GeneLength') - 1
		return (indiv.gene_value('SelfSacrifice') / maxvalue)

	def selfSacrifice(self, indiv):
		""" An agent decides to make the ultimate sacrifice
			Self-Sacrifice is only a possibiltiy from a certain age (e.g. adulthood)
			and is controlled by the SelfSacrifice gene (see deathProbability)
			Used in 'sacrifices'
		"""
		p = self.deathProbability(indiv)
		## 'Probablistic' mode:
		bool = p > random() and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))

		## 'Binary mode': (Individuals are programmed to self-sacrifice at a certain age)
		#bool = p > 0 and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))
		indiv.SelfSacrifice = bool
		return bool

########################################
			## (2b) Population-level self-sacrifice game
	def sacrifices(self, members, max_heroes=100):
		""" Self-sacrifice 'game':
			Heroes may self-sacrifice "for the good of the group"
			In return they are admired - admiration is exogenous here
			Used in 'life_game'
		"""
		Heroes = []
		Cowards = members[:]
		for i in range(min(max_heroes,len(members))):
			Potential_Hero = choice(Cowards)
			if self.selfSacrifice(Potential_Hero):
				Heroes.append(Potential_Hero)
				Cowards.remove(Potential_Hero)
		# In return, heroes are honored (admired) by society
		self.honoring(Cowards, Heroes)

	def honoring(self, patriots, heroes):
		""" Honoring of heroes - exogenous here
			Determines total social admiration heroes will 'compete' over (see 'honoring')
			Used in 'sacrifices'
		"""
		# Admiration is a social constant, proportional to the size of the population
		social_admiration = self.Parameter('Admiration')*self.Parameter('PopulationSize')
		# social_admiration = self.Parameters('Admiration')*len(patriots)	# Variant
		self.pantheon(heroes, social_admiration, self.Parameter('HeroCompetivity'))

	def pantheon(self, heroes, social_admiration = 0, competivity_ratio = 100):
		""" Heroes 'compete' for admiration
			(They have no control over which share of the pie they will receive)
			Used in 'honoring'
		"""
		if not heroes:
			return
		equa = 1 - competivity_ratio / 100.0
		if equa == 1:	# The pantheon is equalitarian
			tot_weights = len(heroes)
		elif equa >= 0 and equa < 1:
			tot_weights = (1-(equa)**len(heroes)) / (1 - equa)	# Geometric sum
		else:
			error('competivity_ratio must be between 0 and 100')
		best_weight = 1 / tot_weights
		for Hero in heroes:
			Hero.Admiration = best_weight * social_admiration
			best_weight = equa * best_weight

########################################
##### Life_game #### (3) Social interactions ####
########################################
	def interactions(self, members, nb_interactions = 1):
		"""	Defines how the (alive) population interacts
			Used in 'life_game'
		"""
		for Run in range(nb_interactions):
			Fan = choice(members)
			# Fan chooses friends from a sample of Partners
			Partners = self.partners(Fan, members, int(percent(self.Parameter('SampleSize')\
																	* (self.Parameter('PopulationSize')-1) )))
			self.interact(Fan, Partners)

	def interact(self, indiv, partners):
		""" Nothing by default - Used in 'interactions'
		"""
		pass

	def partners(self, indiv, members, sample_size = 1):
		""" Decides whom to interact with - Used in 'interactions'
			By default, a sample of partners is randomly chosen
		"""
		# By default, a partner is randomly chosen
		partners = members[:]
		partners.remove(indiv)
		if sample_size > self.Parameter('PopulationSize'):
			error('SampleSize is too large (should be between 0 and 100)')
		if sample_size > len(partners):
			print(len(partners))
			return partners
			#error('SampleSize is too large (should be between 0 and 100)')
		if partners != []:
			return sample(partners, sample_size)
		else:
			return None

########################################
##### Life_game #### (4) Computing scores and life points ####
########################################
	def evaluation(self, indiv):
		""" Implements the computation of individuals' scores
			Used in 'life_game'
		"""
		if indiv.SelfSacrifice:
			#self.spillover(indiv, self.Parameter('Admiration'), percent(self.Parameter('KinSelection')))
			self.spillover(indiv, indiv.Admiration, percent(self.Parameter('KinSelection')))

	def spillover(self, Hero, admiration = 0, kin_transfer = 0.5):
		""" A hero's descendants benefit from his or her sacrifice,
			proportionally to how much he or she is honored / admired
			and depending on how close they are to the hero in the family tree
			Used in 'evaluation'
		"""
		tot_benef = percent(admiration * self.Parameter('SacrificeHeredity'))
		# Some admiration is 'lost' for descendants (the goat is eaten without them, people they will never meet talk about the heroes' values...)
		if not Hero.Descendants:
			return	# Hero has no descendants for 'admiration' to spillover to
		tot_weights = 0
		for (Desc, gen) in Hero.Descendants:
			tot_weights += (kin_transfer)**gen
		for (Desc, gen) in Hero.Descendants:
			share = (kin_transfer)**gen	# share is coefficient of relatedness by default (depends on the 'KinSelection' parameter)
			Desc.score(+ share / tot_weights * tot_benef)

	def lives(self, members):
		""" Converts scores into life points - used in 'life_game'
			(Unchanged from Default_Scenario: put here for informative purposes)
		"""
		if self.Parameter('SelectionPressure') == 0:
			return	# 'Selectivity mode' : outcomes depend on relative ranking  (see 'parenthood')
		if len(members) == 0:
			return
		BestScore = max([i.score() for i in members])
		MinScore = min([i.score() for i in members])
		if BestScore == MinScore:	return
		for indiv in members:
			indiv.LifePoints = (self.Parameter('SelectionPressure') \
								* (indiv.score() - MinScore))/float(BestScore - MinScore)
		#### Variant where self-sacrifiers actually die: (not performed here)
		#if indiv.SelfSacrifice:
				#indiv.LifePoints = -1	# Individual dies
		#	else:		# Translating scores to Lifepoints above zero
		#		indiv.LifePoints = (self.Parameter('SelectionPressure') \
		#						* (indiv.score() - MinScore))/float(BestScore - MinScore)
		return

########################################
#### Reproduction ####
########################################
# Reproduction is already defined elsewhere, but some functions have to be overloaded to create local individuals
# This is the case with parenthood (here) and Group.reproduction
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

#	def remove_agent(self, descendant, members):
#		""" When an individual dies, he or she is removed from
#		ascendant's family trees
#		"""
#		for Asc in members:
#			g = Asc.generationalGap(descendant)	# None if indiv does not descend from Asc
#			if g:
#				Asc.removeDescendant(descendant, g) # removes indiv from his parents/etc family trees

########################################
########################################
########################################

class Individual(EI.EvolifeIndividual):
	"   Defines what an individual consists of "

	def __init__(self, Scenario, ID=None, Newborn=True):
		self.SelfSacrifice = False
		self.Admiration = 0
		self.Descendants = []
		EI.EvolifeIndividual.__init__(self, Scenario, ID=ID, Newborn=Newborn)

	def isDesc(self, Indiv, gen = 1):
		if (Indiv, gen) in self.Descendants: return True
		return False

	def generationalGap(self, Desc):
		""" Returns the 'generational gap' (1 for a child) if Desc descends from Individual
			Used in 'updateDescendants'
		"""
		for i in range(len(self.Descendants)):
			if self.Descendants[i][0] == Desc:
				return self.Descendants[i][1]
		return None

	def addDescendant(self, Desc, gen = 1):
		""" Adds descendants coupled with the 'generational gap' (1 for a child)
			Used in 'updateChildren' or 'updateDescendants'
		"""
		self.Descendants.append((Desc, gen))

	def removeDescendant(self, Desc, gen = 1):
		""" Removes a descendant of self
		Used when the descendant dies (see 'Group.remove_')
		"""
		if self.isDesc(Desc, gen):
			self.Descendants.remove((Desc, gen))

########################################
########################################
########################################

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

	def remove_(self, memberNbr):
		""" An individual is removed from the group
			and from his ascendant's family trees
		"""
		indiv = self.whoIs(memberNbr)
		for Asc in self.members:
			g = Asc.generationalGap(indiv)	# None if indiv does not descend from Asc
			if g:
				Asc.removeDescendant(indiv, g) # removes indiv from his parents/etc family trees
		return EG.EvolifeGroup.remove_(self, memberNbr)

	def reproduction(self):
		""" Reproduction within the group
			Uses 'parenthood' (in Scenario) and 'couples' (not reproduced here)
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

########################################
########################################
########################################

class Population(EP.EvolifePopulation):
	""" Defines the population of agents
		This is the level at which 'life_game' is played
	"""

	def __init__(self, Scenario, Observer):
		" Creates a population of agents "
		EP.EvolifePopulation.__init__(self, Scenario, Observer)
		self.Scenario = Scenario
		#self.Observer = Observer	####

	def createGroup(self, ID=0, Size=0):
		" Calling local class 'Group' "
		return Group(self.Scenario, ID=ID, Size=Size)

	def reproduction(self):
		" launches reproduction in groups "
		for gr in self.groups:
			gr.reproduction()
		#if self.popSize == 0:
		#	self.__init__(self.Scenario,self.Observer)
		#while self.popSize < self.Scenario.Parameter('PopulationSize'):
		#	for gr in self.groups:
		#		gr.reproduction()
		self.update()

########################################
########################################
########################################

def Start(Gbl = None, PopClass = Population, ObsClass = None, Capabilities = 'PCG'):
	" Launch function "
	if Gbl == None: Gbl = Scenario()
	if ObsClass == None: Observer = EO.EvolifeObserver(Gbl)	# Observer contains statistics
	Pop = PopClass(Gbl, Observer)

	EW.Start(Pop.one_year, Observer, Capabilities=Capabilities)




if __name__ == "__main__":
	print(__doc__)

	#############################
	# Global objects			#
	#############################
	Gbl = Scenario()
	Start(Gbl)

	print("Bye.......")


__author__ = 'Lie and Dessalles'
