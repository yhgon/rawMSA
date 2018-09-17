
from sys import argv, exit
from keras.models import load_model
from keras.models import Sequential, Model
from keras.layers import Input, average, maximum
from keras.utils.io_utils import HDF5Matrix
from collections import defaultdict
import glob

from numpy import newaxis
import numpy as np
import re

input_dataset = "train_test_sseq_rsa_3k.hdf5"

def ensembleModels(models, model_inputs):

    # collect outputs of models in a list
    yModels = [model(model_input) for (model, model_input) in zip(models, model_inputs)]
    # averaging outputs
    yAvg = average(yModels)
    # build model from same input and avg output
    modelEns = Model(inputs=model_inputs, outputs=yAvg, name='ensemble')

    return modelEns

all_models = glob.glob('../../models/ss/*window*[0-9].h5')

model_depths = [int(re.search("depth_(\d+)", model_path).group(1)) for model_path in all_models]
windows = [int(re.search("window_(\d+)", model_path).group(1)) for model_path in all_models]
model_folds  = [int(re.search("fold_(\d+)", model_path).group(1)) for model_path in all_models]
q3s  = [float(re.search("q3_(\d+\.\d+)", model_path).group(1)) for model_path in all_models]
vals = [float(re.search("val_(\d+\.\d+)", model_path).group(1)) for model_path in all_models]

models_dict = defaultdict(list)

for (mod, depth, fold, q3, val) in zip(all_models, model_depths, model_folds, q3s, vals):

    (models_dict[(depth, fold)]).append([mod, q3, val])

model_paths = {}
models = {}

for key in models_dict.keys():

    models_dict[key].sort(key=lambda x: x[2], reverse=True)

    modelTemp = load_model(models_dict[key][0][0])  # load model
    print(models_dict[key][0][0])
    modelTemp.name = "model_" + str(key[0]) + "_" + str(key[1])
    models[key] = modelTemp

print(models)

test_lists = ['../../dataset/testset_list_sseq_9885_by_superfamily_fold_{}_5'.format(i) for i in range(5)]

count = 0
q3_sseq = 0

q3_res_sseq = 0
count_res = 0

window = windows[0]

for f in range(5):

    models_thisfold = [models[(d, f)] for d in [100, 200, 500, 1000, 2000, 3000]]
    model_inputs_thisfold = [Input(shape=model.input_shape[1:]) for model in models_thisfold]

    modelEns_thisfold = ensembleModels(models_thisfold, model_inputs_thisfold)
    modelEns_thisfold.summary()
    modelEns_thisfold.compile(optimizer='rmsprop',
              loss='sparse_categorical_crossentropy',
              metrics=['sparse_categorical_accuracy'])


    test_list_file = open(test_lists[f])

    for target in test_list_file:

        X_batch = np.asarray(HDF5Matrix(input_dataset, 'inputs/' + target))  # length x max_depth
        length, max_depth = X_batch.shape[0], X_batch.shape[1]

        X_batch = np.lib.pad(X_batch, [(int(window / 2), int(window / 2)), (0, 0)], 'constant', constant_values=(0, 0))

        X = []

        for alignment_max_depth in [100, 200, 500, 1000, 2000, 3000]: 
            X_batch_windows = []

            for i in range(length):
                X_batch_windows.append(X_batch[i:i + window, :alignment_max_depth].reshape(window * alignment_max_depth))

            X.append(np.asarray(X_batch_windows))

        labels_sseq = np.asarray(HDF5Matrix(input_dataset, 'labels_sseq/' + target))

        res_sseq = modelEns_thisfold.evaluate([x for x in X], labels_sseq, verbose=0)

        count += 1
        q3_sseq += res_sseq[1]
        q3_res_sseq += int(round(res_sseq[1] * length))
        count_res += length
        print("{}: length {} q3 {} res {} avg_q3 {}".format(target.rstrip(), length, res_sseq[1], int(res_sseq[1] * length), q3_res_sseq/count_res))


print(str(q3_res_sseq/count_res))
