echo reading machine names from MachineNames$1.txt
for machine in `cat MachineNames$1.txt`
do
#	if [ `ping $machine 1 | grep alive` != '' ]; then echo $machine OKAY; fi
	echo .
	echo XXXXXXXXX    Connecting to $machine  XXXXXXXXXX
	ping -c 1 $machine && ssh $machine 
done
