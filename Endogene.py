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

from random import randint, random

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
        return [('SelfSacrifice'), ('Patriot'), ('NonPatriot')] 		# gene length (in bits) is read from configuration

    def display_(self):
        return [('red', 'SelfSacrifice'), ('white', 'Patriot'), ('black', 'NonPatriot')]

    def update_positions(self, members, start_location):
        """ locates individuals on an 2D space
        """
        # sorting individuals by gene value
        duplicate = members[:]
        #duplicate.sort(key=lambda x: x.gene_value('SelfSacrifice'))
        duplicate.sort(key = lambda x: x.Patriotism)
        for m in enumerate(duplicate):
            #m[1].location = (start_location + m[0], m[1].score() )
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
        indiv.score(10, True)
        #max = self.Parameter('MaxOffer')
        #indiv.score( max + indiv.Patriotism * (100 - max), FlagSet = True)	# Sets score to 10 or 90
        
        if self.Parameter('LongTerm'):
            indiv.SignalLevel = (1-percent(self.Parameter('Forgetfullness')))*indiv.SignalLevel
            # Something from nothing ? / but sacrifice => dead forever // compensated by gain for ever ?
        else: indiv.SignalLevel = 0

########################################
##### Life_game #### (2) Self-sacrifices ####
########################################
    def honoring(self, members, nbheroes, LongTerm = True):
        #if not heroes: return 0

        Offerings = 0
        for Indiv in members:
            #score = Indiv.score()
            if Indiv.Patriotism == 0:
                offering = Indiv.gene_relative_value('NonPatriot')
                
                if self.Parameter('DifferentialCosts') == 0: # version offre bornee
                    Indiv.score(- self.costHonor(offering))
                    offering = min(self.Parameter('MaxOffer'), offering)    # can't offer that much : face already tatooed, arm already cut off...
                        # triche faire ca apres le cout ?
                else:   # version cout differenties
                    Indiv.score( - self.costHonor(offering, DifferentialCosts = True))
            else:
                offering = Indiv.gene_relative_value('Patriot')
                Indiv.score (- self.costHonor(offering))

            #Indiv.SignalLevel += int(offering * nbheroes / 200)
            #### Pour version avec reinit du signal
                # Signal value depends on number of heroes...  
            #Offerings += offering * nbheroes    # MASSIF /// mais defendable ?
                # argument : ce qui est shared vient de plein d'annees ?? => oui mais c'est pas dans nbheroes ca, mais dans SGLLVL

            #Offerings += int(offering)  # meme sans int OK ??
            #Offerings += offering
            #Offerings += offering * nbheroes / 10
            

            #### version sans reinit du signal :
            Indiv.SignalLevel += offering
            Offerings += Indiv.SignalLevel
            Indiv.VisibleSignal = int(Indiv.SignalLevel / self.Parameter('DiscernableUnit'))
            #print(Indiv.SignalLevel)
            #print(nbheroes)
        #print(Offerings)    
        return Offerings
    
    def costHonor(self, offering, DifferentialCosts = False, patriotism = 0):
        basic_cost = offering * percent(self.Parameter('HonoringCost'))
        if not DifferentialCosts:
            return basic_cost
        else:   # NonPatriots face a premium for honoring
            return basic_cost * (1 - patriotism) * (1 + percent(self.Parameter('DishonestPremium')))
            # NonPatriots face a premium for honoring

########################################
##### Life_game #### (3) Social interactions ####
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
        Signalers.sort(key=lambda S: S.VisibleSignal, reverse=True)
        for Signaler in Signalers:
            if Signaler == indiv:	continue
            if OldFriend and OldFriend.VisibleSignal >= Signaler.VisibleSignal:
                break	# no available interesting signaler
            if Signaler.followers.accepts(0) >= 0:
                # cool! Self accepted as fan by Signaler.
                if OldFriend is not None and OldFriend != Signaler:
                    indiv.G_quit_(OldFriend)
                indiv.F_follow(0, Signaler, Signaler.VisibleSignal)
                break
    
    
    def interact_all(self, indiv, Signalers):
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
        if indiv.best_friend() is not None:
                if not indiv.best_friend().SelfSacrifice:
                    indiv.best_friend().score(+ self.Parameter('JoiningBonus'))

        " It's the end of the war: friends reveal themselves for who they really are "
        for Friend in indiv.friends.names():
            #print(Friend.Patriotism)
            if Friend.Patriotism == 0:
                if random() < percent(self.Parameter('NbTraitors')):
                # Friend is a traitor who sells you out
                    if self.Parameter('DenunciationCost')==0: 
                        indiv.Executed = True   # infinite cost: indiv will be executed by the Gestapo
                    else:
                        indiv.score(- self.Parameter('DenunciationCost'))
            else:
                if random() < percent(self.Parameter('NbTruePatriots')):
                # Friend is a true patriot who can vouch for you
                    indiv.score(+ self.Parameter('FriendshipValue'))
        indiv.detach()	# indiv quits his/her friends


    def lives(self, members):
        """ Converts alive members' scores into life points - used in 'life_game'
        """
        AliveMembers = members[:]
        for i in members:
            if i.Executed:
                AliveMembers.remove(i)
                i.LifePoints = -1
        if self.Parameter('SelectionPressure') == 0:
            return	# 'Selectivity mode' : outcomes depend on relative ranking  (see 'parenthood')
        if not AliveMembers:
            return
        BestScore = max([i.score() for i in AliveMembers])
        MinScore = min([i.score() for i in AliveMembers])
        if BestScore == MinScore:
            return
        for indiv in members:
            indiv.LifePoints =  int ( (indiv.score()-MinScore) * self.Parameter('SelectionPressure') / (BestScore - MinScore) )
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
        #self.Offerings = 0		# represents how much one is honored after self-sacrifice (should stay at 0 whilst alive)
        self.SignalLevel = 0
        self.VisibleSignal = 0
        self.Executed = False
        # self.BestSignal = 0
        EA.Follower.__init__(self, Scenario.Parameter('MaxFriends'), Scenario.Parameter('MaxFriends'))

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