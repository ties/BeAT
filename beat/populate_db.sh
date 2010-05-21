# Absolute path to this script. /home/user/bin/foo.sh
SCRIPT=$(readlink -f $0)
# Absolute path this script is in. /home/user/bin
SCRIPTPATH='dirname $SCRIPT'

rm db.db
python manage.py syncdb
export DJANGO_SETTINGS_MODULE=settings
#if [[ $PYTHONPATH != *$SCRIPTPATH* ]]
#then
#	echo "FAIL"
#fi
mkdir logs
mkdir git
mkdir git\ltsmin
python db_defaults.py
python filereader.py --noisy ltsmin-ouput/output.txt > log0.txt~
python spawndata.py
python spawndata.py
python spawndata.py
if [ ! -z $1 ]
then
	python filereader.py --noisy $* > log1.txt~
fi
