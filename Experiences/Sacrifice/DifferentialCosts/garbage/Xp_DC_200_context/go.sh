#echo usage: sh go.sh <Typical_xxx.evo> <fich.evm> <python program>
#echo or
#echo usage: sh go.sh <program and config name (no ext)>
echo lancement d une experience
#cd /run/user/1000/gvfs/sftp:host=lame10.enst.fr/cal/homes/jpanis/Evolife/Other/2vit
nohup nice sh ./Explore.sh $1.evo $1.evm $1.py &
