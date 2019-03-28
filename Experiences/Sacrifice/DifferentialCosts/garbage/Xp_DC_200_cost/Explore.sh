# Usage: sh Explore.sh <Typical_conf_file.evo> <Meta_conf_file.evm> <Python Program>
count=0
echo `hostname`: Experience `basename $3` $count - `date` demarrage
#echo Pour tErminer faire:   touch fini   et attendre la fin de la simulation en cours
#echo En cas d urgence ajouter:   touch stop 
while [ $count -lt 6 ]
do
	if [ `date '+%H'` -eq 4 ]; then sleep  7200; fi
	#if [ `date '+%H'` -eq 5 ]; then sleep  7200; fi
	#if [ `date '+%H'` -eq 6 ]; then sleep  7200; fi
	#if [ `date '+%H'` -eq 7 ]; then sleep  7200; fi
	#if [ `date '+%H'` -eq 8 ]; then sleep 36000; fi
	#if [ `date '+%H'` -eq 9 ]; then sleep 32400; fi
	#if [ `date '+%H'` -eq 10 ]; then sleep 28800; fi
	#if [ `date '+%H'` -eq 11 ]; then sleep 25200; fi
	#if [ `date '+%H'` -eq 12 ]; then sleep 21600; fi
	#if [ `date '+%H'` -eq 13 ]; then sleep 18000; fi
	#if [ `date '+%H'` -eq 14 ]; then sleep 14400; fi
	#if [ `date '+%H'` -eq 15 ]; then sleep 10800; fi
	#if [ `date '+%H'` -eq 16 ]; then sleep 7200; fi
	#if [ `date '+%H'` -eq 17 ]; then sleep 3600; fi
	#if [ `date '+%H'` -eq 18 ]; then sleep 3600; fi
	printf "..."
	echo `hostname`: Experience `basename $3` $count - `date`
	python3 EvoGen.py -m $1 $2 _Params.evo
	nice python3 $3
	# actualisation des fichiers ?
	ls > /dev/null
	if test -f fini
	then break
	fi
	if test -f stop
	then break
	fi
	count=`expr $count + 1`
done
echo `hostname`: Experience `basename $3` $count - `date` terminee
# rm -f fini
