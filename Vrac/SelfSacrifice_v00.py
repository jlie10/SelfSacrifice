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
And families are (exact) genetic relatives
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
import Evolife.Genetics.DNA as Gen

from Evolife.Tools.Tools import percent, chances, decrease, error

class Scenario(ED.Default_Scenario):

########################################
#### General initializations and visual display ####
########################################
    def __init__(self):
        # Parameter values
        ED.Default_Scenario.__init__(self, CfgFile='_Params.evo')	# loads parameters from configuration file

    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('SelfSacrifice'), ('Genome', 100)] 		# gene length (in bits) is read from configuration

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
            #m[1].location = (start_location + m[0], m[1].LifePoints)
            #m[1].location = (start_location + m[0], m[1].HeroesRelatedness)
            #m[1].location = (start_location + m[0], m[1].gene_value('SelfSacrifice'))
    
    #### For test
    def remove_agent(self, agent):
        " action to be performed when an agent dies "
        #print(agent.LifePoints)
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
        self.sacrifices(members)
            # Social interactions between the living (3)
        #### integrated into self.sacrifices (nothing here)
        # Last: work out final tallies (4)
        for indiv in members:
            self.evaluation(indiv, members)
        # Scores are translated into life points, which affect individual's survival
        #self.lives(members)
        self.lives_simple(members)
#		for i in members:
#			print(i.score())
#			print(i.LifePoints)
#			print('\n')

########################################
##### Life_game #### (1) Initializations ####
########################################
    def prepare(self, indiv):
        """ Defines what is to be done at the individual level before interactions
            occur - Used in 'start_game'
        """
        indiv.score(10, FlagSet = True)	# Sets score to 10
        indiv.Admiration = 0
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
        if p!=1: q = 1 - exp((log(1-p))/self.Parameter('AgeMax')*(1-percent(self.Parameter('SacrificeMaturity'))))  # => proba p de mourir a cause du gene
        else: q = 1
        bool = q > random() and (indiv.age > ((percent(self.Parameter('SacrificeMaturity')) * self.Parameter('AgeMax'))))

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
        for indiv in members:	# Deciding who are the population's heroes
            if indiv.SelfSacrifice:	# indiv is already a hero (that sacrificed at an earlier round)
                Heroes.append(indiv)
                Cowards.remove(indiv)
            elif self.selfSacrifice(indiv):	# indiv is not already a hero but is given an opportunity to be one
                Heroes.append(indiv)
                Cowards.remove(indiv)
        # In return, heroes are honored (admired) by society
        self.honoring(Cowards, Heroes)
        # The rest of society interacts (builds friendships) - see 3
        self.interactions(Cowards, self.Parameter('Rounds'))

#####
    def honoring_eaf(self, patriots, heroes):
        """ Simpler version where past heroes and present heroes don't compete
            Past heroes just add bonus points ---> can explode ?
        """
        social_admiration = self.Parameter('Admiration')
        self.pantheon(heroes, social_admiration, 0, self.Parameter('HeroCompetivity'))
        self.pastScores(patriots)

    def pastscores(self, patriots):
        for indiv in patriots:
            indiv.score(+ indiv.PastScore)
