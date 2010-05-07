#!/bin/bash


function pbsgen() {
filename=$1.pbs
(
echo "#PBS -q default"
echo "#PBS -N $1"
echo "#PBS -l nodes=$2"
echo "#PBS -j oe"
echo "#PBS -W x=NACCESSPOLICY:SINGLEJOB"
echo
echo cd $PWD
echo echo "Setting stack to 64MB"
echo ulimit -s 65536
echo echo command: $*
shift
shift
echo $*
) >$filename
}


function suitegen(){
       base=$1
       lang=$2
       file=$3


       pbsgen $base-$lang-idx '1:E5335,walltime=4:00:00' memtime ${lang}2lts-grey $i
       pbsgen $base-$lang-idx-cache '1:E5335,walltime=4:00:00' memtime ${lang}2lts-grey --cache $i
       for vset in list tree fdd ; do
               pbsgen $base-$lang-$vset '1:E5335,walltime=4:00:00' memtime
${lang}2lts-grey --state vset --vset $vset $i
               pbsgen $base-$lang-$vset-cache '1:E5335,walltime=4:00:00' memtime
${lang}2lts-grey --state vset --vset $vset --cache $i
       done
       for order in bfs bfs2 chain ; do
               for vset in list fdd ; do
                       pbsgen $base-$lang-$order-$vset
'1:E5335,walltime=4:00:00' memtime
$lang-reach --order $order --vset $vset $i
               done
       done
       for W in 1 2 4 ; do
               pbsgen $base-$lang-mpi-$W-6
"$W:ppn=6:E5335,walltime=4:00:00" mpirun
-mca btl tcp,self memtime ${lang}2lts-mpi $i
               pbsgen $base-$lang-mpi-cache-$W-6
"$W:ppn=6:E5335,walltime=4:00:00"
mpirun -mca btl tcp,self memtime ${lang}2lts-mpi --cache $i
       done
}


function instgen() {
       base=$1
       file=$2
       for W in 1 2 4 ; do
               mkdir $base-mcrl-insts-$W-6
               cp $file $base-mcrl-insts-$W-6
               pbsgen $base-mcrl-insts-$W-6
"$W:ppn=6:E5335,walltime=4:00:00" memtime
instantiators -no-lts $PWD/$base-mcrl-insts-$W-6/$file
       done
}

for i in beem*.mcrl2 ; do
       base=`basename $i .mcrl2`
       echo $base
       mcrl22lps -vnDf $base.mcrl2 | lpssumelm -v | lpsconstelm -v >
$base.v1.lps
       java -jar jmcrl.jar $base.v1.lps $base.v1.tbf
       structelm -alt rw $base.v1.tbf | rewr -case  -alt rw | constelm  -alt
rw > $base.v2.tbf
#       tbf2lps -v $base.v2.tbf $base.v2.lps
done
for i in native*.mcrl2 ; do
       base=`basename $i .mcrl2`
       echo $base
       mcrl22lps -vnDf $base.mcrl2 | lpssumelm -v | lpsconstelm -v >
$base.v1.lps
       java -jar jmcrl.jar $base.v1.lps $base.v1.tbf
       stategraph -alt rw $base.v1.tbf | rewr -case  -alt rw | constelm  -alt
rw > $base.v2.tbf
#       tbf2lps -v $base.v2.tbf $base.v2.lps
done
for i in *.mcrl ; do
       base=`basename $i .mcrl`
       echo $base
       mcrl -tbf -stdout $i > $base.stack.tbf
       mcrl -regular -nocluster -stdout $i | constelm | parelm | stategraph |
constelm > $base.tbf
done
for i in *.lps ; do
       base=`basename $i .lps`
       echo $base
       pbsgen $base-lps2lts-jittyc '1:E5335,walltime=4:00:00' memtime lps2lts
-v --rewriter=jittyc $i
       pbsgen $base-lps2lts-jittyc-ftree '1:E5335,walltime=4:00:00' memtime
lps2lts -v -ftree --rewriter=jittyc $i
       suitegen $base lps $i
done
for i in *.tbf ; do
       base=`basename $i .tbf`
       echo $base
       pbsgen $base-mcrl-inst '1:E5335,walltime=4:00:00' memtime
instantiator - $i
       instgen $base $i
       suitegen $base lpo $i
done
for i in *.b ; do
       base=`basename $i .b`
       echo $base
       pbsgen $base-divine '1:E5335,walltime=4:00:00' memtime divine.generator
-q -S $i
       suitegen $base nips $i
done
for i in *.dve ; do
       base=`basename $i .dve`
       echo $base
       pbsgen $base-divine '1:E5335,walltime=4:00:00' memtime divine.generator
-q -S $i
done
