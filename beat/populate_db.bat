del db.db
python manage.py syncdb
set DJANGO_SETTINGS_MODULE=settings
mkdir logs
mkdir git
mkdir git\ltsmin
cd git\ltsmin
git init
cd ..\..
python db_defaults.py
python filereader.py --quiet ltsmin-ouput\output.txt
python spawndata.py
python spawndata.py
python spawndata.py
