
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
Families are assumed to be (exact) genetic relatives
"""

#from time import sleep
#from random import sample, randint, shuffle, random
from numpy.random import choice

import sys

import SelfSacrifice_v00 as Base
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
            m[1].location = (start_location + m[0], m[1].gene_value('Honoring'))
            #m[1].location = (start_location + m[0], m[1].Patriotism)
            #m[1].location = (start_location + m[0], m[1].score())

########################################
##### Life_game #### (1) Initializations ####
########################################
    def prepare(self, indiv):
        """ Defines what is to be done at the individual level before interactions
            occur - Used in 'start_game'
        """
        indiv.score(self.endowment(indiv), FlagSet = True)	# Sets initial endowment
        indiv.SignalLevel = 0
        indiv.Admiration = 0
        #indiv.SelfSacrifice = False    #useful only for probabilistic mode
        #indiv.detach()	# indiv quits his/her friends
            # Done at the end of the year (evaluation) to avoid friendship with dead individuals
        
        
        ##### TEST : corr h and P ####
        h = indiv.gene_value('Honoring')
        maxvalue = 2 **	self.Parameter('GeneLength') - 1
        h = h / maxvalue * 10
        #indiv.Patriotism = (indiv.Patriotism + h)/2
        #   indiv.Patriotism = h



    def endowment(self,indiv): 
        """ Defines an individual's starting endowment
            Disloyal individuals are seen here as being loyal to the other group:
            they have already paid a cost to demonstrate that commitment
        """
        #return 10.0  # variant
        return indiv.Patriotism # should be between 0 and 10

########################################
##### TEST: honoring if all self-sacrifice
########################################
#    def spilloverSimple(self, Hero, beneficiaries, kin_transfer = 1):
 #       Relatives = beneficiaries[:]
#        for indiv in Relatives:
#            if indiv.SelfSacrifice:
#                Relatives.remove(indiv)
 #       for indiv in Relatives:
  #          indiv.score(+ Hero.Admiration / len(Relatives))
#
 #   def deathProbability(self, indiv):
  #      return 1

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
        if not heroes: return   # you need heroes to be able to honor them
        Offerings = 0
        for Patriot in patriots:
            maxvalue = 2 **	self.Parameter('GeneLength') - 1
            max_offering = Patriot.gene_value('Honoring') / maxvalue * 10
            offering = min(self.endowment(Patriot), max_offering)
                # you can't cut off your arm twice
            # An individual gives (his time, a valuable object, a goat...) proportionally to his or her genes
            # Here, he gives up some or all of his initial endowment of 10 points
            
                    # CHEAT ? variant ############ pourquoi j'ai fait ca ?
                    #Patriot.SignalLevel += offering * len(heroes) # CHEAT?
                    #Patriot.score(-self.costOffering(Patriot, offering))
            
            Patriot.SignalLevel += offering
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
        if not Signalers:	return
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
    def evaluation(self, indiv, members):
        indiv.score(- self.costSignal(indiv))   # cost of offering
        
        if indiv.SelfSacrifice:
            self.spilloverSimple(indiv, members, percent(self.Parameter('SacrificeHeredity')))
            indiv.score(0, FlagSet = True) #### Heroes don't actually die but can't reproduce / have a lower score than alive individuals
                    
        else:
# too conplicated? // CHEAT => look at Coopeartion not Patriotism
            if indiv.best_friend() is not None:
                #Variant: friends from the group you are commited to benefit you
#                indiv.best_friend().score(+ self.Parameter('JoiningBonus')/100.0 \
#                                                * indiv.best_friend().Patriotism / 10)

                indiv.best_friend().score(+ percent(self.Parameter('JoiningBonus')))


            " It's the end of the war: friends reveal themselves for who they really are "            
            for Friend in indiv.friends.names():
                if (Friend.Patriotism > (1-percent(self.Parameter('TruePatriots'))) * 10.0) :
                    # Friend is a true patriot who can vouch for you
                    indiv.score(+ 10 * (self.Parameter('FriendshipValue')/100.0) )
                if (Friend.Patriotism < percent(self.Parameter('Traitors') * 10.0)) :
                    # Friend is a traitor who sells you out
                    indiv.score(- 10 * (self.Parameter('DenunciationCost')/100.0) )
        indiv.detach()	# indiv quits his/her friends
        #print(indiv.score())

    def costSignal(self, indiv):
        #return indiv.SignalLevel * (10 - indiv.Patriotism) / 10 ## :( variant
        return indiv.SignalLevel * percent(self.Parameter('SignalingCost'))

    def costOffering(self, indiv, offering = 0):
        return offering * (10 - indiv.Patriotism) / 10

class Patriotic_Individual(Base.Individual, EA.Follower):
    "   Individuals now also have a patriotism phenotype "

    def __init__(self, Scenario, ID, nbPatriots = 100, Newborn=True):
        self.IdNb = int( ID[2:]	)	# ID is constructed as Groupnumber_IdNb - there is always only 1 group
        self.Patriotism = (10.0 * self.IdNb) / nbPatriots
        self.Patriotism = min(10.0, self.Patriotism)
        # Patriotism should be between 0 and 10
        Base.Individual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
        #self.Offerings = 0		# represents how much one is honored after self-sacrifice (should stay at 0 whilst alive)
        self.SignalLevel = 0
        # self.BestSignal = 0
        EA.Follower.__init__(self, Scenario.Parameter('MaxFriends'), Scenario.Parameter('MaxFriends'))

class Patriotic_Group(Base.Group):
    " In each group, patriotism is evenly distributed between 0 and 10 "

    def __init__(self, Scenario, ID=1, Size=100):
        Base.Group.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        # calling local class 'Individual'
        Indiv = Patriotic_Individual(self.Scenario, ID=self.free_ID(), nbPatriots = self.Scenario.Parameter('PopulationSize'), Newborn=Newborn)
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
            child = Patriotic_Individual(self.Scenario,ID=self.free_ID(), nbPatriots = self.Scenario.Parameter('PopulationSize'), Newborn=True)
            if child:
                child.hybrid(C[0],C[1]) # child's DNA results from parents' DNA crossover
                child.mutate()
                child.update()  # computes the value of genes, as DNA is available only now
                if self.Scenario.new_agent(child, C):  # let scenario decide something about the newcomer (not used here)
                        # Child is added to parents' children lists
                    C[0].addChild(child)
                    C[1].addChild(child)
            
                    self.receive(child) # Adds child to the group


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
        return Patriotic_Group(self.Scenario, ID=ID, Size=Size)




if __name__ == "__main__":
    print(__doc__)

    #############################
    # Global objects			#
    #############################
    Gbl = Scenario()
    Base.Start(Gbl, Patriotic_Population)

    print("Bye.......")



