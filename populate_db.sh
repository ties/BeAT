echo "Starting database reset..."
rm beat/db.db
python beat/manage.py syncdb
export DJANGO_SETTINGS_MODULE=beat.settings

rm -rf beat/logs
rm -rf beat/git
mkdir beat/git

echo "... adding basic data..."
python db_defaults.py with_git ltsmin-1.5-20-g6d5d0c
python db_defaults.py with_git ltsmin-1.5-19-g0f5585
echo "... reading real test logs..."
python filereader.py -v --dulwich ltsmin-output/brp.tbf-suite-cur.log
python filereader.py -v --dulwich ltsmin-output/brp.tbf-suite-prev.log

if [ ! -z $1 ]
then
	echo "... reading provided logs..."
	python filereader.py --noisy $*

fi
echo "... done!"
