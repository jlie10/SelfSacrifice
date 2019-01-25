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
#  S_SelfSacrifice                                                           #
##############################################################################


"""	 EVOLIFE: SelfSacrifice Scenario:
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

from random import sample, choice, randint, shuffle
#from numpy.random import choice as np.choice

from Evolife.Tools.Tools import percent, chances, decrease, noise_mult
from Evolife.Scenarii.Default_Scenario import Default_Scenario
from Evolife.Ecology.Group import EvolifeGroup
#import Evolife.Ecology.Individual as EI

######################################
# specific variables and functions   #
######################################

#class EvolifeIndividual(EI.EvolifeIndividual):
#	def __init__(
#class AscendantIndividual(EI.EvolifeIndividual, Scenario):
#	" Adds descendants to Individuals"
#	def __init__(self):
#		EvolifeIndividual.__init__(self, Scenario)
#		self.descendants = []


class Scenario(Default_Scenario, EvolifeGroup):

	######################################
	# Most functions below overload some #
	# functions of Default_Scenario	  #
	######################################


	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
        """
		return ['SelfRisk', 'AffiliationInvestment', 'Exploration'] # gene sizes are read from configuration (Starter, see Genetics section)

	def selfsacrifice(self, indiv):	#Individuals are genetically programmed to self-sacrifice at a certain age
		return indiv.gene_value('SelfRisk') > self.Parameter('SacrificeThreshold') \
					& (indiv.age>((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))

	def prepare(self, indiv):
		""" defines what is to be done at the individual level before interactions
			occur - Used in 'start_game'
		"""
		#   scores are reset
		indiv.score(0, FlagSet=True)	# resetting scores

		# friendship links (lessening with time) are updated
		indiv.lessening_friendship((100 - self.Parameter('SocialLinkErosion')/100.0))

	def sacrifices(self, members):
		""" Self-sacrifice 'game':
			Heroes may self-sacrifice "for the good of the group"
            This is an honest signal: they are a hero
            Then, social affiliates of the hero have signalled their value by honoring his/her sacrifice (second order signal)
            Biological descendants of the hero are quasi-heroes: affiliation to them is also valuable (third-order signal)
		"""
		Heroes = members[:]
		#shuffle(Heroes)
		for Coward in Heroes:
			if not self.selfsacrifice(Coward): Heroes.remove(Coward)
		Heroes = sample(Heroes,min(self.Parameter('MaxSacrifiers'),len(Heroes)))
		#NbHeroes = 0
				# After a certain number of selfsacrifices, selfsacrifice is pointless
				# ALT (plus tard) : decroitre les benefices avec le nb de deja sacrifies...

		for (HeroNbr, Hero) in enumerate(Heroes):
			if self.selfsacrifice(Hero):
				#NbHeroes += 1
				for Patriot in Hero.followers: #in retrospect, the Heroes' followers are deemed patriosts (second order signal)
					Patriot.score(+ self.Parameter('PatriotismValue')\
											* percent(self.Parameter('SacrificeHeredity')))    #ALT : avec la distance d'amitie?
					#Patriot.score(+ 1/NbHeroes * self.Parameter('PatriotismValue')\
					#						* percent(self.Parameter('SacrificeHeredity')))    #ALT : avec la distance d'amitie?

				for (Desc, gen) in Hero.descendants:
					for IndirectPatriot in Desc.followers:  #third-order signal
						if IndirectPatriot.follows(Desc):
							IndirectPatriot.score(+ percent(self.Parameter('KinSelection'))**gen \
											* self.Parameter('PatriotismValue') * percent(self.Parameter('SacrificeHeredity')))
							#IndirectPatriot.score(+ 1/NbHeroes * percent(self.Parameter('KinSelection'))**gen \
							#				* self.Parameter('PatriotismValue') * percent(self.Parameter('SacrificeHeredity')))

#				self.remove_agent(Hero)
#				EvolifeGroup.remove_(EvolifeGroup, HeroNbr)					# the hero dies
				#print(type(members))
				#members.remove_(members, HeroNbr)
				#members.kill(HeroNbr)
				#print(Hero.gene_value('SelfRisk'))
				#Hero.score(-100000)
				#Hero.LifePoints = - 100000
				Hero.selfSacrifice = True
				#Hero.dead()

	def evaluation(self, indiv):
#		" Social benefit from having friends "	# cost dans interaction
#		indiv.score(- self.Parameter('SignalingCost') * indiv.gene_value('AffiliationInvestment') / 100.0)
		#BF = indiv.best_friend()
		#if BF:
		#	BF.score(+ self.Parameter('JoiningBonus'))

		""" Social benefit from having followers
		"""
		indiv.score(+ indiv.nbFollowers() * self.Parameter('JoiningBonus'))


	def partner(self, indiv, others):
		""" Selects the best memorized cooperator, if any.
	#But with a probability controlled by the gene 'AffiliationInvestment'/Exploration en fait
			another partner is randomly selected
		"""

		BF = indiv.best_friend()
		#if BF and randint(0,100) <= indiv.gene_relative_value('AffiliationInvestment'):
		if BF and randint(0,100) >= indiv.gene_relative_value('Exploration'):
			return BF
		# Exploration: a new partner is randomly chosen
		partners = others[:]	# ground copy of the list
		partners.remove(indiv)
		if BF in others:
			partners.remove(BF)
		if partners != []:
			return choice(partners)
		else:
			return None

#	def remove_agent(self, agent):
#		" action to be performed when an agent dies "
#		print(agent.ID)
#		print(agent.gene_value('SelfRisk'))
#		print(agent.gene_value('AffiliationInvestment'))

	def interaction(self, indiv, partner):
		""" Dyadic (asymetrical) signaling interaction:
			one player (indiv) signals his desire to follow another (partner)
			by offering him/her a gift.
			The gift's value and cost are controlled by indiv's genes.

			Both involve costs.
		"""

		#   First step: initial gift
		gift = percent(self.Parameter('SignalingCost') * indiv.gene_relative_value('AffiliationInvestment'))
		partner.score(noise_mult(gift,self.Parameter('Noise')))	# multiplicative noise
		#   First player pays associated cost
		cost = gift
		indiv.score(-cost)
		#   Receiver remembers who gave the gift and may accept indiv as a follower
		indiv.F_follow(0, partner, gift)


#Version inutile ? Avec Signallers etc.
#	def interaction(self, indiv, Signallers):
#		if Signallers == []:	return
#		# The agent chooses the best available Signaller from a sample.
#		OldFriend = indiv.best_friend()
#		Signallers.sort(key=lambda S: S.gene_value('AffiliationInvestment'), reverse=True)
#		for Signaller in Signallers:
#			if Signaller == indiv:	continue
#			if OldFriend and OldFriend.gene_value('AffiliationInvestment') >= Signaller.gene_value('AffiliationInvestment'):
#				break	# no available interesting signaller
			#if Signaller.accepts(0) >= 0:
#			if 1 > 0:
				# cool! Self accepted as fan by Signaller.
#				if OldFriend is not None and OldFriend != Signaller:
#					indiv.quit_(OldFriend)
#				indiv.follow(0, Signaller, Signaller.gene_value('AffiliationInvestment'))
#				break

	def new_agent(self, child, parents):
		" initializes newborns - parents==None when the population is created"
		if parents:
			parents[0].descendants.append((child,1))
			parents[1].descendants.append((child,1))
		return True

	def end_game(self, members):
		self.sacrifices(members)

	def lives(self, members):
		" converts scores into life points "
		if self.Parameter('SelectionPressure') == 0:
			return
		if len(members) == 0:
			return
		BestScore = max([i.score() for i in members])
		MinScore = min([i.score() for i in members])
		if BestScore == MinScore:	return
		for indiv in members:
			if indiv.selfSacrifice == True:
				indiv.LifePoints = -1			#Ca les tue bien ca ?
			else:	# translating scores to zero and above
				indiv.LifePoints = (self.Parameter('SelectionPressure') \
								* (indiv.score() - MinScore))/float(BestScore - MinScore)
		return



#V2 pour rien
#	def life_game(self, members):
#		""" SelfSacrifice and Honoring (Affiliation) game
#		"""
#		# First: make initializations
#		self.start_game(members)
#		# Then: play multipartite games: interaction(Affiliation) and sacrifices
#		for Run in range(self.Parameter('NbInteractions')):
#			Fan = np.choice(members)
#			self.interaction(Fan, sample(members, self.Parameter('SampleSize')))
#
#		self.sacrifices(members)
#		# Lastly: work out
#		self.end_game(members)
#		for indiv in members:
#			self.evaluation(indiv)
#		# scores are translated into life points
#		self.lives(members)


# pour plus tard ??
	def update_descendants(self, members):	#adds grandchildren, greatgrandchildren...
		for A in members:
			for D in members:
				if D in A.descendants:
					for (grandchild, gen) in D.descendants:
						A.descendants.append((grandchild,gen+1))

	def update_positions(self, members, start_location):
		""" locates individuals on an 2D space
		"""
		# sorting individuals by gene value
		duplicate = members[:]
		duplicate.sort(key=lambda x: x.gene_value('SelfRisk'))
		for m in enumerate(duplicate):
			m[1].location = (start_location + m[0], m[1].gene_relative_value('AffiliationInvestment'))

	# def default_view(self):	return ['Network']

	def display_(self):
		""" Defines what is to be displayed. It offers the possibility
			of plotting the evolution through time of the best score,
			the average score, and the average value of the
			various genes defined on the DNA.
			It should return a list of pairs (C,X)
			where C is the curve colour and X can be
			'best', 'average', any gene name as defined by genemap
			or any phene name as dedined by phenomap
		"""
		#return [(2,'Cooperativeness'),(3,'Exploration'),(4,'average'),(5,'best')]
		return [('green','SelfRisk'),('blue','AffiliationInvestment')]

	# def remove_agent(self, agent):
		# " action to be performed when an agent dies "
		# print('removing', agent.ID)
		# pass


###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')