##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2018                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


""" Study of patriotism signaling in time of war (uncertainty about friends' patriotism)
"""

from math import log
from random import randint, random, choice, sample
from time import sleep

import sys
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Ecology.Observer	as EO
import Evolife.Scenarii.Default_Scenario as ED
import Evolife.Ecology.Individual as EI
import Evolife.Ecology.Alliances as EA
import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.QtGraphics.Evolife_Batch  as EB
import Evolife.Ecology.Group as EG
import Evolife.Ecology.Population as EP

from Evolife.Tools.Tools import percent


class Scenario(ED.Default_Scenario):

########################################
#### General initializations and visual display ####c
########################################
    def __init__(self):
        # Parameter values
        ED.Default_Scenario.__init__(self, CfgFile='_Params.evo')	# loads parameters from configuration file
        self.initialization()

    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('Patriot'), ('NonPatriot'), ('Demand')] 		# gene length (in bits) is read from configuration

    def phenemap(self):
        """ Defines the set of non-inheritable characteristics
        """
        return ['Patriotism']
    
    def display_(self):
        return [('blue', 'Patriot', 'signal level if patriot'), 
                 ('green', 'Demand', 'signal level expected from acquaintances'),
                 ('red', 'NonPatriot', 'signal level if non-patriot'),
                 ]

    def update_positions(self, members, groupLocation):
        """ locates individuals on an 2D space
        """
        for indiv in members:	
            indiv.location = (groupLocation + indiv.Phene_value('Patriotism'), 
                # indiv.score(), 'blue', 6)
                indiv.signal(), 'blue', 6)

    def Field_grid(self):	
        return [(0, 98, 'green', 1, 100, 98, 'green', 1), (100, 100, 1, 0)]

    #def update_positions(self, members, start_location):
        """ locates individuals on an 2D space
        """
        # sorting individuals by gene value
    #    duplicate = members[:]
     #   duplicate.sort(key = lambda x: x.Patriotism)
     #   for m in enumerate(duplicate):
            #m[1].location = (start_location + m[0], m[1].score() )
            #m[1].location = (start_location + m[0], m[1].Reproductive_points )
            #m[1].location = (start_location + m[0], m[1].Share )
            #m[1].location = (start_location + m[0], m[1].LifePoints)
            #m[1].location = (start_location + m[0], m[1].HeroesRelatedness)
      #      m[1].location = (start_location + m[0], m[1].signal())

########################################
##### Life_game #### (1) Initializations ####
########################################
    def prepare(self, indiv):
        """ Defines what is to be done at the individual level before interactions
            occur - Used in 'start_game'
        """
        indiv.score(100, True)  # Set initial score to 100
        
        #max = self.Parameter('MaxOffer')
        #indiv.score( max + indiv.Patriotism * (100 - max), FlagSet = True)	# Sets score to 10 or 90
        # = super bad idea... (rel score -> +++ cool have friends)

        # friendship links (lessening with time) are updated 
        indiv.lessening_friendship((100 - self.Parameter('Erosion'))/100.0)

########################################
##### Life_game #### (3) Social interactions ####
########################################

    def interaction(self, indiv, partner):
        " Interaction between individuals "
        PartnerOffer = partner.signal()
        Offer = indiv.signal()
        if PartnerOffer >= indiv.demand() and Offer >= partner.demand():
            #if partner.followers.accepts(0) >= 0:
            #    indiv.F_follow(Offer, partner, PartnerOffer)
            indiv.acquainted(partner)
    
########################################
##### Life_game #### (4) Computing scores and life points ####
########################################
    
    def evaluation(self, indiv):
        
        
        #print('indiv has {} friends'.format(indiv.nbFriends()))   
        #print('indiv has {} friends and {} followers'.format(indiv.nbFriends(), indiv.nbFollowers()))   
        
        if indiv.nbFollowers() == 0:
            # indiv is alone in the world
            self.alone(indiv, penalty = self.Parameter('AlonePenalty'))
        else:
            indiv.score( + self.Parameter('JoiningBonus') * indiv.nbFollowers() )   # 0 by default
            # Sert vraiment a rien en principe...
        
        for follower in indiv.followers:
            follower.score(+ self.Parameter('FriendshipValue'))
            # Friendship is beneficial no matter what


        if not indiv.patriot() ==0 and random() < percent(self.Parameter('NbTraitors')):
            # indiv is a traitor who betrays its friends
            for follower in indiv.followers:
                self.betrayed(follower, cost = self.Parameter('DenunciationCost'))
                indiv.score(+ self.Parameter('Judas')) 

        elif indiv.patriot():
            # indiv is a true patriot : bonus (0 by default)
            for follower in indiv.followers:
                follower.score(+ self.Parameter('PatriotFriendBonus'))     
        
        return

    def betrayed(self, indiv, cost = 100):
        if cost == 0:
            indiv.Executed = True
        indiv.score( - cost)

    def alone(self, indiv, penalty = 200):
        if penalty == 0:
            indiv.Executed = True
        indiv.score( - penalty)

    def lives(self, members):
        """ Converts alive members' scores into life points - used in 'life_game'
        """
        if self.Parameter('EraseNetwork'): self.reinitialize_network(members)
        #alivemembers1 = self.social_death(members, Spare=self.Parameter('DenunciationCost'))
        #AliveMembers = self.social_death(alivemembers1, Spare=self.Parameter('AlonePenalty'))
        AliveMembers = members      # Version without death for now...
        if self.Parameter('SelectionPressure') == 0:
            return
        if not AliveMembers:
            return
        BestScore = max([i.score() for i in AliveMembers])
        MinScore = min([i.score() for i in AliveMembers])
        if BestScore == MinScore:
            return
        for indiv in members:
            indiv.LifePoints =  int ( (indiv.score()-MinScore) * self.Parameter('SelectionPressure') / (BestScore - MinScore) )
            #print(indiv.LifePoints)
            #print(indiv.score() )
            #print(indiv.Patriotism)
            #print('\n')

    def social_death(self, members, Spare=True):
        if Spare: return members
        AliveMembers = members[:]
        for i in members:
            if i.Executed:
                AliveMembers.remove(i)
                i.LifePoints = -1
        return AliveMembers

    def reinitialize_network(self, members):
        for i in members:
            i.forgetAll()


    def lives_10(self, members):
        AliveMembers = members[:]
        for i in members:
            if i.Executed:
                AliveMembers.remove(i)
                i.LifePoints = -1
        if self.Parameter('SelectionPressure') == 0:
            return	# 'Selectivity mode' : outcomes depend on relative ranking  (see 'parenthood')
        if not members:
            return
        BestScore = max([ int (i.score() / 10) for i in members])
        MinScore = min([ int (i.score() /10) for i in members])
        if BestScore == MinScore:
            return
        for indiv in members:
            indiv.LifePoints =  (int ( indiv.score() / 10) -MinScore) * self.Parameter('SelectionPressure') / (BestScore - MinScore)
            #print(indiv.LifePoints)
            #print(indiv.Share)
            #print('\n')

