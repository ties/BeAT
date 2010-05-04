if [ ! -z "$1" ] && [ -d "$1" ] && [ ! -z "$2" ] && [ ! -z "$3" ]
then
	#fiddle with the arguments
	f=$1
	g=$2

	case $f in
		 */) f=$f;;
		 *) f=$f/;;
	esac
	case $g in
		 */) g=$g;;
		 *) g=$g/;;
	esac

	#print out
	echo "logs source: $f"
	echo "writing to dir: $g"
	echo "Call: $3 <model_filename>"

else
	#print error message
	echo "Error, invalid arguments. Usage:"
	echo "./logconvert.sh <source_dir> <target_dir> <call>"
	if [ -z "$1" ]
	then
		echo "empty argument <source_dir>"
	elif [ ! -d "$1" ]
	then
		echo "$1 is not a directory"
	elif [ -z "$2" ]
	then
		echo "empty argument <target_dir>"
	elif [ -z "$3" ]
	then
		echo "empty argument <call>"
	fi
	exit
fi


let counter=0

for i in $f*; do
	# if the log matches the regular expression '.*\.e[0-9]+$' (ie. ends with '.e' followed by digits)
	if [ ! -z $( echo "$i" | egrep '.*\.e[0-9]+$' ) ]
	then
		#produce a header and the log
		(
			echo "BEGIN OF HEADER"
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
			echo ToolVersion: ltsmin-1.5-a2f445c
			echo Call: memtime $3 $i
			echo "END OF HEADER"
			cat $i
			echo "REPORT ENDS HERE"
		) > "$i.eatme"
	((counter++))
	fi
done

if [ ! -e $g ]
then
	mkdir $g
fi 

mv -t$g $f*.eatme

echo "done! created $counter logs with header in $g, leaving the original ones in $f"
