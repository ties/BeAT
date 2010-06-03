#PBS -q default
#PBS -N beat_{{ filename }}
#PBS -l nodes={{ nodes }}
#PBS -j oe
#PBS -o {{ filename }}.log
#PBS -W x=NACCESSPOLICY:SINGLEJOB