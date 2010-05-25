echo "Reading logs!"
export DJANGO_SETTINGS_MODULE=beat.settings
if [ ! -z $1 ]
then
	python filereader.py --noisy $* > log1.txt~
fi
echo "done!"
