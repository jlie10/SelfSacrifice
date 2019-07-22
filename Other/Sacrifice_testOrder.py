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


""" Study of the possibility of self-sacrifice being an ESS / as first-order signal for patriotism
Adding a Demand gene --> which should prevent a dishonest signal // should be null in time of peace
===> 27-05: ah non en fait, depend de bruit d'explo ?
v1
"""

from math import log
from random import randint, random, choice

import Exogene as Base

import sys
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Ecology.Alliances as EA
from Evolife.Tools.Tools import percent


class Scenario(Base.Scenario):

########################################
#### General initializations and visual display ####
########################################

    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('Patriot'), ('NonPatriot'), ('Demand'), ('SelfSacrifice')] 		# gene length (in bits) is read from configuration

    def update_positions(self, members, start_location):
        """ locates individuals on an 2D space
        """
        # sorting individuals by gene value
        duplicate = members[:]
        #duplicate.sort(key=lambda x: x.gene_value('SelfSacrifice'))
        duplicate.sort(key = lambda x: x.Patriotism)
        for m in enumerate(duplicate):
            #m[1].location = (start_location + m[0], m[1].score() )
            #m[1].location = (start_location + m[0], m[1].Reproductive_points )
            #m[1].location = (start_location + m[0], m[1].Share )
            #m[1].location = (start_location + m[0], m[1].LifePoints)
            #m[1].location = (start_location + m[0], m[1].HeroesRelatedness)
            #m[1].location = (start_location + m[0], m[1].gene_value('SelfSacrifice'))
            m[1].location = (start_location + m[0], m[1].SignalLevel)

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

        indiv.SignalLevel = 0      
        indiv.Reproduction_points = 0 

        # friendship links (lessening with time) are updated 
        indiv.lessening_friendship((100 - self.Parameter('Erosion'))/100.0)

########################################
##### Life_game #### (2) Self-sacrifices ####
########################################

    def honoring(self, worshippers, nb_heroes):        
        if nb_heroes == 0: return 0 # no heroes to honor
        Offerings = 0
        for Indiv in worshippers:
            #score = Indiv.score()
            if Indiv.Patriotism == 0:
                offering = Indiv.gene_relative_value('NonPatriot')
                if self.Parameter('DifferentialCosts') == 0: # version offre bornee
                    Indiv.score(- self.costHonor(offering))
                    offering = min(self.Parameter('MaxOffer'), offering) 
                       # can't offer that much : face already tatooed, arm already cut off...
                        # TRICHE faire ca apres le cout ? +++++ REFLECHIR
                else:   # version cout differenties
                    Indiv.score( - self.costHonor(offering, DifferentialCosts = True))
            else:
                offering = Indiv.gene_relative_value('Patriot')
                Indiv.score (-self.costHonor(offering))

            Indiv.SignalLevel += int( offering / self.Parameter('VisibleThreshold')) * self.Parameter('VisibleThreshold')
            #Indiv.SignalLevel += offering   #int ?
            #Indiv.SignalLevel += offering / log(1 + nb_heroes)  # variant
            Offerings += Indiv.SignalLevel #int ?
            #Offerings += int( offering / self.Parameter('VisibleThreshold')) * self.Parameter('VisibleThreshold')
                # ou plus fort ---> param un seuil... y a deja precision et disc...
            #Indiv.VisibleSignal = Indiv.SignalLevel
            #Indiv.VisibleSignal = int(Indiv.SignalLevel / self.Parameter('DiscernableUnit'))
                # OSEF FOR NOW ??
                # redondant avec lives10 du coup ? / variant
            #print(Indiv.SignalLevel)
            #print(nbheroes)
        return Offerings
    
      
    def costHonor(self, offering, DifferentialCosts = False, patriotism = 0):
        basic_cost = offering * percent(self.Parameter('HonoringCost'))
        if not DifferentialCosts:
            #print('Offer max')
            return basic_cost
        else:   # NonPatriots face a premium for honoring
            #print('diff cost')
            return basic_cost + basic_cost * (1 - patriotism) * percent(self.Parameter('DishonestPremium'))
            # NonPatriots face a premium for honoring

