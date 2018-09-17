#!/bin/bash

#run hhblits on a fasta input,
#then format into .num format
#for rawMSA input

id=`basename $1 .seq`
input=$1

OUTPUTDIR=$(dirname $input)

echo "Output dir: $OUTPUTDIR"
DBDIR=./
SCRIPTS=/HD/claudio/deep_contact/CASP13/scripts/


dbbase=`basename $database .cs219`

echo "Aligning target $id against DB $dbbase"

hhblits -diff inf -cov 50 -id 99 -cpu 4 -i $1 -d $DBDIR/$dbbase -oa3m $OUTPUTDIR/$id.a3m -n 3

egrep -v "^>" $OUTPUTDIR/$id.a3m | sed 's/[a-z]//g'   > $OUTPUTDIR/$id.aln
python3 letters_to_numbers_3000.py $OUTPUTDIR/$id.aln > $OUTPUTDIR/$id.num

