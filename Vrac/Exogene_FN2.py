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
'Family name' version
"""

from random import shuffle, random, randint, choice, randint

import Exogene as Base

import sys
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Ecology.Phenotype as Phen

from Evolife.Tools.Tools import percent

class Scenario(Base.Scenario):

########################################
#### General initializations and visual display ####
########################################

#    def phenemap(self):
#        """ Defines the set of non inheritable characteristics
#        """
 #       return['Name1', 'Name2', 'Name3', 'Name4', 'Name5', 'Name6']
        
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
##### Life_game #### (1) Initializations ####
########################################
    def prepare(self, indiv):
        """ Defines what is to be done at the individual level before interactions
            occur - Used in 'start_game'
        """
        indiv.score(0, FlagSet = True)	# Sets score to 0
        indiv.Admiration = 0
        indiv.Share = 0


########################################
##### Life_game #### (2) Self-sacrifices ####
########################################
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
        self.honoring(Cowards, Heroes)
        self.spillover(Cowards, Heroes)
        self.kill_heroes(Heroes)
        return Cowards

    def honoring(self, patriots, heroes):
        " Exogenous honoring of heroes"
        for Hero in heroes:
            Hero.Admiration = self.Parameter('Admiration')

    def spillover(self, members, heroes):
        " Admiration spills over to relatives "
        for Hero in heroes:
            tot_share = 0
            for Relative in members:
                tot_share += self.relatedness(Hero, Relative)
            if tot_share != 0:           
                for Relative in members:
                    Relative.score(+ self.relatedness(Hero, Relative) / tot_share * Hero.Admiration)
                    print(Relative.score())

    def relatedness(self, indiv1, indiv2):
        FN2 = indiv2.FamilyNames[:]
        FN1 = indiv1.FamilyNames
        Common_Names = [n for n in FN1 if n in FN2 and (FN2.pop(FN2.index(n)))]
        #print( len(Common_Names) / self.Parameter('NbNames') )
        if len(Common_Names) >= 2:
            return len(Common_Names) / self.Parameter('NbNames')
        else:
            return 0

########################################
########################################
########################################

class Individual(Base.Individual, Phen.Phene):
    "   Defines what an individual consists of "

    def __init__(self, Scenario, ID=None, Newborn=True):
        self.SelfSacrifice = False
        
        NbNames = Scenario.Parameter('NbNames')
        self.FamilyNames = [randint(1,100) for i in range(NbNames)]
        #self.LifePoints = randint(0, Scenario.Parameter('SelectionPressure'))


        # ECHEC version avec phene init ici
        #NbNames = Scenario.Parameter('NbNames')
        #if NameClass is None: NameClass = Phen.Phene
        #self.FamilyNames = [NameClass(NameNb) for NameNb in range(NbNames)]
        #self.FamilyNames = [Phen.Phene(NameNb) for NameNb in range(NbNames)]

        #self.HeroesRelatedness = 0
        #self.HeroesWitnessed = 0
        #self.PastScore = 0

        self.Share = 0
        #if Newborn:
        #    self.LifePoints = 100 # Test vs morta infantile
        #else:
        #    self.LifePoints = 0 


        self.Children = []  # useless here
        Base.Individual.__init__(self, Scenario, ID=ID, Newborn=Newborn)

    def inherit_names(self, parent1, parent2, NbNames = 6):
        for i in range(NbNames):
            if i < NbNames/3:
                self.FamilyNames[i] = parent1.FamilyNames[i]
            elif i < 2*NbNames/3:
                self.FamilyNames[i] = parent2.FamilyNames[i]
        shuffle(self.FamilyNames)

    def inherit_names_dico_relou(self, parent1, parent2):
        Remaining_Names = self.Phenes[:]
        for i in range(4):
            inh_Name = choice(Remaining_Names)
            if i < 2:
                self.Phenes[inh_Name].__value = parent1.Phenes[inh_Name].value()
            else:
                self.Phenes[inh_Name].__value = parent1.Phenes[inh_Name].value()
            Remaining_Names.pop(inh_Name)
            # Last two names are left random        

    def inherit_names_failed(self, parent1, parent2, NbNames = 6):
        for i in range(NbNames):
            if i < NbNames/3:
                self.FamilyNames[i].__value = parent1.FamilyNames[i].value()
            elif i < 2*NbNames/3:
                self.FamilyNames[i].__value = parent2.FamilyNames[i].value()
        shuffle(self.FamilyNames)

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
                #child.inherit_share(C[0],C[1])
                child.inherit_names(C[0], C[1], self.Scenario.Parameter('NbNames'))
                child.update()  # Computes the value of genes, as DNA is available only now
                if self.Scenario.new_agent(child, C):  # Let scenario decide something about the newcomer (not used here)
            
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
    Base.Start(Gbl, Population)
