#!/bin/bash

# rm -f _pythonJobs

if [[ $* = "" ]]
then
	echo Usage: "`basename $0` <MachineListFile>  [<MachineListFile> ...]" 
else
	printf "looking for python jobs in these machines lists:" 
	echo $*
	for MachineList in $*
	do
		for machine in `cat $MachineList`
		do
			if [[ $machine = \#* ]]
			then
				continue
			fi
			#echo looking into $machine
			echo 
			#ping -c 1 $machine && Alive = 1
			#if [ "`ping -c 1 $machine | tail -6c`" = "alive" ]
			if [ "`ping -c 1 $machine | tail -3c`" = "ms" ]
			then 
				echo $machine
				ssh jld@$machine ps -u jld -o pid,cmd | egrep python
			fi
		done
	done
fi
