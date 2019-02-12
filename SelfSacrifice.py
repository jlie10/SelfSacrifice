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
from numpy.random import choice

import sys

import SelfSacrifice_v0 as Base
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Ecology.Alliances as EA
import Evolife.Ecology.Observer	as EO
import Evolife.QtGraphics.Evolife_Window as EW
from Evolife.Tools.Tools import percent, powerlaw

class Scenario(Base.Scenario):

########################################
#### General initializations and visual display ####
########################################
    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('SelfSacrifice'), ('Honoring')] 		# gene size is read from configuration

    def display_(self):
        return [('red', 'SelfSacrifice'), ('blue', 'Honoring')]
        #return[('red','SelfSacrifice'), ('blue', 'Honoring'), ('yellow', 'average'), ('black', 'best')]
        #Best and/or average scores can also be displayed
        
    def update_positions(self, members, start_location):
        """ locates individuals on an 2D space
        """
        # sorting individuals by gene value
        duplicate = members[:]
        #duplicate.sort(key=lambda x: x.gene_value('SelfSacrifice'))
        duplicate.sort(key=lambda x: x.gene_value('Honoring'))
        for m in enumerate(duplicate):
            #m[1].location = (start_location + m[0], m[1].gene_value('Honoring'))
            m[1].location = (start_location + m[0], m[1].Patriotism)

########################################
##### Life_game #### (1) Initializations ####
########################################
    def prepare(self, indiv):
        """ Defines what is to be done at the individual level before interactions
            occur - Used in 'start_game'
        """
        indiv.score(100, FlagSet = True)	# Sets score to 100
        indiv.SignalLevel = 0
        indiv.Admiration = 0
        #indiv.SelfSacrifice = False 	# for probabilistic mode
        #indiv.detach()	# indiv quits his/her friends
            # Done at the end of the year (evaluation) to avoid friendship with dead individuals


########################################
##### Life_game #### (2a) Self-sacrifices ####
########################################
    def honoring(self, patriots, heroes):
        """ 'Endogenous' honoring of heroes
            Total social admiration directed at heroes now depends on
            the propensity of (alive) individuals to signal their patriotism
            which is controlled by a gene
            Used in 'sacrifices'
        """
        Offerings = 0
        for Patriot in patriots:
            maxvalue = 2 **	self.Parameter('GeneLength') - 1
            offering = Patriot.gene_value('Honoring') / maxvalue * 100
            # An individual gives (his time, a valuable object, a goat...) proportionally to his or her genes
            Patriot.SignalLevel += offering
            #print(offering)
            # By doing so, a patriot signals his/her patriotism to others, which they will take into account when choosing friends
            Offerings += offering
        self.pantheon(heroes, Offerings, self.Parameter('HeroCompetivity'))

########################################
##### Life_game #### (2b) Social interactions ####
########################################
    def interact(self, indiv, Signalers):
        """ Formation of friendship bonds
            By honoring heroes (see 'honoring'), individuals signal their patriotism
            This signal is used by others to choose their friends
            (keeping in mind this is crucial: see 'evaluation')
        """
        if Signalers == []:	return
        # The agent chooses the best available Signaler from a sample.
        OldFriend = indiv.best_friend()
        Signalers.sort(key=lambda S: S.SignalLevel, reverse=True)
        for Signaler in Signalers:
            if Signaler == indiv:	continue
            if OldFriend and OldFriend.SignalLevel >= Signaler.SignalLevel:
                break	# no available interesting signaler
            if Signaler.followers.accepts(0) >= 0:
                # cool! Self accepted as fan by Signaler.
                if OldFriend is not None and OldFriend != Signaler:
                    indiv.G_quit_(OldFriend)
                indiv.F_follow(0, Signaler, Signaler.SignalLevel)
                break

########################################
##### Life_game #### (4) Computing scores and life points ####
########################################
    def evaluation(self, indiv):
        indiv.score(- self.costSignal(indiv))
        if indiv.SelfSacrifice:
            indiv.score(-1, True)	#cheat
            #print(indiv.Admiration)
            #print(indiv.score())
            #print('\n')
            self.spillover(indiv, indiv.Admiration, percent(self.Parameter('KinSelection')))
            indiv.detach()
            return	# dead individuals don't have friends
