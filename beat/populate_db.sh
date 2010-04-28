date
rm db.db
python manage.py syncdb
export DJANGO_SETTINGS_MODULE=settings
python file_to_db.py
python filereader.py --quiet ltsmin-ouput/output.txt > log0.txt~
if [ ! -z $1 ]
then
	for i in $1/*; do
		for j in $i/*; do
			python filereader.py --quiet $* > log1.txt~
		done
	done
fi
date
