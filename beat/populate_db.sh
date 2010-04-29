date
rm db.db
python manage.py syncdb
export DJANGO_SETTINGS_MODULE=settings
python file_to_db.py
python filereader.py --quiet ltsmin-ouput/output.txt > log0.txt~
python spawndata.py
python spawndata.py
python spawndata.py
if [ ! -z $1 ]
then
	python filereader.py --quiet $* > log1.txt~
fi
date