####
    def honoring(self, patriots, heroes):
        """ Honoring of heroes - exogenous here
            Determines total social admiration heroes will 'compete' over (see 'honoring')
            Used in 'sacrifices'
        """
        # Admiration is a social constant
        social_admiration = self.Parameter('Admiration')
        #social_admiration = self.Parameter('Admiration')*self.Parameter('PopulationSize')
        #social_admiration = self.Parameters('Admiration')*len(patriots)
        
        # Heroes compete for admiration
        if patriots:
            past_heroes = max([i.HeroesWitnessed for i in patriots])
        else:
            past_heroes = 0
        remaining_admiration = self.pantheon_simple(heroes, social_admiration, past_heroes)
        #remaining_admiration = self.pantheon(heroes, social_admiration, past_heroes, self.Parameter('HeroCompetivity'))
        
        # Patriots witness heroes' sacrifice
        if heroes:
            for indiv in patriots:
                indiv.HeroesWitnessed += len(heroes)

        # Alive individuals start off with indirect benefits from past sacrifices
        self.pastSpillover(patriots, remaining_admiration)

    def pantheon_simple(self, heroes, social_admiration = 0, past_heroes = 0, discount = 0.5):
        """ Heroes 'compete' for admiration, including with heroes of the past
            (those that society remembers)
            Simple equalitarian version         
            Used in 'honoring'
        """
        tot_heroes = len(heroes) + past_heroes
        if tot_heroes == 0:
            return  0
        
        share_past = past_heroes / tot_heroes * discount * social_admiration
        share_present = social_admiration - share_past
        for Hero in heroes:
            Hero.Admiration = share_present / len(heroes)
        print('There are {} heroes \n'.format(len(heroes)))
        return share_past

    def pantheon(self, heroes, social_admiration = 0, past_heroes = 0, competivity_ratio = 0, discount = 0.5):
        """ Heroes 'compete' for admiration, including with heroes of the past
            (those that society remembers)
            They have no control over which share of the pie they will receive
            Used in 'honoring'
        """
        #if not heroes:
        #   return
        tot_heroes = len(heroes) + past_heroes
        if tot_heroes == 0:
            return  0
        AllHeroes = heroes[:] + list(range(past_heroes))
        shuffle(AllHeroes)  # Hero order is random

        equa = 1 - competivity_ratio / 100.0
        if equa == 1:	# The pantheon is equalitarian
            #tot_weights = tot_heroes
            tot_weights = len(heroes) + past_heroes * discount      # Time discounted version --- others to modify as well
        elif equa >= 0 and equa < 1:
            tot_weights = (1-(equa)**tot_heroes) / (1 - equa)	# Geometric sum (1 if equa is 0)
        else:
            error('competivity_ratio must be between 0 and 100')
        
        #best_weight = 1 / tot_weights
        best_weight = 1 / len(heroes)               # only works for equalitarian pantheon...
        remaining_admiration = 0
        for Hero in AllHeroes:
            if type(Hero) == Individual:
                Hero.Admiration = best_weight * social_admiration
            else:
                remaining_admiration += best_weight * social_admiration * discount
            best_weight = equa * best_weight

        return remaining_admiration


    def pastSpillover(self, relatives, admiration = 0, heredity = 1):
        """ Relatives of heroes fallen in the past benefit from their sacrifice
            depending on genetic relatedness
            Used in 'honoring'
        """
#        tot_benef = admiration * heredity
#        # Some admiration is 'lost'     for descendants (the goat is eaten without them, people they will never meet talk about the heroes' values...)
        if not relatives:
            return # no surviving relatives for 'admiration' to spillover to
        if admiration == 0:
            return # all social admiration 'taken up' by recent heroes
        tot_weights = 0
        for indiv in relatives:
            #tot_weights += max(1, indiv.HeroesRelatedness)      # TEST
            tot_weights += indiv.HeroesRelatedness
        if tot_weights == 0:
            return
        for indiv in relatives:
            indiv.score(+ indiv.HeroesRelatedness / tot_weights * admiration)

########################################
##### Life_game #### (3) Social interactions ####
########################################
    def interactions(self, members, nb_interactions = 1):
        """	Defines how the (alive) population interacts
            Used in 'life_game'
        """
        for Run in range(nb_interactions):
            if not members: return
            Fan = choice(members)
            # Fan chooses friends from a sample of Partners
            Partners = self.partners(Fan, members, int(percent(self.Parameter('SampleSize')\
                                                                    * (len(members)-1) )))
            self.interact(Fan, Partners)

    def interact(self, indiv, partners):
        """ Nothing by default - Used in 'interactions'
        """
        pass

    def partners(self, indiv, members, sample_size = 1):
        """ Decides whom to interact with - Used in 'interactions'
            By default, a sample of partners is randomly chosen
        """
        # By default, a partner is randomly chosen
        partners = members[:]
        partners.remove(indiv)
        if sample_size > len(partners):
            print(len(partners))
            return partners
            #error('SampleSize is too large (should be between 0 and 100)')
        if partners != []:
            return sample(partners, sample_size)
        else:
            return None

