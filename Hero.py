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


""" 
Taken from master ---> TODO : check that no conflicts / old stuff when computer is back up running
"""

from random import sample, shuffle, random, choice, randint
from math import exp, log
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

from Evolife.Tools.Tools import percent, chances, decrease, error

class Scenario(ED.Default_Scenario):

########################################
#### General initializations and visual display ####
########################################
    def __init__(self):
        # Parameter values
        ED.Default_Scenario.__init__(self, CfgFile='_Params.evo')	# loads parameters from configuration file
        self.initialization()

    def initialization(self):
        self.RememberedHeroes = 0 # Nb of heroes that society "remembers" in a given round

    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('Readiness')]
        #return [('Hero')]   
        #return [('SelfSacrifice')]  # gene length (in bits) is read from configuration

    def phenemap(self):
        """ Defines the set of non inheritable characteristics """
        return ['Patriotism']

    def display_(self):
        disp = [(i+1,G.name) for (i,G) in enumerate(self.GeneMap)]
        L = len(disp)
        disp += [(L+1, 'RememberedHeroes')]
        return disp
        
    def local_display(self, ToBeDisplayed):
        " allows to diplay locally defined values "
        if ToBeDisplayed == 'RememberedHeroes':
            return self.RememberedHeroes # displaying a quantity that can be computed within the scenario
        return None

    def update_positions(self, members, groupLocation):
        for indiv in members:	
            indiv.location = (groupLocation + indiv.Phene_value('Patriotism'), 
                # indiv.Phene_value('Risk'), 'blue', 6)
                indiv.Reproductive_points, 'blue', 6)
    
    def new_agent(self, child, parents):
        child.inherit_share(parents[0],parents[1], heredity = percent(self.Parameter('SacrificeHeredity')))
        for P in parents: P.addChild(child)
        return True
           
########################################
##### Life_game #### (1) Initializations ####
########################################
    def prepare(self, indiv):
        """ Defines what is to be done at the individual level before interactions
            occur - Used in 'start_game'
        """
        indiv.Reproductive_points = 0
        #indiv.SelfSacrifice = False #for probabilistic + 'castrated zombie' mode

    def end_game(self, members):
        """ Sacrifice game. "Heroes" are removed from the group
            and will not bear (additional) children.
        """
        self.sacrifices(members)

    def lives(self, members):
        " Converts scores into life points (useless here) "
        AliveMembers = members[:]
        for indiv in members:
            if indiv.SelfSacrifice:
                AliveMembers.remove(indiv)  
                # For later: so their LP aren't changed to more than -1
        super().lives(AliveMembers)
    
########################################
##### Sacrifice game
########################################
            ## (a) Individual propensity to self-sacrifice
    def deathProbability(self, indiv):
        """ Depending on an individual's patriotism
            and genetic readiness to display it,
            the individual may engage in self-sacrifice
        """
        r = percent (indiv.gene_relative_value('Readiness')) \
            * percent (indiv.Phene_value('Patriotism'))
        #r = r/5 # pour comme JLD

        return r
        #if r > random():
        #    return percent( self.Parameter('SacrificeProbability') )
        #else: 
        #    return 0

    def selfSacrifice(self, indiv):
        """ An agent decides to make the ultimate sacrifice
            Self-Sacrifice is only a possibiltiy from a certain age (e.g. adulthood)
            and is controlled by the SelfSacrifice gene (see deathProbability)
            ---- NOT ANYMORE: type (hero gene) + parameter(SacrificeProbability)
            Used in 'sacrifices'
        """        
        p = self.deathProbability(indiv)
        ## 'Probablistic' mode:
        #bool = p > random() and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))
        #if p!=1: q = 1 - exp((log(1-p))/self.Parameter('AgeMax')*(1-percent(self.Parameter('SacrificeMaturity'))))  # => proba p de mourir a cause du gene
        #if p!=1: q = 1 - exp((log(1-p))/self.Parameter('AgeMax'))  # => proba p de mourir a cause du gene        
        #else: q = 1
        #bool = q > random() and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))
        #bool = q > random()
        #bool = 5*q > random()
        bool = p > random() 
        #bool = p > random() and p > random()
        #bool = p > 2*random()
        #bool = p > 10*random()

        ## 'Binary mode': (Individuals are programmed to self-sacrifice at a certain age)
        #bool = p == 1 and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))
        #bool = p > 0 and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))
        
        ## 'Threshold mode': gene codes for the value of the age after which sacrifice occurs
        # This is a measure of the 'value' of the sacrifice (how much potential reproduction is given up)
        #bool = indiv.age > (1-p) * self.Parameter('AgeMax')
        #bool = ( indiv.age > (1-p) * self.Parameter('AgeMax') ) and indiv.age < 0.8 * self.Parameter('AgeMax')

        indiv.SelfSacrifice = bool
        return bool

