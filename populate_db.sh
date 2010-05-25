python manage.py syncdb
export DJANGO_SETTINGS_MODULE=beat.settings

rm -rf logs
rm -rf git
mkdir logs
mkdir git
mkdir git/ltsmin

python db_defaults.py
python filereader.py --noisy ltsmin-output/output.txt > log0.txt~
python spawndata.py
python spawndata.py
python spawndata.py
if [ ! -z $1 ]
then
	python filereader.py --noisy $* > log1.txt~
fi
