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
11-03: implementing jeux a 2 vitesses : sacrifice Select // other ...
14-03: interactions a 2 comme dans Def_s...
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
        self.NbHeroes = 0 # Nb of heroes each round

    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('SelfSacrifice')] 		# gene length (in bits) is read from configuration

    def display_(self):
        disp = [(i+1,G.name) for (i,G) in enumerate(self.GeneMap)]
        L = len(disp)
        disp += [(L+1, 'NbHeroes')]
        return disp
        
    def local_display(self, ToBeDisplayed):
        " allows to diplay locally defined values "
        if ToBeDisplayed == 'NbHeroes':
            return self.NbHeroes # displaying a quantity that can be computed within the scenario
        return None
        
    def update_positions(self, members, start_location):
        """ locates individuals on an 2D space
        """
        # sorting individuals by gene value
        duplicate = members[:]
        duplicate.sort(key=lambda x: x.gene_value('SelfSacrifice'))
        #duplicate.sort(key = lambda x: x.ID)
        for m in enumerate(duplicate):
            m[1].location = (start_location + m[0], m[1].Reproductive_points )
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
##### Life_game ####
########################################
    def life_game(self, members):
        """ Defines one year of play (outside of reproduction)
            This is where individual's acquire their score
        """
        # First: make initializations (1)
        self.start_game(members)
        # Then: play multipartite game, composed of:
            # The sacrifices game (2):
        AliveMembers = self.sacrifices(members)
            # Social interactions between the living (3)
        for play in range(self.Parameter('Rounds', Default=1)):
            players = AliveMembers[:]	# ground copy
            shuffle(players)
            # Individuals engage in several interactions successively
            for indiv in players:
                Partner = self.partner(indiv, players)
                if Partner is not None:
                    self.interaction(indiv, Partner)
        # Last: work out final tallies (4)
        for indiv in AliveMembers:
            self.evaluation(indiv)
        # Scores are translated into life points, which affect individual's survival
        self.lives(AliveMembers)      
        #self.lives10(AliveMembers)  
#		for i in members:
#			print(i.score())
#			print(i.LifePoints)
#			print('\n')
        #Ages = [i.age for i in AliveMembers]
        #print(sum(Ages)/len(Ages))


########################################
##### Life_game #### (1) Initializations ####
########################################
    def prepare(self, indiv):
        """ Defines what is to be done at the individual level before interactions
            occur - Used in 'start_game'
        """
        #indiv.score(100, FlagSet = True)	# Sets score to 100 // osef here...
        indiv.Reproductive_points = 0
        #if indiv.Share < 0.1:
        #    indiv.Share = 0
        #indiv.Admiration = 0
        #indiv.SelfSacrifice = False #for probabilistic + 'castrated zombie' mode

    def start_game(self, members):
        """ Defines what is to be done at the group level each year
            before interactions occur - Used in 'life_game'
        """
        for indiv in members:	self.prepare(indiv)
        #print(len(members))
        #Ages = [i.age for i in members]
        #print(sum(Ages)/len(Ages))

