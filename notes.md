Seuil de r minimal
- 1/A pour pas dispa (sens ?)
- p < f(r) < r / (1+r) a l'equilibre ---> pour que cv disc. faut un truc minimal ?

Simplification :
    - osef tous les seuils pour l'instant...
        remplacer precision par THRESHOLD, for sacrifice
        du coup pas besoin d'autre seuil pour offering ? Pas de coeff mult en plus ?


0312
- Exogene : semble OK, graphes a faire... semble plus robuste qu'avant
    + en attente de version avec pop 1000
- Honor : P cv vers truc relativement petit / NP 0 quand MO en dessous d'un certain seuil
        cout assez faible ?
        ATTENTION A ROUNDS... -> finalement plus de detach / juste un peu d'erosion (sinon P grandit avec rounds)
    Version JB = 0 semble ne pas marcher (deux sgnx 0) => PROBLEMATIQUE OU NON ?
    Version Diffcosts non plus (deux sgnx 0)
    Version max in prepare : dishonest signaling

    GROS PROB : emerge meme quand FT = 0...
        => FAIRE QUE DU JB = 0 ???
            marche pas ...
                
- Endo : faut pas que appa n'importe comment...

Comment marche network ? // liens asymetriques = bien ??? (Followers)
    Indiv : already has friends... donc osef ? / d'ou le pb ?

Tests honor a la con :
- corr entre patriotism pote et score OK
- corr LP et score OK (mais pas enorme) in lives
- test lives 10 : pas mieux, rien n'emerge


TO DO : MATHS ---> pourquoi emerge avec JB 5 et c'est tout ? (en Diff cost aussi... )


0311
Results :
    Exo :
- f(r) avant tout
- f(S) aussi (S irrealiste -> bruit ... ou que au debut ?/ S faible plus faible)
- f(h) aussi : h = 100 => plus de bruit ?
- beaucoup plus stable avec N plus grand ? (test = 1)

=> VISUALISER NOMBRE DE HEROS ou un truc du style ---> PAS CLAIR LA si resultat...

Endo:
- pas la peine plein de rounds ? // carrement mx avec 100 > 1000 ??? (sur nb_h fixe)
- test nb_h fixe : ok ?
- evol sacri sans trop reste (tout a 1, avec MO 50, D 0) -> rajotuer un seuil minimal dans offering..
- v1 190311184130, cool image, mais 0 csv ?
- v1 190311184411, MO 50, D 500, signal pas honnete

=> DES QUE MO trop grand, pb d'honnete du signal ???
    C'est pbatique si signal 1 evolue alors que S2 pas honnete ??
            semble pas mal : on voit l'interet du cout +++
                tenter variante avec max score initial...
    Par conter un peu TROP FACILE de faire evol le sacrifice ??

Units ?
- S 1 D 10 : tout reste a 0 ? (bruit pour blanc) /  p = ?
- S 10 D 10 : pas bcp mx // P 1 = le facteur det probablement...
- tout 10, un peux mx ?????? bof
- D1 S10 : le plus stable semble-til... tjs pas facile ---> AUGMENTER r aussi..