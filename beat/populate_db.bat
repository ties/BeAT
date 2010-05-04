del db.db
python manage.py syncdb
set DJANGO_SETTINGS_MODULE=settings
python file_to_db.py
python filereader.update.py --noisy ltsmin-ouput\output.txt > log0.txt~