########################################
            ## (b) Population-level self-sacrifice game
    def sacrifices(self, members):
        """ Self-sacrifice 'game':
            Heroes may self-sacrifice "for the good of the group"
            In return they are admired - admiration is exogenous here
            Used in 'life_game'
        """
        Heroes = []
        Cowards = members[:]
        for indiv in members:	# Deciding who are the population's heroes
            #if indiv.SelfSacrifice:	# indiv is already a hero (that sacrificed at an earlier round)
            #    Heroes.append(indiv)    # (useless here : for 'castrated Zombie' mode)
            #    Cowards.remove(indiv)
            if self.selfSacrifice(indiv):	# indiv is not already a hero but is given an opportunity to be one
                Heroes.append(indiv)
                Cowards.remove(indiv)
        
        if self.Parameter('Baseline')==0:
            ######## baseline tot_h around 0 version
            random_heroes = 1 + int ( self.Parameter('PopulationSize') * (self.Parameter('MutationRate') / 1000 ) / self.Parameter('GeneLength'))
            self.RememberedHeroes = self.memo_heroes(len(Heroes)-random_heroes, Cowards, threshold = self.Parameter('RemThreshold'))
            #print('Society remembers {} voluntary heroes'.format(tot_heroes))   # Gives around 0 when A = 0...
        else: # not used
            ####### baseline > 0 version (20 with usual para)
            self.RememberedHeroes = self.memo_heroes(len(Heroes), Cowards, threshold = self.Parameter('RemThreshold'))
            #print('Society remembers {} total heroes'.format(tot_heroes))   # Gives around 20 +/- when A = 0...
        
        self.inc_shares(Heroes, Cowards)
    
        # In return, heroes are honored (admired) by society
        Admiration = self.honoring(Cowards, len(Heroes))
        #self.NbHeroes = len(Heroes)   # for display    # old = only display heroes of that round
        #self.RememberedHeroes = self.memo_heroes(len(Heroes), Cowards)
        self.spillover(Cowards, Admiration, threshold = self.Parameter('ReproGainsThreshold'))
        self.kill_heroes(Heroes)
        #return Cowards #Not used anymore

    def memo_heroes(self, new_heroes, members, threshold = 5):
        " Society, through its (alive)_ individuals, remembers its heroes "
        
        members.sort(key=lambda x: x.HeroesWitnessed, reverse = True)

        past_heroes = members[ int( percent(threshold) * len(members) )].HeroesWitnessed   
        # Heroes pass off to posterity if they are "remembered" by a sufficient amount of alive individuals (threshold %)
        for indiv in members:
            indiv.HeroesWitnessed += new_heroes
        return past_heroes + new_heroes

    def inc_shares(self, heroes, members):
        for Hero in heroes: # Children of heroes will benefit from their sacrifice
            for Child in Hero.Children:
                Child.Share += 1

    def honoring(self, worshippers, nb_heroes):
        """ Determines total 'social admiration' heroes may share
            Exogenous here, as a function of admiration.
            To be overloaded in two-tier (endogenous) model
        """
        if nb_heroes == 0: return 0 # no heroes to admire this round
        return self.Parameter('Admiration') * len(worshippers)

    def spillover(self, members, admiration = 0, threshold = 10):
        tot_share = 0
        for indiv in members:
            tot_share += indiv.Share
        if tot_share == 0:
            return
        for indiv in members:
            indiv.Reproductive_points += indiv.Share / tot_share * admiration
            indiv.Reproductive_points = int(indiv.Reproductive_points /threshold) # Only points above threshold entail reproductive advantage 

    def kill_heroes(self, heroes):
        for Hero in heroes:
            #Hero.score(-1, FlagSet = True)
            Hero.LifePoints = -1

