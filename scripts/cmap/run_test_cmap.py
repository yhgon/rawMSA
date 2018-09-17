#!/bin/bash

OUTPUTDIR=/CASP12/
export CUDA_VISIBLE_DEVICES="" #use CPU just to be safe on memory side
groupid="XXXX-XXXX-XXXX"
do_jack=1

for fasta in $OUTPUTDIR/fasta/*.seq; do

	TARGETDIR=$(dirname "${fasta}")
	id=`basename $fasta .seq`
	echo "Target id: $id"

	if [ ! -e $TARGETDIR/${id}.num ]; then

		echo "Running alignments"
		./run_hhblits.sh $fasta &> $TARGETDIR/${id}.hhlog

	fi


	if [ ! -e $TARGETDIR/${id}_jack.num ] && [[ $do_jack == 1 ]]; then

		echo "Running Jack alignments"
		./run_jack.sh $fasta &> $TARGETDIR/${id}.jacklog


	fi

	for model in ../../models/cmap/*.h5; do

		mod=`basename $model .h5`
		maxdepth=`echo $mod | grep -o "depth_[0-9]*" | head -1 | tr "_" " " | awk '{ print $2 }'`
		for alignment in $TARGETDIR/*[lk].num; do
			alid=`basename $alignment .num` #T0XXX or T0XXX_jack .num

			if [[ ! $alignment == *"jack"* ]] || [[ $do_jack == 1 ]]; then
				if [[ ! $alignment == *"jack"* ]] || [[ $maxdepth -gt 1 ]]; then
					if [ ! -e $TARGETDIR/${alid}_${mod}.cmap ]; then

						echo "Predicting target $id with model $mod, align $alid and maxdepth $maxdepth"
                                                echo "python3.5 predict_cmap.py $alignment $model $maxdepth &> $TARGETDIR/${alid}_${mod}.predictlog"

						python3.5 predict_cmap.py $alignment $model $maxdepth &> $TARGETDIR/${alid}_${mod}.predictlog

					fi
				fi
			fi
		done
	done

	echo "Ensembling predicted maps"
	length=`head -1 $TARGETDIR/${id}.num | wc | awk '{ print $2 }'`
	rm $TARGETDIR/${id}_ensemble.cmap

	python3.5 ensemble_maps.py $fasta $length $groupid &> $TARGETDIR/${id}.ensemblelog

done

