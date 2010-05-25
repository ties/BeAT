del beat\db.db
python beat\manage.py syncdb
set DJANGO_SETTINGS_MODULE=beat.settings
mkdir logs
mkdir git\ltsmin
python db_defaults.py
python filereader.py --quiet ltsmin-ouput\output.txt
python spawndata.py
python spawndata.py
python spawndata.py