########################################
##### Life_game #### (4) Computing scores and life points ####
########################################
    def evaluation(self, indiv, members):
        """ Implements the computation of individuals' scores
            Used in 'life_game'
        """
        if indiv.SelfSacrifice:
            Beneficiaries = self.beneficiaries(indiv, members)
            self.spillover(indiv, Beneficiaries, indiv.Admiration, percent(self.Parameter('SacrificeHeredity')))
            indiv.score(0, FlagSet = True) ### Should be useless...

    def beneficiaries(self, Hero, members):
        #PotentialRelatives = []        # useful if several groups to which repro is limited
        #for indiv in members:
        #    if indiv.ID[0] == Hero.ID[0]:
        #        PotentialRelatives.append(indiv)
        PotentialRelatives = members[:]
        for indiv in members:
            if indiv.SelfSacrifice: # Heroes don't survive to receive points
                PotentialRelatives.remove(indiv)        
        return PotentialRelatives

    def spillover(self, Hero, beneficiaries, admiration = 0, heredity = 1):
        """ A hero's descendants benefit from his or her sacrifice,
            proportionally to how much he or she is honored / admired
            and depending on how close they are to the hero in the family tree
            Used in 'evaluation'
        """
#        tot_benef = admiration * heredity
#        # Some admiration is 'lost' for descendants (the goat is eaten without them, people they will never meet talk about the heroes' values...)   
        tot_weights = 0
        hero_genome = Hero.get_DNA()[self.Parameter('GeneLength'):]

#### TEST average rel
        #L = []
        #for indiv in beneficiaries:
        #    genome = indiv.get_DNA()[self.Parameter('GeneLength'):]
        #    r = self.DNA_test(hero_genome, genome)
        #    L.append(r)
        #print(L)
        #print(sum(L)/float(len(L)))
                        #### C'est la merde
###
        Benef = beneficiaries[:]
        for indiv in Benef:
            genome = indiv.get_DNA()[self.Parameter('GeneLength'):]
            share = self.DNA_r_eaf(hero_genome, genome)
            #share = self.DNA_r_eaf2(hero_genome, genome)

            if share == 0:
                beneficiaries.remove(indiv)
            else:
                tot_weights += share
        if tot_weights == 0:
            return # Hero has no kin for 'admiration' to spillover to
        print('{} has {} beneficiaries \n'.format(Hero.ID, len(beneficiaries)))
        score = 0
        for relative in beneficiaries:

            rel_genome = relative.get_DNA()[self.Parameter('GeneLength'):]
            #share = self.same_family(hero_genome, genome)
            #if indiv.gene_value('SelfSacrifice') == 0:
            ##       share = 0 #### CHEAT 
            share = self.DNA_r_eaf(hero_genome, rel_genome)
            #share = self.DNA_r_eaf2(hero_genome, rel_genome)
### Test child                        
            #if share>0.7: 
            #    print(Hero.isChild(relative))
            #    print(indiv.HeroesRelatedness)
            #    print('\n')
### 
            relative.score(+ share / tot_weights * admiration)
                        # PB WITH TOT W // why aren't they removed ??
            relative.HeroesRelatedness += share
            score += relative.score()
        print(score/len(beneficiaries))

    def DNA_test(self, gen1, gen2, length = 100):
        r = 0
        for i in range(length):  # both sequences should be of length 100
            if gen1[i] == gen2[i]:
                r += 1
        r = r / length
        return r

    def DNA_r_eaf(self, gen1, gen2, length = 100, noise = 10):
        r = 0
        for i in range(length):  # both sequences should be of length 100
            if gen1[i] == gen2[i]:
                r += 1
        r = r / length
        if r < 0.550:
        #if r - percent(self.Parameter('MutationRate')) - noise/length < 0.575:
            return 0
        #else: print(r)
        return 2 * (r - 0.5)

    def DNA_r_eaf2(self, gen1, gen2, length = 100, noise = 10):
        r = 0
        for i in range(length):  # both sequences should be of length 100
            if gen1[i] == gen2[i]:
                r += 1
        r = r / length
        if r < 0.9:
        #if r - percent(self.Parameter('MutationRate')) - noise/length < 0.575:
            return 0
        #else: print(r)
        return 2 * (r - 0.5)



