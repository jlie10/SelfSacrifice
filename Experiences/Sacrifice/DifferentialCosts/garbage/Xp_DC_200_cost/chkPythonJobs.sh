#!/bin/bash


if [[ $* = "" ]]
then
	echo Usage: "`basename $0` <MachineListFile>  [<MachineListFile> ...]" 
else
	echo looking for python jobs in various machines
	echo
	for MachineList in $*
	do
		for machine in `cat $MachineList`
		do
			if [[ $machine = \#* ]]
			then
				continue
			fi
			#echo looking into $machine
			# echo .
			#ping -c 1 $machine && Alive = 1
			#if [ "`ping -c 1 $machine | tail -6c`" = "alive" ]
			if [ "`ping -c 1 $machine | tail -3c`" = "ms" ]
			then 
				# actualisation des fichiers ?
				ssh jld@$machine ls > /dev/null
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
	echo
fi
