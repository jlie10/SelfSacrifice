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
'Family gene' version
"""

from random import shuffle, random, randint

import Exogene as Base

import sys
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Genetics.DNA as Gen

from Evolife.Tools.Tools import percent

class Scenario(Base.Scenario):

########################################
#### General initializations and visual display ####
########################################

    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('SelfSacrifice'), ('Family', 100)] 		# gene length (in bits) is read from configuration

    def display_(self):
        return [('red', 'SelfSacrifice')]

    def update_positions(self, members, start_location):
        """ locates individuals on an 2D space
        """
        # sorting individuals by gene value
        duplicate = members[:]
        duplicate.sort(key=lambda x: x.gene_value('SelfSacrifice'))
        #duplicate.sort(key = lambda x: x.ID)
        for m in enumerate(duplicate):
            m[1].location = (start_location + m[0], m[1].score() )
            #m[1].location = (start_location + m[0], m[1].Share )
            #m[1].location = (start_location + m[0], m[1].LifePoints)
            #m[1].location = (start_location + m[0], m[1].HeroesRelatedness)
            #m[1].location = (start_location + m[0], m[1].gene_value('SelfSacrifice'))
    
    #### For test
    def remove_agent(self, agent):
        " action to be performed when an agent dies "
        #print(agent.LifePoints)
        #print(agent.age)
        #print(agent.SelfSacrifice)
        #print('\n')
            


########################################
##### Life_game #### (2) Self-sacrifices ####
########################################
            ## (2b) Population-level self-sacrifice game
    def sacrifices(self, members):
        """ Self-sacrifice 'game':
            Heroes may self-sacrifice "for the good of the group"
            In return they are admired - admiration is exogenous here
            Used in 'life_game'
        """
        Heroes = []
        Cowards = members[:]
        for indiv in members:	# Deciding who are the population's heroes
            if indiv.SelfSacrifice:	# indiv is already a hero (that sacrificed at an earlier round)
                Heroes.append(indiv)
                Cowards.remove(indiv)
            elif self.selfSacrifice(indiv):	# indiv is not already a hero but is given an opportunity to be one
                Heroes.append(indiv)
                Cowards.remove(indiv)
        # In return, heroes are honored (admired) by society
        #self.honoring(Cowards, Heroes)
        self.spillover_relatives(Heroes, Cowards)
        self.kill_heroes(Heroes)
        # The rest of society interacts (builds friendships) - see 3
        #self.interactions(Cowards, self.Parameter('Rounds'))           #USELESS HERE
        return Cowards

    def spillover_relatives(self, heroes, relatives):
        """ Genetic relatives of heroes benefit from their sacrifice
            Used in 'honoring'
        """
        for Hero in heroes:
            hero_gen = Hero.get_DNA()[self.Parameter('GeneLength'):]
            share_Hero = 0
            for PotentialRelative in relatives:
                prel_gen = PotentialRelative.get_DNA()[self.Parameter('GeneLength'):]
                share_Hero += PotentialRelative.Share
                PotentialRelative.Share += self.genetic_relatedness(hero_gen, prel_gen)
                share_Hero += PotentialRelative.Share
            print(Hero.ID)
            print(share_Hero / len(relatives))
            print('\n')

    def genetic_relatedness(self, gen1, gen2, length = 100):
        r = 0
        for i in range(length):  # both sequences should be of length 100
            if gen1[i] == gen2[i]:
                r += 1
        r = r / length
        if r < 0.7:
        #if r - percent(self.Parameter('MutationRate')) - noise/length < 0.575:
            return 0
        return 2 * (r - 0.5)

########################################
########################################
########################################

class DNA(Gen.DNA):
    
    #def __init__(self, Scenario, Nb_nucleotides):
                    
    def noise(self, excluded = 0, maxloci = 5):
        " Adds noise to the 'family' gene to prevent convergence / 'free-riding' "
        for pertub in range(maxloci):
            pos = randint(excluded, self.nb_nucleotides - 1)     # Noise should only affect the 'family' gene
            if random() < 0.5:
                self.__dna[pos] = 0
            else:
                self.__dna[pos] = 1

########################################
########################################
########################################

class Individual(Base.Individual, DNA):
    "   Defines what an individual consists of "

    def __init__(self, Scenario, ID=None, Newborn=True):
        self.SelfSacrifice = False
        self.Admiration = 0
        
        #self.HeroesRelatedness = 0
        #self.HeroesWitnessed = 0
        #self.PastScore = 0

        self.Share = 0
        #if Newborn:
        #    self.LifePoints = 100 # Test vs morta infantile
        #else:
        #    self.LifePoints = 0 


        self.Children = []  # useless here
        EI.EvolifeIndividual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
        DNA.__init__(self, Scenario, Scenario.geneMap_length())

  
########################################
########################################
########################################

class Group(Base.Group):
    """ The group is a container for individual (By default the population only has one)
        It is also the level at which reproduction occurs
        Individuals are stored in self.members
    """

    def __init__(self, Scenario, ID=1, Size=100):
        Base.Group.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        " Calling local class 'Individual'"
        Indiv = Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
        # Individual creation may fail if there is no room left
        self.Scenario.new_agent(Indiv, None)  # Let scenario know that there is a newcomer (unused)
        return Indiv

    #def update_(self, flagRanking = False, display=False):
        """ updates various facts about the group
        """
    #    # removing old chaps
    #    for m in self.members[:]:  # must duplicate the list to avoid looping over a modifying list
    #        if m.dead():	self.remove_(self.members.index(m))
            #if m.SelfSacrifice:	self.remove_(self.members.index(m)) # heroes die ################### ??
    #    self.size = len(self.members)
    #    if self.size == 0:	return 0
        # ranking individuals
    #    if flagRanking:
            # ranking individuals in the group according to their score
    #        self.ranking = self.members[:]	  # duplicates the list, not the elements
    #        self.ranking.sort(key=lambda x: int(x.score()/10),reverse=True)
    #        if self.ranking != [] and self.ranking[0].score() < 1:           #### RANDOM THRESHOLD = 1
    #            # all scores are zero
    ##            shuffle(self.ranking)  # not always the same ones first
    #        self.best_score = self.ranking[0].score()
    #    return self.size


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
                child.inherit_share(C[0],C[1])
                child.noise(excluded = self.Scenario.Parameter('GeneLength'), maxloci = self.Scenario.Parameter('GeneticNoise'))
                child.update()  # Computes the value of genes, as DNA is available only now
                if self.Scenario.new_agent(child, C):  # Let scenario decide something about the newcomer (not used here)
                        # Child is added to parents' children lists
                    C[0].addChild(child)
                    C[1].addChild(child)        #useless here - just for test
            
                    self.receive(child) # Adds child to the group

########################################
########################################
########################################

class Population(Base.Population):
    """ Defines the population of agents
        This is the level at which 'life_game' is played
    """

    def createGroup(self, ID=0, Size=0):
        " Calling local class 'Group' "
        return Group(self.Scenario, ID=ID, Size=Size)

########################################
########################################
########################################


if __name__ == "__main__":
    print(__doc__)

    #############################
    # Global objects			#
    #############################
    Gbl = Scenario()
    Base.Start(Gbl)
