let counter=0
if [ -d $1 ] && [ ! -z $1 ] &&	 ( [ ! -e ./tmp ] || ( [ ! -z $2 ] && [ ! -e $2 ]   ) )
then
	echo "working directory: $1"
else
	echo "invalid directory $1 or the ./tmp folder exists and the second argument points to something that exists or is not provided"
	echo "please provide a valid directory and target, or delete ./tmp"
	exit
fi

f=$1

if [ ! -e ./tmp ]
then
	g="./tmp"
else
	g=$2
fi

case $f in
     */) f=$f;;
     *) f=$f/;;
esac

for i in $f*; do
	(
		echo Nodename: $(uname -n)
		echo Hardware-name: $(uname -m)
		echo OS: $(uname -o)
		echo Kernel-name: $(uname -s)
		echo Kernel-release: $(uname -r)
		echo Kernel-version: $(uname -v)
		echo Hardware-platform: $(uname -i)
		echo Processor: $(uname -p)
		echo Memory-total: $(cat /proc/meminfo | grep MemTotal | tr -s " " | cut -d" " -f 2 -)
		echo DateTime: 2010 03 16 13 24 43
		echo Call: memtime dve-reach -c $i
		cat $i
		echo "REPORT ENDS HERE"
	) > "$i.eatme"
	((counter++))
done

mkdir $g

mv -t$g $f*.eatme

echo "done! created $counter logs with header in $g, leaving the original ones in $f"