########################################
##### Life_game #### (2) Self-sacrifices ####
########################################
            ## (2a) Individual propensity to self-sacrifice
    def deathProbability(self, indiv):
        """ Converts an individual's genetic propensity to self-sacrifice into a probability
            Used in 'selfSacrifice'
        """
        maxvalue = 2 **	self.Parameter('GeneLength') - 1
        return (indiv.gene_value('SelfSacrifice') / maxvalue)

    def selfSacrifice(self, indiv):
        """ An agent decides to make the ultimate sacrifice
            Self-Sacrifice is only a possibiltiy from a certain age (e.g. adulthood)
            and is controlled by the SelfSacrifice gene (see deathProbability)
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
            ## (2b) Population-level self-sacrifice game
    def sacrifices(self, members):
        """ Self-sacrifice 'game':
            Heroes may self-sacrifice "for the good of the group"
            In return they are admired - admiration is exogenous here
            Used in 'life_game'
        """
        Heroes = []
        Cowards = members[:]
        #shuffle(members)   # VARIANT : only some people can be heroes each turn ===> p ++
        #for indiv in members[:50]:    (not great)
        for indiv in members:	# Deciding who are the population's heroes
            if indiv.SelfSacrifice:	# indiv is already a hero (that sacrificed at an earlier round)
                Heroes.append(indiv)    # (useless here : for 'castrated Zombie' mode)
                Cowards.remove(indiv)
            elif self.selfSacrifice(indiv):	# indiv is not already a hero but is given an opportunity to be one
                Heroes.append(indiv)
                Cowards.remove(indiv)
        
        #if self.Parameter('Baseline')==0:
            ######## baseline tot_h around 0 version
        #    random_heroes = 1 + int ( self.Parameter('PopulationSize') * (self.Parameter('MutationRate') / 1000 ) / self.Parameter('GeneLength'))
        #    tot_heroes = self.inc_witness(len(Heroes)-random_heroes, Cowards, discount = percent(self.Parameter('Forgetfullness')))
        #    print('Society remembers {} voluntary heroes'.format(tot_heroes))   # Gives around 0 when A = 0...
        #else:
            ####### baseline > 0 version (20 with usual para)
        #    tot_heroes = self.inc_witness(len(Heroes), Cowards, discount = percent(self.Parameter('Forgetfullness')))
        #    print('Society remembers {} total heroes'.format(tot_heroes))   # Gives around 20 +/- when A = 0...
        
        self.inc_shares(Heroes, Cowards)
    
        # In return, heroes are honored (admired) by society
        #Admiration = self.honoring(Cowards, tot_heroes, LongTerm=self.Parameter('LongTerm'))
        Admiration = self.honoring(Cowards, len(Heroes))
        self.NbHeroes = len(Heroes)   # for display
        self.spillover(Cowards, Admiration, threshold = self.Parameter('ReproGainsThreshold'))
        self.kill_heroes(Heroes)
        return Cowards

    def inc_witness(self, new_heroes, members, discount = 0.5):
        #random_heroes = self.Parameter('PopulationSize') * (self.Parameter('MutationRate') / 1000 ) / self.Parameter('GeneLength')
        #print(random_heroes)
        #print('\n')
        past_heroes = max([i.HeroesWitnessed for i in members])
        #members.sort(key=lambda x: x.HeroesWitnessed, reverse = True)
        #past_heroes = members[10].HeroesWitnessed
        for indiv in members:
            indiv.HeroesWitnessed += new_heroes
        return past_heroes * (1-discount) + new_heroes

    def inc_shares(self, heroes, members):
        for Hero in heroes: # Children of heroes will benefit from their sacrifice
            for Child in Hero.Children:
                Child.Share += 1
                #Child.Share += percent(self.Parameter('SacrificeHeredity'))

    def honoring(self, worshippers, nb_heroes):
        if nb_heroes == 0: return 0 # no heroes to admire this round
        return self.Parameter('Admiration') * len(worshippers)

    def honoring_old(self, members, nbheroes, LongTerm = True):
        if LongTerm:
            return self.Parameter('Admiration') * nbheroes
        # 'long term' mode where what matters is how much heroes are remembered over the years
        # The more society remembers (honors...) its heroes, the more their descendants stand to gain

        else:
            return self.Parameter('Admiration') * len(members)
        # 'short term' mode where everything is as if all Alive membered equally admired the fallen
                ### SO H should be improtant ??? How ??? Just in share to children ??

    def spillover(self, members, admiration = 0, threshold = 10):
        #  Osef precision ? = useless complication ?
        tot_share = 0
        for indiv in members:
            tot_share += indiv.Share
            #tot_share += int(precision * indiv.Share)  # useless complication ??
            #tot_share += min(2, indiv.Share)
        if tot_share == 0:
            return
        #print(tot_share / len(members))
        for indiv in members:
            indiv.Reproductive_points += indiv.Share / tot_share * admiration
            #indiv.Reproductive_points += int(precision * indiv.Share) / tot_share * admiration      # useless complication ??    
            #indiv.score(+ indiv.Share  * admiration)  # TEST 
            #print(indiv.score())
            #print(indiv.Share)
            #print('\n')
            indiv.Reproductive_points = int(indiv.Reproductive_points /threshold) # Only points above threshold entail reproductive advantage 
                # OK ??

    def spillover_old(self, members, admiration = 0, precision = 1000):
        #  Abandonned : give only to x % (first)  
        tot_share = 0
        for indiv in members:
            #tot_share += indiv.Share
            tot_share += int(precision * indiv.Share)
            #tot_share += min(2, indiv.Share)
        if tot_share == 0:
            return
        #print(tot_share / len(members))
        for indiv in members:
            #indiv.score(+ indiv.Share / tot_share * admiration)
            indiv.score(+ int(precision * indiv.Share) / tot_share * admiration)            
            #indiv.score(+ indiv.Share  * admiration)  # TEST 
            #print(indiv.score())
            #print(indiv.Share)
            #print('\n')

    def kill_heroes(self, heroes):
        for Hero in heroes:
            #Hero.score(-1, FlagSet = True)
            Hero.LifePoints = -1

########################################
##### Life_game #### (3) Social interactions ####
#######################################
    def partner(self, indiv, members):
        """ Decides whom to interact with - Used in 'life_game'
        """
        # By default, a partner is randomly chosen
        partners = members[:]
        partners.remove(indiv)
        if partners != []:
            return choice(partners)
        else:
            return None
                    
    def interaction(self, indiv, partner):
        " Nothing by default - Used in 'life_game' "
        pass

########################################
##### Life_game #### (4) Computing scores and life points ####
########################################
    def evaluation(self, indiv):
        pass    # Reproductive points are computed in spillover (see sacrifices)

    def lives(self, members):
        """ Converts alive members' scores into life points - used in 'life_game'
        """
        return    # No LP here (see Endogene_2vit)
   
########################################
#### Reproduction ####
########################################
# Reproduction is already defined elsewhere, but some functions have to be overloaded to create local individuals
# This is the case with parenthood (here) and Group.reproduction
    def parenthood(self, RankedCandidates, Def_Nb_Children):
        """ Determines the number of children depending on rank
        Note: when Selectivity is 0 (as is the default), number of children does not depend on rank
        Using Selectivity instead of SelectionPressure leads to much faster albeit perhaps less realistic convergence
        (as having 1001 points is much better than having 1000...)
        """
        ValidCandidates = RankedCandidates[:]
        for Candidate in RankedCandidates:
            if Candidate.SelfSacrifice or Candidate.age < self.Parameter('AgeAdult'):
                #print('something')
                ValidCandidates.remove(Candidate)	# Children and (dead) heroes cannot reproduce
        candidates = [[m,0] for m in ValidCandidates]
        # Parenthood is distributed as a function of the rank
        # It is the responsibility of the caller to rank members appropriately
        # Note: reproduction_rate has to be doubled, as it takes two parents to beget a child
        for ParentID in enumerate(ValidCandidates):
            candidates[ParentID[0]][1] = chances(decrease(ParentID[0],len(ValidCandidates), self.Parameter('Selectivity')), 2 * Def_Nb_Children)
        #candidates[0][1] = 100
        #print(len(candidates))
        #print('parenthood')
        #print(candidates)
        #print(candidates[0][1])
        #print(candidates[-1][1])
        return candidates

########################################
########################################
########################################

class Individual(EI.EvolifeIndividual):
    "   Defines what an individual consists of "

    def __init__(self, Scenario, ID=None, Newborn=True):
        self.SelfSacrifice = False
        #self.Admiration = 0
        #self.LifePoints = randint(0, Scenario.Parameter('SelectionPressure'))
        
        #self.HeroesRelatedness = 0
        #self.HeroesWitnessed = 0
        #self.PastScore = 0

        self.Reproductive_points = 0
        self.Share = 0
        #if Newborn:
        #    self.LifePoints = 100 # Test vs morta infantile
        #else:
        #    self.LifePoints = 0 


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
    """

    def __init__(self, Scenario, ID=1, Size=100):
        EG.EvolifeGroup.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        " Calling local class 'Individual'"
        Indiv = Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
        # Individual creation may fail if there is no room left
        self.Scenario.new_agent(Indiv, None)  # Let scenario know that there is a newcomer (unused)
        return Indiv

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
                child.inherit_share(C[0],C[1], heredity = percent(self.Scenario.Parameter('SacrificeHeredity')))
                child.update()  # Computes the value of genes, as DNA is available only now
                if self.Scenario.new_agent(child, C):  # Let scenario decide something about the newcomer (not used here)
                        # Child is added to parents' children lists
                    C[0].addChild(child)
                    C[1].addChild(child)
            
                    self.receive(child) # Adds child to the group

########################################
########################################
########################################

class Population(EP.EvolifePopulation):
    """ Defines the population of agents
        This is the level at which 'life_game' is played
    """

    def __init__(self, Scenario, Observer):
        " Creates a population of agents "
        EP.EvolifePopulation.__init__(self, Scenario, Observer)
        self.Scenario = Scenario
        #self.Observer = Observer	####

    def createGroup(self, ID=0, Size=0):
        " Calling local class 'Group' "
        return Group(self.Scenario, ID=ID, Size=Size)

#    def reproduction(self):
#        " launches reproduction in groups "
#        for gr in self.groups:
#            gr.reproduction()
        #if self.popSize == 0:
        #	self.__init__(self.Scenario,self.Observer)
        #while self.popSize < self.Scenario.Parameter('PopulationSize'):
        #	for gr in self.groups:
        #		gr.reproduction()
#        self.update()
    
#    def life_game(self):
        # Let's play the game as defined in the scenario
#        members = []
#        for group in self.groups:
#            for indiv in group.members:
#                members.append(indiv)
        
#        self.Scenario.life_game(members)
        # life game is supposed to change individual scores and life points

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