########################################
########################################
########################################

class Patriotic_Individual(EI.EvolifeIndividual, EA.Follower):
    "   Individuals have a patriotism phenotype "

    def __init__(self, Scenario, ID, maxPatriotism = 100, Newborn=True):
        #self.IdNb = int( ID[2:]	)	# ID is constructed as Groupnumber_IdNb - there is always only 1 group
        # self.Patriotism = randint(0, 1)

        #self.Offerings = 0		# represents how much one is honored after self-sacrifice (should stay at 0 whilst alive)
        self.SignalLevel = -1
        #self.VisibleSignal = 0
        self.Executed = False
        # self.BestSignal = 0
        EI.EvolifeIndividual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
        EA.Follower.__init__(self, self.Scenario.Parameter('MaxFriends'), Scenario.Parameter('MaxFriends'))
        #EA.Friend.__init__(self.Scenario.Parameter('MaxFriends'))  # WHY DOESN'T WORK ?

    def patriot(self):
        return self.Phene_value('Patriotism') > 100 - self.Scenario['PatriotRatio']

    def signal(self):
        " computes signal level "
        sgl = 0
        if self.SignalLevel < 0:
            if self.patriot():	
                sgl = self.gene_relative_value('Patriot')
                self.signalCost(sgl)
            else:
                sgl = self.gene_relative_value('NonPatriot')
                if self.Scenario.Parameter('DifferentialCosts') == 0: # version offre bornee
                    self.signalCost(sgl)
                    sgl = min(self.Scenario.Parameter('MaxOffer'), sgl)
                       # can't offer that much : face already tatooed, arm already cut off...
                        # TRICHE faire ca apres le cout ? +++++ REFLECHIR
                else:
                    self.signalCost(sgl, DifferentialCosts = True)
            self.SignalLevel = int( sgl / self.Scenario.Parameter('VisibleThreshold')) * self.Scenario.Parameter('VisibleThreshold')
        return self.SignalLevel

    def signalCost(self, sgl, DifferentialCosts = False, patriotism = 0):
        basic_cost = sgl * percent(self.Scenario.Parameter('HonoringCost'))
        if not DifferentialCosts:
            #print('Offer max')
            self.score( - basic_cost)
        else:   # NonPatriots face a premium for honoring
            #print('diff cost')
            self.score (- basic_cost + basic_cost * (1 - patriotism) * percent(self.Parameter('DishonestPremium')))
            # NonPatriots face a premium for honoring
    
    def demand(self):
        return self.gene_relative_value('Demand')

class Group(EG.EvolifeGroup):
    " In each group, patriotism ranges from 0 to group size (simplification) "

    def __init__(self, Scenario, ID=1, Size=100):
        EG.Group.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        # calling local class 'Individual'
        Indiv = Patriotic_Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
        # Individual creation may fail if there is no room left
        self.Scenario.new_agent(Indiv, None)  # let scenario know that there is a newcomer (unused)
        #if Indiv.location == None:	return None
        return Indiv

class Patriotic_Population(EP.EvolifePopulation):
    """ Defines the population of agents
    """

    def __init__(self, Scenario, Observer):
        " Creates a population of agents "
        EP.EvolifePopulation.__init__(self, Scenario, Observer)
        self.Scenario = Scenario

    def createGroup(self, ID=0, Size=0):
        " Calling local class 'Group' "
        return Group(self.Scenario, ID=ID, Size=Size)


def Start(Gbl = None, PopClass = Patriotic_Population, ObsClass = None, Capabilities = 'FGCNP'):
    " Launch function "
    if Gbl == None: Gbl = Scenario()
    if ObsClass == None: Observer = EO.EvolifeObserver(Gbl)	# Observer contains statistics
    Pop = PopClass(Gbl, Observer)
    BatchMode = Gbl.Parameter('BatchMode')

    if BatchMode:
        EB.Start(Pop.one_year, Observer)
    else:
        EW.Start(Pop.one_year, Observer, Capabilities=Capabilities)
    if not BatchMode:	print("Bye.......")
    sleep(2.1)	
    return


if __name__ == "__main__":
    print(__doc__)

    #############################
    # Global objects			#
    #############################
    Gbl = Scenario()
    Start(Gbl)