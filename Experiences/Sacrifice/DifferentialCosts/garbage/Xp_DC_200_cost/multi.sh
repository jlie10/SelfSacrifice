

for ((i=0 ; 10 - $i ; i++))
    do echo lancement de lexperience $i
    nohup nice sh ./Explore.sh $1.evo $1.evm $1.py &
    sleep 2
done