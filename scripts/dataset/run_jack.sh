#!/bin/bash

#run jackhmmer on a fasta input,
#then format into .num format
#for rawMSA input
#Note: this is also using the reformat.pl
#script that comes with the hh-suite

id=`basename $1 .seq`
input=$1

OUTPUTDIR=$(dirname $input)
echo "Jack Output dir: $OUTPUTDIR"

DBDIR=./
REFORMAT="/home/claudio/hh-suite3/scripts/reformat.pl"

dbbase=`basename $database .cs219`

echo "Jack aligning target $id against DB $dbbase"

jackhmmer --cpu 4 -N 3 -E 1e-3 --incE 1e-3 -A $OUTPUTDIR/${id}_jack.sto $1 $DBDIR/uniref100.fasta
$REFORMAT -l 10000 $OUTPUTDIR/${id}_jack.sto $OUTPUTDIR/${id}_jack.a3m
egrep -v "^>" $OUTPUTDIR/${id}_jack.a3m | sed 's/[a-z]//g'   > $OUTPUTDIR/${id}_jack.aln

#filter out duplicate sequences, coverage < 50%
length=`head -1 $OUTPUTDIR/${id}_jack.aln | wc | awk '{ print $3 }'`
halflength=$((length / 2))

awk '!x[$0]++' $OUTPUTDIR/${id}_jack.aln > $OUTPUTDIR/${id}_jack.aln.filtered

awk -v hl=$halflength -F '-' 'NF-1 < hl {print $0}' $OUTPUTDIR/${id}_jack.aln.filtered > $OUTPUTDIR/${id}_jack.aln.filtered.coverage50

python3 letters_to_numbers_3000.py $OUTPUTDIR/${id}_jack.aln.filtered.coverage50 > $OUTPUTDIR/${id}_jack.num
