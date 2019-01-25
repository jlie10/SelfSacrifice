Self-sacrifice
===========================

Throughout history, people have been willing to lay down their lives for the sake of their groups or ideology (for a review, see [Whitehouse, 2018](https://www.ncbi.nlm.nih.gov/pubmed/29409552)). Whether hailed as heroes or reviled as terrorists (oftentimes both, depending on the group), self-sacrifiers are generally young, ambitious male adults. Put together, these facts seem to underlie the incompleteness of proximal explanations (e.g. in termes of the contents of a specific ideology) and the inadequateness of a 'pathological' vision of self-sacrifice (whereby self-sacrifice results from unadaptive behavior and/or from miscalculations).

Could self-sacrifice therefore have a biological function? This project sets the groundwork for investigating the (individual) biological motivations that may underlie self-sacrifice (which need not coincide with its moral motivations, which may be geared towards the collective), following a costly social signal model (e. g. [Dessalles, 2014](https://onlinelibrary.wiley.com/doi/full/10.1111/evo.12378). Social signals are meant to attract friends ; in cases wheere the signaled quality correlates with the audience's fitness, such a quality will be in social demand and signaling can therefore bring benefits in terms of social status.

However, in the case of self-sacrifice, signalers do not survive to enjoy these potential benefits. An additional hypothesis is needed - we propose that social status be in part inherited. And, to explain why a martyr's children may be in social demand, we propose another additional hypothesis - namely that individuals may want to signal their patriorism by honoring heroes, which may 'spill over' to their desendants (more details later).

We program two scenarios, using [Evolife](https://evolife.telecom-paristech.fr/). A simplified scenario establishes the initial framework of the study. A second scenario builds on this base, aiming for a plausible explanation of self-sacrifice.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

[Self-Sacrifice](#self-sacrifice)
  - [Evolife](#Evolife)
  - [Base scenario](#base-scenario)
    - [(2a-i) Individual propensity to self-sacrifice](#2a-i)
    - [(2b-ii) Population-level self-sacrifice game](#2a-ii)
    - [(3) Computing scores](#computng-scores)
  - [Actual scenario](#actual-scenario)
    - [Theoretical argument](#pseudowords)
    - .....
  - [Previous attempts](#initial-attempts)
    - [Social game](#pseudowords)
    - [Evolife scenario](#pseudowords)
  - [Conclusion](#conclusion)


<!-- markdown-toc end -->


## Evolife

Evolife has been developed by Jean-Louis Dessalles in order to study various evolutionary phenomena. It is written in Python, and can be downloaded [here](https://evolife.telecom-paristech.fr/Evolife.zip).

The core of Evolife is a genetic algorithm. Individual's behavior is controlled by a binary vector (genome). They live, reproduce sexually, and gain points in a life_game (see under).

Evolife implements two modes of selection:
    Ranking, whereby individuals are ranked according to their score and are granted a number of potential children that is a in increasing function of their rank - whose sloped is controlled by the `Selectivity` parameter.
    Differential Death, whereby score lead to life points that protect them from life hazards, thus increasing their life expectancy (and opportunities to reproduce) - relative gains are controlled by the `SelectionPressure` parameter.

While ranking allows for faster convergence, differential death seems more realistic - and will be the subsequent preferred mode of selection (with ranking, having 1 000 001 points is significantly better than having 1 000 000)

The code is organized in separated modules - a complete description, including of how to launch Evolife is available on the [site](https://evolife.telecom-paristech.fr).
A scenario such as the two written here, inherits from `Default_Scenario`. However, simply rewriting its functions does not allow to modify individuals, as will prove useful in our scenarios (adding a selfSacrifice boolean for instance) - see [Evolife scenario](#evolife-scenario) for a failed attempt. Another (initial) attempt unsuccessfully implemented a purely [Social game](#social-game), where individuals did not inherit from Evolife's  `Individual` module - and hence did not inherit from  `Genes `.

## Base scenario

In this simplified scenario, we suppose that admiration of martyrs is a social given (controlled by an `Admiration` parameter) - meaning that we will not implement the second-order signal here (see [Actual scenario](#actual-scenario)).

Instead, self-sacrifice of individuals leeds to competition for this exogenous version of social admiration. This does not benefit the martyrs (who die), but can benefit their children, who indirectly benefit from their ascendant being admired.

The base scenario is implemented in `SelfSacrifice_v0.py`.

The core of the script is the `life_game` function which is where individuals in a population acquire their score. It is launched every year.

    # Life_game
    """ Defines one year of play (outside of reproduction)
    		This is where individual's acquire their score
    """
    # First: make initializations (1)
    self.start_game(members)
    # Then: play multipartite game (2)
    self.sacrifices(members, self.Parameter('MaxHeroes')) 	# (2a) Decides who will self-sacrifice
    self.interactions(members, self.Parameter('Rounds'))	# (2b) Social interactions
    # Last: work out final tallies (3)
    for indiv in members:
      self.evaluation(indiv)
    # Scores are translated into life points, which affect individual's survival
    self.lives(members)

For both scenarios, important individual variables (e. g. score, admiration) impacting the multipartite game are reset using `start_game`. For this basic scenario where admiration is exogenous, social interactions (2b) are not implemented.


### (2a-i) Individual propensity to self-sacrifices

An individual's propensity to self-sacrifice for the group is controlled by his `SelfSacrifice` gene, `deathProbability` converts this gene's value into a number between 0 and 1. Self-sacrifice is only possible from a certain age (controlled by `SacrificeMaturity`).
We propose two 'modes':
    One 'probabilistic', where a individual's probability of martyrdom is the result of deathProbability.
    One 'binary', whereby having any non null value for the gene leads to martyrdom.

Because long-term gene levels in the population are the fruit of reproductive dynamics, and order to avoid bugs associated with every individual in a population dying at once, we propose that individuals who self-sacrifice not actually 'die' - but be excluded from reproduction that year. The cost of the signal is thus measured in terms of lost reproductive potential. Individuals who don't have the gene (have a null value) will not face any cost in this base scenario.

### (2a-ii) Population-level self-sacrifice game

This stage is implemented using three python function: sacrifices, honoring and pantheon. The first imlements self-sacrifices at the population level:

    # sacrifices
    def sacrifices(self, members, max_heroes=100):
  		""" Self-sacrifice 'game':
  			Heroes may self-sacrifice "for the good of the group"
  			In return they are admired - admiration is exogenous here
  			Used in 'life_game'
  		"""
  		Heroes = []
  		Cowards = members[:]
  		for i in range(min(max_heroes,len(members))):
  			Potential_Hero = choice(Cowards)
  			if self.selfSacrifice(Potential_Hero):
  				Heroes.append(Potential_Hero)
  				Cowards.remove(Potential_Hero)
  		# In return, heroes are honored (admired) by society
  		self.honoring(Cowards, Heroes)

`Honoring` calls `pantheon` with a local `social_admiration` variable, which represents the total amount of admiration that is 'avaialable' for heroes (to compete over). In this base scenario, this is a given (and is the product of an 'Admiration' parameter and total population size).

'Competition' between heroes for social admiration is defined by `pantheon`. Degree of competition depends on a `HeroCompetivity` parameter (0: equalitarian pantheon; 100: winner-takes-all; anything in between: geometric repartition).

    # pantheon
    def pantheon(self, heroes, social_admiration = 0, competivity_ratio = 100):
  		""" Heroes 'compete' for admiration
  			(They have no control over which share of the pie they will receive)
  			Used in 'honoring'
  		"""
  		if not heroes:
  			return
  		equa = 1 - competivity_ratio / 100.0
  		if equa == 1:	# The pantheon is equalitarian
  			tot_weights = len(heroes)
  		elif equa >= 0 and equa < 1:
  			tot_weights = (1-(equa)^len(heroes)) / (1 - equa)	# Geometric sum (python power symbol gave an error with markdown)
  		else:
  			error('competivity_ratio must be between 0 and 100')
  		best_weight = 1 / tot_weights
  		for Hero in heroes:
  			Hero.Admiration = best_weight * social_admiration
  			best_weight = equa * best_weight


### (3) Computing scores

Scores are calculated at the end of the 'year'. Here, the only reason to gain points is through a parents' (or more largely ascendants') sacrifice. This is done through `spillover`

    # spillover
    def spillover(self, Hero, admiration = 0, kin_transfer = 0.5):
      """ A hero's descendants benefit from his or her sacrifice,
        proportionally to how much he or she is honored / admired
        and depending on how close they are to the hero in the family tree
        Used in 'evaluation'
      """
      tot_benef = percent(admiration * self.Parameter('SacrificeHeredity'))
      # Some admiration is 'lost' for descendants (the goat is eaten without them, people they will never meet talk about the heroes' values...)
      if not Hero.Descendants:
        return	# Hero has no descendants for 'admiration' to spillover to
      tot_weights = 0
      for (Desc, gen) in Hero.Descendants:
        tot_weights += (kin_transfer)^gen
      for (Desc, gen) in Hero.Descendants:
        share = (kin_transfer)^gen	# share is coefficient of relatedness by default (depends on the 'KinSelection' parameter)
        Desc.score(+ share / tot_weights * tot_benef)




```{python}
""" Implementation of a lexical decision experiment. """

import random
import csv
import expyriment


STIM_FILE = 'stimuli.csv'
WORD_RESP = expyriment.misc.constants.K_j
NONWORD_RESP = expyriment.misc.constants.K_f
MAX_RESP_TIME = 2500
ITI = 1500

exp = expyriment.design.Experiment(name="Lexical Decision Task")

expyriment.control.initialize(exp)

trials = []

## Load the stimuli
with open(STIM_FILE, encoding="utf-8") as f:
    r = csv.reader(f)
    next(r)  # skip header line
    for row in r:
        cat, freq, item = row[0], row[1], row[2]
        trial = expyriment.design.Trial()
        trial.add_stimulus(expyriment.stimuli.TextLine(item))
        trial.set_factor("Category", cat)
        trial.set_factor("Frequency", freq)
        trial.set_factor("Item", item)
        trials.append(trial)

random.shuffle(trials)

exp.add_data_variable_names(['key', 'rt'])

## Run the experiment
expyriment.control.start()

expyriment.stimuli.TextScreen("Instructions", """You will see a series of written stimuli displayed at the center of the screen.

After each stimulus, your task is to press the right key ('J') if you think it is an existing word, the left key ('F') otherwise. Place now your index fingers on the keys 'F' and 'J'.

Press the spacebar when you are ready to start.""").present()

exp.keyboard.wait_char(' ')
exp.screen.clear()
exp.screen.update()

for t in trials:
    exp.clock.wait(ITI - t.stimuli[0].preload())
    t.stimuli[0].present()
    button, rt = exp.keyboard.wait([WORD_RESP, NONWORD_RESP],
                                   duration=MAX_RESP_TIME)
    exp.screen.clear()
    exp.screen.update()
    cat, freq = t.get_factor("Category"), t.get_factor("Frequency")
    ok = ((button == WORD_RESP) and (cat != 'PSEUDO')) or ((button == NONWORD_RESP) and (cat == 'PSEUDO'))
    exp.data.add([cat, freq, t.get_factor("Item"), button, ok, rt])

expyriment.control.end()
```



## CONCLUSION

It was a lot of work and we did not have time to implement all the thing we wanted to, notably:

* we wanted to write a script to analyse the data files and create a statistical report
* to include a training phase with feedback before the actual experiment
