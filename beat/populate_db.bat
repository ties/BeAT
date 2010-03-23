rm db.db
python manage.py syncdb
set DJANGO_SETTINGS_MODULE=settings
python filereader.py --quiet ltsmin-ouput\output.txt