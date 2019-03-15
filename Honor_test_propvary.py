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


""" Honor = test of jeu II
    proportion of patriots / non-patriots varies
    patriots = True Patriots / non-patriots = Traitors
"""
from random import random
import Exogene as Exo
import Honor as Base

import sys
sys.path.append('..')
sys.path.append('../../..')

from Evolife.Tools.Tools import percent

class Scenario(Base.Scenario):

    #def genemap(self):
    #    """ Defines the name of genes and their position on the DNA.
    #    """
     #   return [('Patriot'), ('Traitor')] 		# gene length (in bits) is read from configuration
    
   


    def evaluation(self, indiv):
        if indiv.best_friend() is not None:
                if not indiv.best_friend().SelfSacrifice:
                    indiv.best_friend().score(+ self.Parameter('JoiningBonus'))
            # NOT GOOD AT ALL ? Cv even when no traitors...
        " It's the end of the war: friends reveal themselves for who they really are "
        for Friend in indiv.friends.names():
            #print(Friend.Patriotism)
            if Friend.Patriotism == 0:
                if self.Parameter('DenunciationCost')==0: 
                    indiv.Executed = True   # infinite cost: indiv will be executed by the Gestapo
                else:
                    indiv.score(- self.Parameter('DenunciationCost'))
                    #print(indiv.score())
            else:
                # Friend is a true patriot who can vouch for you
                indiv.score(+ self.Parameter('FriendshipValue'))
                #print('\n')
        #indiv.detach()	# indiv quits his/her friends   # changed : now = erosion (in prepare)

class Individual(Base.Patriotic_Individual):
    "   Proportion of traitors varies / given at inception "

    def __init__(self, Scenario, ID, maxPatriotism = 100, Newborn=True):
        #self.IdNb = int( ID[2:]	)	# ID is constructed as Groupnumber_IdNb - there is always only 1 group
        Base.Patriotic_Individual.__init__(self, Scenario, ID=ID, Newborn=Newborn)

        if random() < percent ( Scenario.Parameter('NbTraitors') ):
            self.Patriotism = 0
        else:
            self.Patriotism = 1

class Group(Base.Group):

    def __init__(self, Scenario, ID=1, Size=100):
        Base.Group.__init__(self, Scenario, ID, Size)

    def createIndividual(self, ID=None, Newborn=True):
        # calling local class 'Individual'
        Indiv = Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
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

class Population(Base.Patriotic_Population):
    """ Defines the population of agents
    """

    def __init__(self, Scenario, Observer):
        " Creates a population of agents "
        Base.Patriotic_Population.__init__(self, Scenario, Observer)
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
    Exo.Start(Gbl, Population)