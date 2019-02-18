
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
import random
import sys

import SelfSacrifice_v00 as Base
import SelfSacrifice_GR as SS
sys.path.append('..')
sys.path.append('../../..')

class Scenario(SS.Scenario):
    
    def genemap(self):
        """ Defines the name of genes and their position on the DNA.
        """
        return [('SelfSacrifice'), ('Honoring'), ('Patriotism')] 		# gene size is read from configuration

    def display_(self):
        #return [('red', 'SelfSacrifice'), ('blue', 'Honoring'), ('black', 'Patriotism')]
        return [('red', 'SelfSacrifice'), ('blue', 'Honoring')]

    def update_positions(self, members, start_location):
        """ locates individuals on an 2D space
        """
        # sorting individuals by gene value
        duplicate = members[:]
        #duplicate.sort(key=lambda x: x.gene_value('SelfSacrifice'))
        duplicate.sort(key=lambda x: x.gene_value('Honoring'))
        for m in enumerate(duplicate):
            m[1].location = (start_location + m[0], m[1].gene_value('Patriotism'))
            #m[1].location = (start_location + m[0], m[1].Patriotism)
            #m[1].location = (start_location + m[0], m[1].score())


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
        
        p = random.random()
        if p > 0.5: 
            indiv.Patriotism = 10
        else:
            indiv.Patriotism = 0
        #p = indiv.gene_value('Patriotism')
        #maxvalue = 2 **	self.Parameter('GeneLength') - 1
        #indiv.Patriotism = p / maxvalue * 10


if __name__ == "__main__":
    print(__doc__)

    #############################
    # Global objects			#
    #############################
    Gbl = Scenario()
    Base.Start(Gbl, SS.Patriotic_Population)

    print("Bye.......")



