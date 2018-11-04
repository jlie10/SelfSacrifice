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
Social (and intricate ?) version: purely social game with fixed PopSize,
signaller signals on behalf of his/her descendants.
Descendants form bonds based on these signals.
Alignement of interests (kin selection) between Ascendants and Descendants is mediated by social Points
"""

from time import sleep
from random import sample, randint, shuffle, random
from numpy.random import choice

import sys
sys.path.append('../../..')

import SocialSimulation as SSim
# import Evolife.Scenarii.Default_Scenario as DS
# import Evolife.Ecology.Individual as EI
# import Evolife.Ecology.Group as EG
from Evolife.Tools.Tools import percent, chances, decrease

#class ReproductionScenario(DS.Default_Scenario):
#	def __init__(self):
#		DS.Default_Scenario.__init__(self, 'Default scenario', 'Evolife.evo')

class Observer(SSim.Social_Observer):
	def Field_grid(self):
		" initial draw: here a blue line "
		return [(0, 0, 'blue', 1, 100, 100, 'blue', 1), (100, 100, 1, 0)]

class Individual(SSim.Social_Individual):
	"   class Individual: defines what an individual consists of "

	def __init__(self, IdNb, maxQuality=100, parameters=None):
		# Learnable features
		Features = {'SignalInvestment': 0 }   # propensity to self-sacrifice on a scale from 0 to 100
		self.Sacrifice = False
#		self.SacrificePropensity = 0
		self.SignalLevel = 0
		self.MinFriendSignalLevel = 100
		self.BestSacrifice = 0	# best sacrifice propensity value in memory
		SSim.Social_Individual.__init__(self, IdNb, features=Features, maxQuality=maxQuality, parameters=Gbl)
		self.Descendants = Descendants()
#		EI.EvolifeIndividual.__init__(self, ReproductionScenario(), IdNb, Newborn = True)
		self.Points = 0

	def Reset(self):		# called by Learner when born again
		self.Descendants = Descendants()
		SSim.Social_Individual.Reset(self)
		self.SignalLevel = 0
		self.Points = 0
		self.update() #debug?

	def update(self, infancy=True):
		"	updates values for display "
		Colour = 'brown'
		if infancy and not self.adult():	Colour = 'pink'
		# self.SignalLevel = percent(self.Features['SignalInvestment'] * self.Quality)

#		self.Sacrifice = self.SelfSacrifice(percent(self.Features['SignalInvestment']))

		#if not self.Sacrifice:					#TEST => BR reste à 0 mais pas SignalInvest ... pq meurent pas ?
		#	BR = self.bestRecord()
		#	if BR:	self.BestSacrifice = BR[0]['SignalInvestment'] * self.Quality / 100.0			#avec ou sans la qualité ??
		#	else:	self.BestSacrifice = 0
		# self.Position = (self.id, self.Features['SignalInvestment'], Colour)
		#self.Position = (self.Quality, self.BestSacrifice+1, Colour, -1)	# -1 == negative size --> logical size instead of pixel
		#if Gbl.Param('Links') and self.best_friend():
		#	self.Position += (self.best_friend().Quality, self.best_friend().BestSacrifice+1, 21, 1)
		self.Position = (self.Quality, self.SignalLevel+1, Colour, -1)	# -1 == negative size --> logical size instead of pixel
		if Gbl.Param('Links') and self.best_friend():
			self.Position += (self.best_friend().Quality, self.best_friend().SignalLevel+1, 21, 1)


	def SignallingPotential(self, Feature=None, Transparent=False):
		""" returns an individual's signalling potential
			if an agent decides to self-sacrifice, this potential is passed on
			as a signal for the benefit of its descendants (see sacrifices)
		"""
		if Transparent: return self.Quality
		BC = Gbl.Param('BottomCompetence')
		Competence = percent(100-BC) * self.Quality + BC
		return self.Limitate(Competence, 0, 100)

	def SelfSacrifice(self, p):
		" an agent decides to make the ultimate sacrifice"
		return choice([False,True],None,False,[p,1-p])		# proba p of dying
#		return (p>0)										# any SignalInvestment results in death
#		return (p>0.1)								# test non concluant
#		return (p>0.1) or choice([False,True],None,False,[p,1-p])		# lissage ?

	def Interact(self, Signallers):
		if Signallers == []:	return
		# The agent chooses the best available Signaller from a sample.
		OldFriend = self.best_friend()
		Signallers.sort(key=lambda S: S.SignalLevel, reverse=True)
		for Signaller in Signallers:
			if Signaller == self:	continue
			if OldFriend and OldFriend.SignalLevel >= Signaller.SignalLevel:
				break	# no available interesting signaller
			if Signaller.followers.accepts(0) >= 0:
				# cool! Self accepted as fan by Signaller.
				if OldFriend is not None and OldFriend != Signaller:
					self.G_quit_(OldFriend)
				self.F_follow(0, Signaller, Signaller.SignalLevel)
				break

	def riskTaken(self):
#		return self.Features['SignalInvestment'] * (Gbl.Param('EnvironmentalRiskiness') / 100.0)
#		return self.Features['SignalInvestment']
		return self.Features['SignalInvestment'] * max(self.Points,1)
#		if self.SelfSacrifice(percent(self.Features['SignalInvestment'])): return 100
#		else: return 0

	def assessment(self):
		" Social benefit from having friends and descendants "		#Descendant benefit not needed?
		self.Points -= self.riskTaken()
		if self.best_friend() is not None:
			self.best_friend().Points += Gbl.Param('JoiningBonus')
		for (D, g) in self.Descendants:
			self.Points += (( Gbl.Param('KinSelection')/100.0 )**g) * D.Points

	def isDesc(self, Indiv):
		if Indiv in self.Descendants: return True
		return False

	def __str__(self):
		return "%s[%0.1f]" % (self.id, self.SignalLevel)

class Descendants:
	"  defines an individual's descendants, paired with the 'generational gap' (e.g. 2 for a grandchild)  "

	def __init__(self):
		self.members = []
		self.nbDescendants = 0

	def nbDescendants(self): return len(self.members)

#	def loss(self, deadDesc):
#		" an individual loses a descendant "
#		for (M,gen) in self.descendants()
#			if M == deadDesc:
#				self.descendants.remove((deadDesc,gen))
#				return True
#		print('dead: %s' % str(deadDesc))
#		error('Descendants: alive descendant attempting to quit a club')
#		return False

	def new_child(self, child, gen = 1):
		self.members.append((child,gen))
		self.nbDescendants +=1

	def __iter__(self):	return iter(self.members)


class Population(SSim.Social_Population):
	" defines the population of agents "

	def __init__(self, parameters, NbAgents, Observer, IndividualClass=Individual):
		" creates a population of agents "
		SSim.Social_Population.__init__(self, Gbl, NbAgents, Observer, IndividualClass=IndividualClass)
		self.AdoptionRanking = []		#ranking used for adoption

	def interactions(self):
		for Run in range(Gbl.Param('NbInteractions')):
			Fan = choice(self.Pop)
			# Fan chooses from a sample
			Fan.Interact(sample(self.Pop, Gbl.Param('SampleSize')))

	def adoptRanking(self):				# hypo: points also earn adoption rights
		self.AdoptionRanking = self.Pop[:]	  # duplicates the list, not the elements
		for indiv in self.AdoptionRanking:
			if not indiv.adult():
				self.AdoptionRanking.remove(indiv)	# children cannot adopt
		shuffle(self.AdoptionRanking)			# so as to randomize among individuals with the same number of points
		self.AdoptionRanking.sort(key=lambda x: x.Points,reverse=True)

	def simpleAdoption(self):			# n'est pas utilisee
		""" simple (test) adoption: 2 among the best scores get an adoptive child
			like below, an adopted child is a random reset individual
		"""
		self.adoptRanking()
		M = self.AdoptionRanking[0]
		F = self.AdoptionRanking[1]
		C = choice(self.AdoptionRanking[2:])
		C.Reset()
		M.Descendants.new_child(C)
		F.Descendants.new_child(C)

		for A in self.Pop:			# adds grandchildren, greatgrandchildren etc.
			if A.isDesc(M):
				for (grandchild, gen) in M.Descendants:
					A.Descendants.new_child(grandchild, gen+1)
			if A.isDesc(F):
				for (grandchild, gen) in F.Descendants:
					A.Descendants.new_child(grandchild, gen+1)

	def parenthood(self, RankedCandidates, Def_Nb_Children):
		" Determines the number of children depending on rank "
		candidates = [[m,0] for m in RankedCandidates]
		# parenthood is distributed as a function of the rank
		# it is the responsibility of the caller to rank members appropriately
		# Note: reproduction_rate has to be doubled, as it takes two parents to beget a child
		for ParentID in enumerate(RankedCandidates):
			candidates[ParentID[0]][1] = chances(decrease(ParentID[0],len(RankedCandidates),self.Param('Selectivity')), 2 * Def_Nb_Children)
		return candidates

	def parents(self, candidates):
		"""	Selects one couple from candidates.
			Candidates are (indiv, NbChildren) couples, where NbChildren indicates the number of
			children that indiv can still have
		"""
		try:
			return sample(candidates, 2)
		except ValueError:	return None

	def couples(self, members, nb_children=-1):
		""" Returns a set of couples that will beget (adopt) newborns
			Note that a given individual may appear several times
			By default, the probability for an individual to be in a
			couple (and thus to have a child) decreases with its rank
		"""
		if nb_children < 0:		# the number of children may be imposed (e.g. in s_gazelle)
			nb_children = chances(self.Param('ReproductionRate') / 100.0, len(members))
		candidates = self.parenthood(members, nb_children)
		Couples = []
		for ii in range(nb_children):
			Couple = self.parents([p for p in candidates if p[1] > 0])	# selects two parents from the list of candidates
			if Couple:
				(mother, father) = Couple
				Couples.append((mother[0],father[0]))
				mother[1] -= 1
				father[1] -= 1
			else:	break
		return Couples

	def adoption(self):
		""" adoption within the population: parents adopt a child, who is a reinitialized social individual
			updates individuals' descendants list
			reproduction_rate is expected in %
		"""
		self.adoptRanking()
		nbAdopters = chances(self.Param('ReproductionProbability') / 100.0, len(self.AdoptionRanking))
		Adopters = self.AdoptionRanking[:nbAdopters]		# adoption semble 'aller tp vite'
		for C in self.couples(Adopters):
			# making of the child: a random social individual is reset to become this child
			availablePop = self.Pop[:]  	# duplicates the list, not the elements
			availablePop.remove(C[0])
			availablePop.remove(C[1])
			child = choice(availablePop)
			child.Reset()
			C[0].Descendants.new_child(child)
			C[1].Descendants.new_child(child) # adds the child to both parents' descendants

			for A in self.Pop:			# adds grandchildren, greatgrandchildren etc.
				if A.isDesc(C[0]):
					for (grandchild, gen) in C[0].Descendants:
						A.Descendants.new_child(grandchild, gen+1)
				if A.isDesc(C[1]):
					for (grandchild, gen) in C[1].Descendants:
						A.Descendants.new_child(grandchild, gen+1)

	def sacrifices(self):
		""" plays the self-sacrifice 'game':
			agents can self-sacrifice and are reset
			in this case, they emit a signal on behalf of their descendants
			whose value depends on the number of generations seperating them
		"""
#		for (rank, Ascendant) in enumerate(self.Pop):
#			if Ascendant.Sacrifice == True:
#				for (Desc,gen) in Ascendant.Descendants:
#					Sgn = int(Ascendant.SignallingPotential(True)//(2**gen)) 	#Self-sacrifice is defined as an honest signal
#					Desc.SignalLevel = Desc.Limitate(Sgn,0,100)
#				self.kill(rank)

		for Ascendant in self.Pop:
			if Ascendant.SelfSacrifice(percent(Ascendant.Features['SignalInvestment'])):
#				Ascendant.Points -= 100
				for (Desc, gen) in Ascendant.Descendants.members:
					Sgn = Ascendant.SignallingPotential(True)*((self.Param('SignalHeredity')/100.0)**gen)	 #Self-sacrifice is defined as an honest signal
					if not Ascendant.adult():
						Sgn = (self.Param('InfantSacrificeValue')/100.0) * Sgn					# child sacrifice is less effective
					Desc.SignalLevel = Desc.Limitate(Sgn,0,100)
				Ascendant.Reset()					# "death" of the social individual

	def season_initialization(self):
		for agent in self.Pop:
			# agent.lessening_friendship()	# eroding past gurus performances
			if self.Param('EraseNetwork'):	agent.forgetAll()
			agent.Points = 0

	def Dump(self, Slot):
		""" Saving self-sacrifice propensity in signalling for each adult agent
			and then distance to best friend for each adult agent having a best friend
		"""
		if Slot == 'SignalInvestment':
			D = [(agent.Quality, "%2.03f" % agent.Features[Slot]) for agent in self.Pop]

		elif Slot == 'DistanceToBestFriend':
			D = [(agent.Quality, "%d" % abs(agent.best_friend().Quality - agent.Quality)) for agent in self.Pop if agent.adult() and agent.best_friend() is not None]
			D += [(agent.Quality, " ") for agent in self.Pop if agent.best_friend() == None or not agent.adult()]
		else:
			D = [(agent	.Quality, "%2.03f" % agent.Features[Slot]) for agent in self.Pop]
		return [Slot] + [d[1] for d in sorted(D, key=lambda x: x[0])]

	def One_Run(self):
		# This procedure is repeatedly called by the simulation thread
		# ====================
		self.Obs.season()	# increments year
		self.display()
		# ====================
		# Interactions
		# ====================
		for Run in range(self.Param('NbRunPerYear')):
			self.season_initialization()
#			if Run == self.Param('NbRunPerYear'):		# only one life-threatening event per year
#				self.sacrifices()
			SacrificeEvent = (random() < self.Param('EnvironmentalRiskiness') / 100.0)
			if SacrificeEvent: self.sacrifices()
			self.interactions()
			self.learning()
			self.adoption()
#			if Run == 1: self.adoption() 			#(solved?) les choses vont très vite avec l'adoption partout...
#			if Run == 1: self.simpleAdoption()
		return True	# This value is forwarded to "ReturnFromThread" (see SocialSimulation)


if __name__ == "__main__":
	Gbl = SSim.Global()
	SSim.Start(Params=Gbl, PopClass=Population, ObsClass=Observer)



__author__ = 'Dessalles et Lie'
