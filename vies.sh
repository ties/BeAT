path=`pwd`
if [ -d $1 ]
then
	for i in $(ls -d $1/*/); do $path/pop_existing_db.sh $i* ; done
else
	echo "please provide a directory"
fi