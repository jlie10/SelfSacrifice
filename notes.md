TODO:
- Interactions => more sym...
- Change exogene => more like maths
- Redo maths II
- maths with bruit explo
- plot old x2 : denun update; ap

   
JLD:
Honnete :
- pourrait etre honnete : avec autre histoire ? => serait segregation sociale entre P et NP : faudrait que se trahissent entre eux
- ici = signal pas honnete.
RMQ: a cause de la DEMANDE...
- cas honnete : 
    histoire differente
    avec RISQUE
        => distinguer conflits intergroupes ou pas: 
            dans la vraie vie, y a des gens honnetes et pas
            si DC++...
                + aller lyncher des gens: = ss2
                    ---> d'autant plus rentable de prendre ce risque pour les anciens
                    collabos : PAPON
            = meca RADICALISATION de la societe...
                si tlm lynche qlqn, si on s'y mele pas on se fera lyncher
                ou alors ss3 = pas envoyer ss2.. // police ss2...
                    => regime communiste : DENONCER qlqn qui ss2 pas => jackpot
METTRE un "honnete" entre "" des le debut => equilibre...

===> c'est pas vraiment que pas honnete : "non-informatif"
a cause de la radicalisation inter-groupe...


TODO restes :    
- Exog:
    comprendre pq p = rmax / 50 ...

- changer modele : > ... change grand chose ?        ========> SI: naze pour t=0..., a virer... : VT = pour la simulation seulement: l'enlever du raisonnement...?
- voire evolution NP avec DC...
- maths sans bruit : tlm a MO ?
    cf Gintis + Bowles 2001
- maths bruit d'app, explo...

- v2: with Alonepenalty, non-lin
    besoin de FV ? ---> tester sans...
    AlonePenalty = 0 ===> TOUT LE MONDE MEURE.... besoin de changer rounds... :/ + DNA Fill = -1...
        ou l'exclure de la reproductiono= ?

- simu: Judas fausse les calculs ? => vrai que assez relou... // + encore une fois FV dans v2...



2805: cf Gintis 2001 + Bowles
et aussi du coup depend du bruit d'apprentissage le MO +++++ ou juste MO

et DC + => pas de NP ??

La en principe tlm converge a MO y compris les NP...
mais y a BRUIT ---> 
essai DC = 0 ??? /// calculer le risque ???? avec bruit d'exploration... [ genre uniforme autour d'une fenetre...] : si ami autour de MO, je px pas deduire grand chose...

Mais pas de pb a pas avoir d'amis: .... => d'ou cv pas ...

+ dans simu: mort si pas d'amis // mort si un traitre ===========> tlm a MO ??

faire varier DC =========> a un certain stade tlm signale au meme niveau ??



Avec cette histoire :
    NP => benef pas si terrible...


Remplacer JB par peine si pas d'amis...
=> regler tq tlm emet a MO.... puis faire varier para un par un..



Signal honnete ou pas ????
- vu la crise, = dur d'assumer de pas etre patriote...
RADICALISATION => tlm envoie le meme signal...


[LORENZACCIO = traitre qui se sacrifie ?]



Preuve de concept pour SS1:
- enfant de heros ou pas... (pas de partage ---> nb de petits enfants...)
- R+ lie entre SS1 et SS2, meme si <> comme dans simulation...



MEMOIRE:
- ce serait tres facile de l'expliquer si GROUPE SEL.... mais marche pas...
[article : modele avant simu]



Prep 28-05:
    HYP FORTE = gene DEMAND non ?
    A partir de la, ca se deroule bien, math pour SS2...
    Et l'idee = que plus D augmente (car pb pour distinguer / car risques... pas trop ici en fait, risque = juste effet de seuil), plus on va pouvoir avoir des heros
        meme si la viennent un peu trop tous seuls


    SS1: calculs possibles ?

    Res: que / comment afficher ??

    Suite : complexifier le modele ?




27-05: pb pas de reinit pts repro ???
    bonne nouvelle en fait ? => pour ca que resultats trop grands sur trucs limites ??


To better understand: NEED JB ==> vrai benef a gagner la competition (asym) pour l'amitie...