##### NEW : tentative a l'arrache ................
        if indiv.best_friend() is not None:
                if not indiv.best_friend().SelfSacrifice:
                    indiv.best_friend().score(+ self.Parameter('JoiningBonus'))

        " It's the end of the war: friends reveal themselves for who they really are "
        for Friend in indiv.friends.names():
            #print(Friend.Patriotism)
            if Friend.Patriotism < percent(self.Parameter('Traitors')*self.Parameter('PopulationSize')):
                # Friend is a traitor who sells you out
                indiv.score(- self.Parameter('DenunciationCost'))
            if Friend.Patriotism > (1-percent(self.Parameter('Patriots'))*self.Parameter('PopulationSize')):
                # Friend is a true patriot who can vouch for you
                indiv.score(+ self.Parameter('FriendshipValue'))
        #print(indiv.ID)
        #print(indiv.score())
        indiv.detach()	# indiv quits his/her friends

    def costSignal(self, indiv):
        #if self.Parameter('FixedSignalingCost') and indiv.SignalLevel > 0:
        #	return self.Parameter('SignalingCost')	# Fixed Cost mode (not prefered)
        #else:	# Proportional cost mode (prefered)
        #	return percent(indiv.SignalLevel * self.Parameter('SignalingCost'))
        cost = indiv.SignalLevel * (1 - percent(indiv.Patriotism))
        cost = cost * percent(self.Parameter('SignalingCost'))
        #print(cost)
        return cost
        #return percent(indiv.SignalLevel * self.Parameter('SignalingCost'))


class Patriotic_Individual(Base.Individual, EA.Follower):
    "   Individuals now also have a patriotism phenotype "

    def __init__(self, Scenario, ID, maxPatriotism = 100, Newborn=True):
        self.IdNb = int( ID[2:]	)	# ID is constructed as Groupnumber_IdNb - there is always only 1 group
        self.Patriotism = (100.0 * self.IdNb) / maxPatriotism
        Base.Individual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
        #self.Offerings = 0		# represents how much one is honored after self-sacrifice (should stay at 0 whilst alive)
        self.SignalLevel = 0
        # self.BestSignal = 0
        EA.Follower.__init__(self, Scenario.Parameter('MaxFriends'), Scenario.Parameter('MaxFriends'))

    # TODO : + update / display ---> rpz graphique 2d avec Patriotism

class Group(Base.Group):
    " In each group, patriotism ranges from 0 to group size (simplification) "

    def __init__(self, Scenario, ID=1, Size=100):
        Base.Group.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        # calling local class 'Individual'
        Indiv = Patriotic_Individual(self.Scenario, ID=self.free_ID(), maxPatriotism = self.Scenario.Parameter('PopulationSize'), Newborn=Newborn)
        # Individual creation may fail if there is no room left
        self.Scenario.new_agent(Indiv, None)  # let scenario know that there is a newcomer (unused)
        #if Indiv.location == None:	return None
        return Indiv

    def reproduction(self):
        """ Reproduction within the group (see SelfSacrifice_v0) for details
            Calls local class 'Patriotic_Individual'
        """
        self.update_(flagRanking=True)   # updates individual ranks
        for C in self.Scenario.couples(self.ranking):
            child = Patriotic_Individual(self.Scenario,ID=self.free_ID(), maxPatriotism = self.Scenario.Parameter('PopulationSize'), Newborn=True)
            if child:
                child.hybrid(C[0],C[1]) # child's DNA results from parents' DNA crossover
                child.mutate()
                child.update()  # computes the value of genes, as DNA is available only now
                if self.Scenario.new_agent(child, C):  # let scenario decide something about the newcomer (not used here)
                    self.updateDescendants(C[0], child)
                    self.updateDescendants(C[1], child)
                    self.receive(child) # adds child to the group


class Patriotic_Population(Base.Population):
    """ Defines the population of agents
        This is the level at which 'life_game' is played
    """

    def __init__(self, Scenario, Observer):
        " Creates a population of agents "
        Base.Population.__init__(self, Scenario, Observer)
        self.Scenario = Scenario

    def createGroup(self, ID=0, Size=0):
        " Calling local class 'Group' "
        return Group(self.Scenario, ID=ID, Size=Size)




if __name__ == "__main__":
    print(__doc__)

    #############################
    # Global objects			#
    #############################
    Gbl = Scenario()
    Base.Start(Gbl, Patriotic_Population)

    print("Bye.......")



__author__ = 'Lie and Dessalles'