############# Failed stuff #############


    def DNA_relatedness(self, gen1, gen2, length = 1000):
        " tentative avec crossovers "
        nb_tests = self.Parameter('NbCrossover')
        l = int(length / nb_tests + 1)
        max_seq = 0
        
        StartingPoints = sample(range(1,length), nb_tests)
        for i in range(nb_tests):
        #    common_seq = self.maxseq(StartingPoints[i], min(length, StartingPoints[i] + l), gen1, gen2)
        #    max_seq += common_seq / nb_tests
            common_seq = self.largest_seq(max(0, StartingPoints[i]), min(length, StartingPoints[i]+l), gen1, gen2)
            #if common_seq > max_seq: max_seq = common_seq
            max_seq += common_seq / nb_tests

        bool = self.DNA_r_distH(gen1, gen2, length)
        if not bool:
            return 0
        elif max_seq < 0.8 * l:
            return 0
        return 1

    def same_family(self, gen1, gen2, length = 100):
        r = 0
        for i in range(length):  # both sequences should be of length 1000
            if gen1[i] == gen2[i]:
                r += 1
        if r + self.Parameter('MutationRate') > 0.95 * length:
            return 1
        else:
            return 0
        




    def maxseq(self, start, end, gen1, gen2):
        max_seq = 0
        common_seq = 0
        for i in range(start, end):
            if gen2[i] == gen1[i]:
                common_seq += 1
            else:
                if common_seq > max_seq: max_seq = common_seq
                common_seq = 0
        return max_seq

    def largest_seq(self, start, end, gen1, gen2):
        right = 0
        left = 0
        for i in range(end - start):
            if gen2[start + i] == gen1 [start + i]:
                right += 1
            else:
                pass
            if gen2[start - i - 1] == gen1 [start - i - 1]:
                left += 1
            else:
                pass
        return left + right
    
    def DNA_r_distH(self, gen1, gen2, length = 1000):
        " Fails "
        r = 0
        for i in range(length):  # both sequences should be of length 1000
            if gen1[i] == gen2[i]:
                r += 1
        #print(r)
        r = r / length

        return r > 0.74

        if r > 0.95:
            return 1
        elif r > 0.90:
            return 0.5
        elif r > 80:
            return 0.25
        elif r > 50:
            return 0.125
        else:
            return 0
############
    def lives(self, members):
        """ Converts scores into life points - used in 'life_game'
        """
        if self.Parameter('SelectionPressure') == 0:
            return	# 'Selectivity mode' : outcomes depend on relative ranking  (see 'parenthood')
        AliveMembers = members[:]
        for hero in members:
            if hero.SelfSacrifice:
                hero.LifePoints = - 1 # hero dies
                AliveMembers.remove(hero)
        if not AliveMembers: return
        print('still here1  ')
        print(len(members))
        BestScore = max([i.score() for i in AliveMembers])
        MinScore = min([i.score() for i in AliveMembers])
        if BestScore == MinScore:
            return
        print('still here')
        #for indiv in AliveMembers:
            #indiv.LifePoints =  max(0, indiv.score() - 10) * self.Parameter('SelectionPressure') / (BestScore - MinScore)
        #    indiv.LifePoints = indiv.score() / 10 * self.Parameter('SelectionPressure')
        ############ = wierd : not differential death
        
        if BestScore - MinScore < 1: 
            print('arf')
            return   # maximum gains are negligeable
        SP = self.Parameter('SelectionPressure')
        for indiv in AliveMembers:
            score = indiv.score()
            if score < 20:
                indiv.LifePoints = SP / 4 * (score - MinScore) / float(BestScore - MinScore)
            else:
                indiv.LifePoints = SP * (score - MinScore) / float(BestScore - MinScore)
            print(indiv.LifePoints)

    def lives_simple(self, members):
        if self.Parameter('SelectionPressure') == 0:
            return	# 'Selectivity mode' : outcomes depend on relative ranking  (see 'parenthood')
        AliveMembers = members[:]
        for hero in members:
            if hero.SelfSacrifice:
                hero.LifePoints = -1 # hero dies
                AliveMembers.remove(hero)
        if not AliveMembers: return
        SP = self.Parameter('SelectionPressure')
        for indiv in AliveMembers:
            score = indiv.score()
            #if score<20:
            if score < 11:
                indiv.LifePoints = 0
            elif score < 100:
                indiv.LifePoints = SP * score / 500
            else:
                indiv.LifePoints = SP * score / 100
            #print(indiv.LifePoints)



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
        #print(len(candidates))
        #print('parenthood')
        return candidates