Calculs version MO, avec pas de +F si NP:
    D = MO+ = ESS ---> P = D / NP = 0 ESS
        des que NbT > F / DC ...
    donc signal honnete
    et signal existe si / pour ... tq JB * k - c > 0
        et donc OK (avec H3), si Max_F * JB > MO+
            tests: HC 100 MaxF 10 / 10 1 OK
                    150 10 / 15 1 OK
                    180 10 non
                    18 1 un peu ?
                    190 10 non
                    19 1 ??? quasiment rien... mais un peu de suicides
                                        de facon generale, PLUS DE SUICIDES en mode 1 seul ami...
                    200 10 : non
                    20 1 : non ou presque, mais tjs des suivides....
                            ===> PREFERENCE TOUJORUS POUR 10 AMIS...

        ==> Pour avoir qu'un seul ami : baisser HC en fonction... (en gros regle de 3...)
        [verif mode calcul JLD: avec un seul gourou je pense...]
        
        ---> changer le nombre de gourous ???? = plus du tout symm...
            ... bof vu le scenario...
                mais du coup pq garder le cote compet ??


Nombre max de relations sociales entre patriotes = Max_F * N/2   ---> tout le monde peut avoir ses Max_F amis...
    peu de role joue par Max_F



Calculs version DP, avec pas de +F si NP:
    Benefices "directs" a signaler: Max_F * JB - cout ( pat)  * s
    ===> D > JB * Max_F / (HC * (1+DP))        ESS  quand NbT > DC / F
        tests: D et P augmentent quand DP baisse........................ MAIS PAS REMHEROES ???

        Hyp: si J = 0, D = Dmin au-dessus suffit, parce qu'on ne fait que perdre au final a attirer des amis pas cool
            [ GARDER J = 0 pour calculs ???? De toute facon c'est pas cool de se faire trahir par les autres...]

    B_NP(s) = B(s)_directs + (F- t * DC) * Max_F + JB * t / 2 * Max_F (si je peux trahir, je peux etre trahi...) ----- ca c'est si tlm signale // sinon ca s'annule si que des traitres
        
        ==> potentiel malhonnete si t <= F / (DC - 1/2*J)........... IMPOSSIBLE car t > F / DC


        POUR QUE SIGNAL MALHONNETE PUR : faut DC, pas MO, et aussi JUDAS > 2 * DC en gros...       <> Hyp implicite (points "voles", sans recompense de la Gestapo...)
            ---> une interpretation interessante : comment recompenser les taupes ? // un peu chelou, la se trahissent entre elles




D ++ quand DP -- : = PROPRE CE GENRE DE MODELE D'ORDRE 2 ?????? Y a des sacrifies ssi assez d'I...
    = mon paradoxe a moi ?




EXOGENOUS:
    Duh, p <=  r / (1+r) * f(S) .... pas tres gros donc...: avec pas invasion par mutant dans pop a 0.

    Duh2: A/T >= 1: avec tlm a 0, faut bien que augmente ///////////// demonstration ????... car avec petit A ca augmente vite vu que tlm admire, ok A*N > T mais bon

    Influence de h ????
        AN: H=0 => echec en gros ? // un peu moins avec Exog, meme si fluctu++
            H=100 => echec aussi, instable visiblement... // aussi avec Exog...
                                    d'ou FLUCUTUATIONS ++ ? 


Rappel : existence RGThreshold = parce que sinon truc binaire : A>0 ===> le max de heros...
La on peut faire un graphe.... plusieurs stades (nbH) selon A / T...

+ bizarre: si trop petit RGT, ca marche pas (?)

... = pb dans calculs, tout depend de tous les autres...


1) Tous a p:
    Peut etre envahi facilement si p > r / (1+r) * ( 1 - S / (S+1) / log(1+S)) = 8%...
2) Tous a 0:
    Peut etre envahi par p <  .... 29%
3) donc il existe un ESS non nul, avec p < 8 % ? ("strategie mixte")


r_max = (1+S) * r_min


4) : calcul a la con avec tous a p vs un p' : la si on sq p' est le meilleur, ca marche tjs...... => pb dans cette hypothese??


RESULTATS - cf mail:
- cutoff autour 15%.... OK, vu les maths
- itou pour cutoff de DC
- F pas tres int, vu que plus "asym" mtn
- ++ D qd DP --, lie a ++ cas ou traitres : risque de se tromper ---> (et la = fluctu stat)
- itou pour MO = 100 ? (osef)























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