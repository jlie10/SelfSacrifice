#!/bin/bash


if [[ $* = "" ]]
then
	echo Usage: "`basename $0` <MachineListFile>  [<MachineListFile> ...]" 
else

	rm -f EvoGen.dat
	rm -f batch.log  
	rm -f stop
	rm -f fini

	printf "launching python jobs on various machines listed in: "
	for MachList in $*
	do
		printf "$MachList "
	done
	echo ...

	sleep 4

	for MachineList in $*
	do
		for machine in `cat $MachineList`
		do
			if [[ $machine = \#* ]]
			then
				continue
			fi
			echo trying $machine
			#ping -c 1 $machine && Alive = 1
			#if [ "`ping -c 1 $machine | tail -6c`" = "alive" ]
			if [ "`ping -c 1 $machine | tail -3c`" = "ms" ]
			then 
				if test `echo $machine | grep -i lame`
				then
					nbprocess=16
				else
					nbprocess=2
				fi
				# if [[ $MachineList = MachineNames3.txt ]]
				count=0
				while [ $count -lt $nbprocess ]
				do
					echo $machine $count
					# actualisation des fichiers ?
					ssh jld@$machine ls > /dev/null
					ssh jld@$machine sh ~/Expe/Evolife/Other/SocialNetwork/go.sh SocialRunaway.evo SocialRunaway.evm SocialRunaway.py >> batch.log &
					sleep 4
					count=`expr $count + 1`
				done
				NbJ=`ssh jld@$machine ps -u jld | egrep python | wc -l`
				if [ $NbJ != 0 ]
				then
					echo XXXXXXXX $machine $NbJ
				else
					echo ........ \($machine\)
				fi
			fi
		done
	done
fi