########################################
########################################
########################################

class DNA(Gen.DNA):
    
    def __init__(self, Scenario, Nb_nucleotides):
        self.Scenario = Scenario
        self.nb_nucleotides = Nb_nucleotides
        self.__dna = []
        Init_Families = self.Scenario.Parameter('InitFamilies', Default = None)
        excluded = self.Scenario.Parameter('GeneLength')
        if Init_Families:
            family_nb = randint(1, Init_Families)
            for i in range(self.nb_nucleotides):
                if i < excluded:    # SelfSacrifice gene
                        #self.__dna.append(randint(0,1))
                        #self.__dna.append(0)
                        #if family_nb ==1: self.__dna.append(randint(0,1))
                        if family_nb ==1 and i == 0: self.__dna.append(1)
                        #if family_nb !=1: self.__dna.append(1) # for test
                        #if family_nb !=1: self.__dna.append(randint(0,1)) # for test
                        else: self.__dna.append(0) # triche
                elif (family_nb - 1) * 1000 / Init_Families < i - excluded < family_nb * 1000 / Init_Families:
                        self.__dna.append(1)
                else:
                        self.__dna.append(0)
            return
        
        Fill = self.Scenario.Parameter('DNAFill', Default=-1)	# 0 or 1 or -1=random
        for pos in range(self.nb_nucleotides):
            if (Fill==1):	self.__dna.append(1)
            elif (Fill==0):	self.__dna.append(0)
            else:			self.__dna.append(randint(0,1))
        #if NUMPY:	self.__dna = numpy.array(self.__dna)	# doesn't seem to be verif y efficient !
            
    def noise(self, excluded = 0, maxloci = 10):
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

class Individual(EI.EvolifeIndividual, DNA):
    "   Defines what an individual consists of "

    def __init__(self, Scenario, ID=None, Newborn=True):
        self.SelfSacrifice = False
        self.Admiration = 0
        self.HeroesRelatedness = 0
        self.HeroesWitnessed = 0
        #self.PastScore = 0

        self.Children = []
        EI.EvolifeIndividual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
        DNA.__init__(self, Scenario, Scenario.geneMap_length())

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

    def update_(self, flagRanking = False, display=False):
        """ updates various facts about the group
        """
        # removing old chaps
        for m in self.members[:]:  # must duplicate the list to avoid looping over a modifying list
            if m.dead():	self.remove_(self.members.index(m))
            if m.SelfSacrifice:	self.remove_(self.members.index(m)) # heroes die ################### ??
        self.size = len(self.members)
        if self.size == 0:	return 0
        # ranking individuals
        if flagRanking:
            # ranking individuals in the group according to their score
            self.ranking = self.members[:]	  # duplicates the list, not the elements
            self.ranking.sort(key=lambda x: int(x.score()/10),reverse=True)
            if self.ranking != [] and self.ranking[0].score() < 15:           #### RANDOM THRESHOLD = 15
                # all scores are zero
                shuffle(self.ranking)  # not always the same ones first
            self.best_score = self.ranking[0].score()
        return self.size


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
                child.noise(excluded = self.Scenario.Parameter('GeneLength'), maxloci = self.Scenario.Parameter('GeneticNoise'))
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

__author__ = 'Lie and Dessalles'