import numpy as np
from sys import argv
import glob
import textwrap
import os
import imageio

np.set_printoptions(threshold=np.nan)

fasta = argv[1]
out_path = os.path.dirname(os.path.abspath(fasta))
target_id = os.path.splitext(os.path.basename(fasta))[0]

target_length = int(argv[2])
group_id = argv[3]

prediction_map = np.zeros((target_length, target_length))

fasta_file = open(fasta)
fastaseq = ""

for line in fasta_file:
    if not line.startswith(">"):
        fastaseq += line.rstrip()

fasta_file.close()
fastaseq_wrap = textwrap.wrap(fastaseq, 50)

#print("Fasta sequence: " + fastaseq)

count = 0

for prediction in glob.glob(out_path + '/*.cmap'):

    try:
        prediction_map_file = open(prediction)
    except:
        print("ERROR: couldn't open prediction " + prediction)
        continue

    #41 88 0 8 0.0800896063447
    #59 65 0 8 0.080059915781
    #35 126 0 8 0.0800547972322

    for predline in prediction_map_file:

        try:
            i = int(predline.split()[0]) - 1
            j = int(predline.split()[1]) - 1

            p = float(predline.split()[4])

            prediction_map[i, j] += p
            prediction_map[j, i] += p

        except:
            print("ERROR: something went wrong while initializing map" + predline)
            continue

    count += 1
    prediction_map_file.close()

prediction_map = prediction_map / count #averaging the ensemble

map_array = []

for i in range(target_length):
        for j in range(i + 5, target_length):
            map_array.append([i + 1, j + 1, 0,  8, prediction_map[i, j]])

map_array_sorted = sorted(map_array, key=lambda x: x[4], reverse=True)

prediction_output = out_path + '/' + target_id + '_ensemble.cmap'
prediction_output_file = open(prediction_output, 'w')

prediction_output_file.write("PFRMAT RR\n")                # PFRMAT RR
prediction_output_file.write("TARGET " + target_id + "\n") # TARGET T0999
prediction_output_file.write("AUTHOR " + group_id + "\n")  # AUTHOR 1234-5678-9000
       # REMARK Predictor remarks
prediction_output_file.write("METHOD rawMSA: ab initio contact map prediction" + "\n")                          # METHOD Description of methods used
prediction_output_file.write("METHOD from a single Multiple Sequence Alignment input" + "\n")               # METHOD Description of methods used
prediction_output_file.write("MODEL  1" + "\n")            # MODEL  1
for fasta_line in fastaseq_wrap:                           # HLEGSIGILLKKHEIVFDGC # <- entire target sequence (up to 50
    prediction_output_file.write(fasta_line + "\n")        # HDFGRTYIWQMSDASHMD   #   residues per line)

for line in map_array_sorted:
    prediction_output_file.write(" ".join(map(str, line)))
    prediction_output_file.write("\n")

prediction_output_file.write("END" + "\n")

prediction_output_file.close()

imageio.imwrite(out_path + '/' + target_id + '_ensemble.png', (prediction_map*255).astype(np.uint8))


