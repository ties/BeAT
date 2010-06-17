echo "Starting database reset..."
rm beat/db.db
python beat/manage.py syncdb
export DJANGO_SETTINGS_MODULE=beat.settings

rm -rf beat/logs
rm -rf beat/git
mkdir beat/logs
mkdir beat/git
#mkdir beat/git/ltsmin

echo "... adding basic data..."
python db_defaults.py with_git ltsmin-1.5-20-g6d5d0c
python db_defaults.py with_git ltsmin-1.5-19-g0f5585
echo "... reading test logs..."
python filereader.py --noisy ltsmin-output/output.txt
# > log0.txt~
#echo "... generating random data..."
#python spawndata.py
#python spawndata.py
#python spawndata.py
if [ ! -z $1 ]
then
	echo "... reading provided logs..."
	python filereader.py --noisy $*
# > log1.txt~
fi
echo "... done!"