########################################
########################################
########################################

class Individual(EI.EvolifeIndividual):
    "   Defines what an individual consists of "

    def __init__(self, Scenario, ID=None, Newborn=True):
        self.SelfSacrifice = False
        self.HeroesWitnessed = 0
        self.Reproductive_points = 0
        self.Share = 0
        self.Children = []
        EI.EvolifeIndividual.__init__(self, Scenario, ID=ID, Newborn=Newborn)

    def inherit_share(self, mom, dad, heredity = 0.5):
        self.Share += (mom.Share + dad.Share ) / 2 * heredity

    def isChild(self, Indiv):
        if Indiv in self.Children: return True
        return False

    def addChild(self, child):
        " Adds child to list "
        self.Children.append(child)

    def removeChild(self, child):
        """ Removes a child of self
        Used when the child dies (see 'Group.remove_')
        """
        if self.isChild(child):
            self.Children.remove(child)
    
########################################
########################################
########################################

class Group(EG.EvolifeGroup):
    """ The group is a container for individual (By default the population only has one)
        It is also the level at which reproduction occurs
        Individuals are stored in self.members
        Reproductive_points are used here to rank members for reproduction, not score
        (Selectivity)
    """

    def __init__(self, Scenario, ID=1, Size=100):
        EG.EvolifeGroup.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        " Calling local class 'Individual'"
        return Individual(self.Scenario, ID=self.free_ID(Prefix=''), Newborn=Newborn)

    def update_ranks(self, flagRanking = False, display=False):
        """ updates various facts about the group
        """
        # removing old chaps
        for m in self.members[:]:  # must duplicate the list to avoid looping over a modifying list
            if m.dead():	self.remove_(self.members.index(m))
            #if m.SelfSacrifice:	self.remove_(self.members.index(m)) # heroes die ################### ??
        self.size = len(self.members)
        if self.size == 0:	return 0
        # ranking individuals
        if flagRanking:
            # ranking individuals in the group according to their score
            self.ranking = self.members[:]	  # duplicates the list, not the elements
            self.ranking.sort(key=lambda x: x.Reproductive_points,reverse=True)
            if self.ranking != [] and self.ranking[0].Reproductive_points == 0:           #### RANDOM THRESHOLD = 1
                # all scores are zero
                shuffle(self.ranking)  # not always the same ones first
#            self.best_score = self.ranking[0].score()
        return self.size

    def update_(self, flagRanking = False, display=False):
        """ updates various facts about the group + positions
        """
        size = Group.update_ranks(self, flagRanking=flagRanking)
        if display:
            if flagRanking:	self.Scenario.update_positions(self.ranking, self.location)
            else:			self.Scenario.update_positions(self.members, self.location)
        # updating social links
        for m in self.members:	m.checkNetwork(membershipFunction=self.isMember)
        return size

    def remove_(self, memberNbr):
        " An individual is removed from the group and his parents' family trees "
        indiv = self.whoIs(memberNbr)
        for parent in self.members:
            parent.removeChild(indiv)
        return EG.EvolifeGroup.remove_(self, memberNbr)

########################################
########################################
########################################

class Population(EP.EvolifePopulation):
    """ Defines the population of agents
        This is the level at which 'life_game' is played
    """

    def createGroup(self, ID=0, Size=0):
        " Calling local class 'Group' "
        return Group(self.Scenario, ID=ID, Size=Size)

########################################
########################################
########################################

def Start(Gbl = None, PopClass = Population, ObsClass = None, Capabilities = 'PCGFN'):
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
