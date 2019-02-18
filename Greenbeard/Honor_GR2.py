
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
Self-sacrifice is completely 'exogenous'
"""

import sys

import Honor_GR as Hon
import SelfSacrifice_v00 as Base
sys.path.append('..')
sys.path.append('../../..')

from Evolife.Tools.Tools import percent


class Scenario(Hon.Scenario):

    def sacrifices(self, members):
        " Heroes aren't in the population under study "
        self.honoring_simple(members)
        self.interactions(members, self.Parameter('Rounds'))
    
    def honoring_simple(self, members):
        for Patriot in members:
            maxvalue = 2 **	self.Parameter('GeneLength') - 1
            max_offering = Patriot.gene_value('Honoring') / maxvalue * 10
            offering = min(self.endowment(Patriot), max_offering)
                # you can't cut off your arm twice
            Patriot.SignalLevel += offering
            #print(offering)
            # By doing so, a patriot signals his/her patriotism to others, which they will take into account when choosing friends

    def evaluation(self, indiv, members):
       
        indiv.score(- self.costSignal(indiv))
        
        if indiv.best_friend() is not None:
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



if __name__ == "__main__":
    print(__doc__)

    #############################
    # Global objects			#
    #############################
    Gbl = Scenario()
    Base.Start(Gbl, Hon.H_Population)

    print("Bye.......")

