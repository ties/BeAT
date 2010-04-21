rm db.db
python manage.py syncdb
export DJANGO_SETTINGS_MODULE=settings
python file_to_db.py
python filereader.py --quiet ltsmin-ouput/output.txt
