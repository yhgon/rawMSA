# rawMSA: end-to-end Deep Learning makes protein sequence profiles and feature extraction obsolete

this is fork from [official source](https://bitbucket.org/clami66/rawmsa/src/master/)

This repository contain all the information about the datasets and the models used in the [paper](https://www.biorxiv.org/content/10.1101/394437v2.full)[pdf](https://www.biorxiv.org/content/10.1101/394437v2.full.pdf). 


 * The folder datasets contains the lists of proteins used in the 5-fold crossvalidation and the scripts necessary to produce the correct alignments and input files in the correct ".num" format
 * The folder scripts contains the python and bash scripts to run predictions and ensembling from the models
 * The folder models contains .h5 models for keras/tensorflow for both the CMAP and SS-RSA networks. These models are binary files that might not work on some keras/tensorflow versions. Send us an email if that is the case.

The full hdf5 dataset containing the SS and RSA classes, as well as the MSA inputs to the SS and RSA models, is too large to be kept on git (150 GB approx.) and can be found here: http://duffman.it.liu.se/rawmsa/

Contact: claudio (dot) mirabello [at] liu (dot) se for original authors. 