########################################
##### Life_game #### (3) Social interactions ####
########################################
    
    def interact_old(self, receiver, Signalers):
        """ Receiver selects the first Signaler it sees that matches his demands
            (and that accepts it as a follower)
        """
        Candidates = self.filter(Signalers, receiver.gene_relative_value('Demand'))
        if Candidates == []: return
        offer = receiver.SignalLevel
        for Signaler in Candidates:
            #demand = Signaler.gene_relative_value('Demand')
            #if offer < demand:
            #    continue
            if Signaler.followers.accepts(0) >=0:
                receiver.F_follow(0, Signaler, 0)
                break
 
    def interact(self, indiv, Signalers):
        """ Formation of friendship bonds
            By honoring heroes (see 'honoring'), individuals signal their patriotism
            This signal is used by others to choose their friends
            (keeping in mind this is crucial: see 'evaluation')
        """
        if not Signalers:	return
        # The agent chooses the best available Signaler from a sample.
        #Signalers.sort(key=lambda S: S.SignalLevel, reverse=True)
        demand = indiv.gene_relative_value('Demand')
        offer = indiv.SignalLevel  
        for Signaler in Signalers:
            if Signaler == indiv: continue
            if indiv.follows(Signaler): continue
            if demand > Signaler.SignalLevel:
                continue
                #break   # No available interesting Signalers
            if offer < Signaler.gene_relative_value('Demand'):
                continue    # Signaler is not interested in befriending indiv
            #if indiv.get_friend(offer, Signaler, Signaler.SignalLevel):
                ##### ERROR: Partner changed mind...    #####
            #    return   # Indiv and Signaler have become friends !
            if Signaler.followers.accepts(0) >=0:
                if indiv.F_follow(offer, Signaler, Signaler.SignalLevel):            
                    return
       
    def filter(self, Signalers, requirement):
        AcceptableFriends = Signalers[:]
        for Signaler in Signalers:
            if Signaler.SignalLevel < requirement:
                AcceptableFriends.remove(Signaler)
        return AcceptableFriends
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


        if indiv.Patriotism ==0 and random() < percent(self.Parameter('NbTraitors')):
            # indiv is a traitor who betrays its friends
            for follower in indiv.followers:
                self.betrayed(follower, cost = self.Parameter('DenunciationCost'))
                indiv.score(+ self.Parameter('Judas')) 

        elif indiv.Patriotism ==1:
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

class Patriotic_Individual(Base.Individual, EA.Follower):
    "   Individuals now also have a patriotism phenotype "

    def __init__(self, Scenario, ID, maxPatriotism = 100, Newborn=True):
        #self.IdNb = int( ID[2:]	)	# ID is constructed as Groupnumber_IdNb - there is always only 1 group
        self.Patriotism = randint(0, 1)

        Base.Individual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
        #EA.Friend.__init__(self, self.Scenario.Parameter('MaxFriends'))  # 

        #self.Offerings = 0		# represents how much one is honored after self-sacrifice (should stay at 0 whilst alive)
        self.SignalLevel = 0
        #self.VisibleSignal = 0
        self.Executed = False
        # self.BestSignal = 0
        EA.Follower.__init__(self, self.Scenario.Parameter('MaxFriends'), Scenario.Parameter('MaxFriends'))
        #EA.Friend.__init__(self.Scenario.Parameter('MaxFriends'))  # WHY DOESN'T WORK ?

    # TODO : + update / display ---> rpz graphique 2d avec Patriotism

class Group(Base.Group):
    " In each group, patriotism ranges from 0 to group size (simplification) "

    def __init__(self, Scenario, ID=1, Size=100):
        Base.Group.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        # calling local class 'Individual'
        Indiv = Patriotic_Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
        # Individual creation may fail if there is no room left
        self.Scenario.new_agent(Indiv, None)  # let scenario know that there is a newcomer (unused)
        #if Indiv.location == None:	return None
        return Indiv

    def reproduction(self):
        """ Reproduction within the group (see Exogene) for details
            Calls local class 'Patriotic_Individual'
        """
        self.update_(flagRanking=True)   # updates individual ranks
        for C in self.Scenario.couples(self.ranking):
            # Making of the child
            child = Patriotic_Individual(self.Scenario,ID=self.free_ID(), Newborn=True)
            if child:
                child.hybrid(C[0],C[1]) # Child's DNA results from parents' DNA crossover
                child.mutate()
                child.inherit_share(C[0],C[1], heredity = percent(self.Scenario.Parameter('SacrificeHeredity')))
                child.update()  # Computes the value of genes, as DNA is available only now
                if self.Scenario.new_agent(child, C):  # Let scenario decide something about the newcomer (not used here)
                        # Child is added to parents' children lists
                    C[0].addChild(child)
                    C[1].addChild(child)
            
                    self.receive(child) # Adds child to the group

class Patriotic_Population(Base.Population):
    """ Defines the population of agents
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