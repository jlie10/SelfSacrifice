# SelfSacrifice

Study of the possibility of self-sacrifice being an ESS

The game is a ("purely") social game, with:
- fixed population size
- variables of interest to individuals computed via a social score, comprising ()
    - benefits of having descendants (see KinSelection parameter)
    - risk taken in the self-sacrifice game (several options)
    - benefit of having friends (JoiningBonus parameter)

If an agent "decides" (?) to self-sacrifice,
a permanent signal is emitted on behalf of his/her descendants.
Descendants form bonds based on these signals.

SignalInvestment (out of 100) is learned and corresponds to an agent's propensity to self-sacrifice (it is thus investment on the behalf of his/her descendants' signals)
When a self-sacrifice game occurs, it is taken into account to decide whether or not the agent will in effect self-sacrifice (several options)

Reproduction (adoption):
Prospective parents are ranked according to their score. A sample of the best scores can beget children via "adoption": a (or several) random other inidividual is then reset and designated as their child.

Options/variants (in the code):
- Amount of risk taken (computed as a social cost) can be calculated differently. By default risk = SignalInvestment * max(points,1)
- SelfSacrifice game (effect of SocialInvestment). By default, an agent engaging in the game will self-sacrifice if SignalInvestment is greater than 0.

New parameters:
- EnvironmentalRiskiness: 100*probability of a self-sacrifice game occuring at a given round
- InfantSacrificeValue: relative (signal) value (out of 100) of an average child sacrifice with respect to an adult one
- KinSelection: should be between 0 and 50. Aligns the interests of an agent with that of his/her descendants ; when it is equal to 50, a descendant's score is taken into account in that of an ascendant with a factor equal to their coefficient of relatedness
- SignalHeredity: mediates the relationship between an ascendant's sacrifice and the signal value given to descendants. Should be between 0 and 50. When equal to 50, self-sacrifice augments all descendants' signal value by the sacrificing agent signal value (which is a function of quality) times their coefficient of relatedness.
- ReproductionProbability: sample size that can adopt each year.
- ReproductionRate: impacts the number of children a couple up for adoption can have.
- Selectivity: defines how parenthood is biased towards individuals with high scores.
