
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


""" Study of the possibility of a second-order signal on self-sacrifice
Families are assumed to be (exact) genetic relatives
"""

#from time import sleep
#from random import sample, randint, shuffle, random
#from numpy.random import choice

import sys

import SelfSacrifice_GR as SS
import SelfSacrifice_v00 as Base
sys.path.append('..')
sys.path.append('../../..')

from Evolife.Tools.Tools import percent

class Scenario(SS.Scenario):
        
    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('Honoring')] 		# gene size is read from configuration

    def display_(self):
        return [('blue', 'Honoring')]
        #return[('red','SelfSacrifice'), ('blue', 'Honoring'), ('yellow', 'average'), ('black', 'best')]
        #Best and/or average scores can also be displayed

    def update_positions(self, members, start_location):
        """ locates individuals on an 2D space
        """
        # sorting individuals by gene value
        duplicate = members[:]
        duplicate.sort(key=lambda x: x.gene_value('Honoring'))
        for m in enumerate(duplicate):
            m[1].location = (start_location + m[0], m[1].gene_value('Honoring'))
            #m[1].location = (start_location + m[0], m[1].Patriotism)
            #m[1].location = (start_location + m[0], m[1].score())
            #m[1].location = (start_location + m[0], m[1].LifePoints)

########################################
##### Self-sacrifices
########################################

    def spilloverSimple(self, Hero, beneficiaries, kin_transfer = 1):
        " All individuals are in the same 'family' (same SelfSacrifice gene) "
        Relatives = beneficiaries[:]
        for indiv in Relatives:
            if indiv.SelfSacrifice:
               Relatives.remove(indiv)
        for indiv in Relatives:
            indiv.score(+ Hero.Admiration / len(Relatives))

    def deathProbability(self, indiv):
        " All individuals have the self-sacrifice gene "
        return 1


########################################
##### Test : corr p et h
########################################

    def prepare(self, indiv):
        """ Defines what is to be done at the individual level before interactions
            occur - Used in 'start_game'
        """
        indiv.score(self.endowment(indiv), FlagSet = True)	# Sets initial endowment
        indiv.SignalLevel = 0
        indiv.Admiration = 0

        h = indiv.gene_value('Honoring')
        maxvalue = 2 **	self.Parameter('GeneLength') - 1
        h = h / maxvalue * 10
        indiv.Patriotism = (indiv.Patriotism + h)/2
        #   indiv.Patriotism = h


########################################
##### Honoring game
########################################

    def honoring(self, patriots, heroes):
        """ Variant where what can be offered is capped by endowment
        """
        if not heroes: return   # should be useless
        Offerings = 0
        for Patriot in patriots:
            maxvalue = 2 **	self.Parameter('GeneLength') - 1
            max_offering = Patriot.gene_value('Honoring') / maxvalue * 10
            offering = min(self.endowment(Patriot), max_offering)
                # you can't cut off your arm twice
            Patriot.SignalLevel += offering
            #print(offering)
            # By doing so, a patriot signals his/her patriotism to others, which they will take into account when choosing friends
            Offerings += offering
        self.pantheon(heroes, Offerings, self.Parameter('HeroCompetivity'))
    

    def endowment(self, indiv):
        #return 10.0
        return indiv.Patriotism # variant -> membership cost idea

    def costSignal(self, indiv):
        return indiv.SignalLevel  * percent(self.Parameter('SignalingCost'))
        #return indiv.SignalLevel * (10 - indiv.Patriotism) / 10 * percent(self.Parameter('SignalingCost'))
        # why would cost depend on P // how is the signal honest ?

    def evaluation(self, indiv, members):
        #print(indiv.LifePoints)
        
        indiv.score(- self.costSignal(indiv))
        
        if indiv.SelfSacrifice:
            #print(indiv.Admiration)
            ####self.spilloverSimple(indiv, members, percent(self.Parameter('SacrificeHeredity')))
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


########################################
##### Other stuff
########################################


class Individual(SS.Patriotic_Individual):

    def __init__(self, Scenario, ID, nbPatriots = 100, Newborn = True):
        SS.Patriotic_Individual.__init__(self, Scenario, nbPatriots=nbPatriots, ID=ID, Newborn=Newborn)
        self.Patriotism = min(self.Patriotism, 10.0)

class Group(SS.Patriotic_Group):

    def __init__(self, Scenario, ID=1, Size=100):
        SS.Patriotic_Group.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        # calling local class 'Individual'
        Indiv = Individual(self.Scenario, ID=self.free_ID(), nbPatriots = self.Scenario.Parameter('PopulationSize'), Newborn=Newborn)
        return Indiv
    
    def reproduction(self):
        """ Reproduction within the group (see SelfSacrifice_v0) for details
            Calls local class 'Patriotic_Individual'
        """
        self.update_(flagRanking=True)   # updates individual ranks
        for C in self.Scenario.couples(self.ranking):
            child = Individual(self.Scenario,ID=self.free_ID(), nbPatriots = self.Scenario.Parameter('PopulationSize'), Newborn=True)
            if child:
                child.hybrid(C[0],C[1]) # child's DNA results from parents' DNA crossover
                child.mutate()
                child.update()  # computes the value of genes, as DNA is available only now
                if self.Scenario.new_agent(child, C):  # let scenario decide something about the newcomer (not used here)
                        # Child is added to parents' children lists
                    C[0].addChild(child)
                    C[1].addChild(child)
            
                    self.receive(child) # Adds child to the group

class H_Population(SS.Patriotic_Population):
    """ Defines the population of agents
        This is the level at which 'life_game' is played
    """

    def __init__(self, Scenario, Observer):
        " Creates a population of agents "
        SS.Patriotic_Population.__init__(self, Scenario, Observer)
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
    Base.Start(Gbl, H_Population)

    print("Bye.......")



