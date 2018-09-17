from keras.models import Sequential, Model, load_model
from keras.layers import Input, Embedding, Flatten, Dense, Dropout, Activation, Reshape, LSTM, Conv2D, MaxPooling2D, Concatenate, Lambda, BatchNormalization, Add
from keras.layers.wrappers import Bidirectional

from keras.callbacks import TensorBoard
from keras.utils.io_utils import HDF5Matrix
from keras.utils.np_utils import to_categorical
from keras import backend as K
from numpy import newaxis

from sys import argv

import itertools
from time import gmtime, strftime, time

import imageio
import traceback

import numpy as np
import os

input = argv[1]
model = argv[2]
alignment_max_depth = int(argv[3])

out_path = os.path.dirname(os.path.abspath(input))
input_id = os.path.splitext(os.path.basename(input))[0]
model_id = os.path.splitext(os.path.basename(model))[0]

length = 0

input_aln_file = open(input)

def average_halves(matrix, length):

    averaged = (matrix + np.swapaxes(matrix, 1, 2))/2

    return averaged

def outer_sum(inputs):    
    """
    inputs: list of two tensors (of equal dimensions,
        for which you need to compute the outer product
    """
    x, y = inputs

    #                batch, window, newaxis, depth*filter_size
    outerSum = x[    :,      :, newaxis,                 :] - y[:,newaxis, :, :]

    return outerSum

def masked_sparse_categorical_crossentropy(y_true, y_pred):

    mask = K.tf.ones_like(y_true[0,:,:,0])

    mask = K.tf.matrix_band_part(mask, 6, 6)
    mask = 1 - mask

    # multiply categorical_crossentropy with the mask
    loss = K.sparse_categorical_crossentropy(y_true[0,:,:], y_pred[0,:,:]) * mask

    ones_in_native = K.sum(y_true * mask)
    zeros_in_native = K.sum((1 - y_true) * mask)
    #ratio = zeros_in_native/ones_in_native
    ratio = 4
    amplify_contacts = K.tf.where(K.tf.equal(y_true[0,:,:,0], 1), K.tf.ones_like(loss) * ratio, K.tf.ones_like(loss))

    loss = loss * amplify_contacts

    # take average w.r.t. the number of unmasked entries
    return K.sum(loss) / K.sum(amplify_contacts * mask)

# FILL THE MSA ARRAY FROM THE .num FILE
depth = 0
length = 0

for l in input_aln_file:

    if depth == 0:
        line_split = l.split()
        length = len(line_split)
        msa = np.zeros((length, alignment_max_depth))  # length x 1000, tipo

    if depth < alignment_max_depth:
        msa[0:length, depth] = [int(element) for element in l.split()]
        depth += 1

print(np.shape(msa))

print('Loading the model...')

model = load_model(model, custom_objects={'masked_sparse_categorical_crossentropy': masked_sparse_categorical_crossentropy, 'newaxis': newaxis, 'outer_sum': outer_sum})

print('Compiling the model...')
model.compile(optimizer='nadam', loss=masked_sparse_categorical_crossentropy, metrics=['sparse_categorical_accuracy'])
model.summary()

print('Predicting target:  ' + input)
print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

results = model.predict(msa[:, :alignment_max_depth].reshape(length * alignment_max_depth)[newaxis, :], verbose=1)
results = average_halves(results, length)

prediction_output = out_path + '/' + input_id + '_' + model_id + '.cmap'
prediction_output_file = open(prediction_output, 'w')

for i in range(length):
        for j in range(i, length):
            prediction_output_file.write(str(i + 1) + ' ' + str(j + 1) + ' 0 8 ' + str(results[0, i, j, 1]) + '\n')

prediction_output_file.close()

imageio.imwrite(out_path + '/' + input_id + '_' + model_id + '.png', (results[0,:,:,1]*255).astype(np.uint8))
