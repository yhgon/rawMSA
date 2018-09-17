#!/usr/bin/python

from __future__ import print_function
from sys import argv

letter_to_number = { 'P':1, 'U':2, 'C':3, 'A':4, 'G':5, 'S':6, 'N':7, 'B':8, 'D':9, 'E':10, 'Z':11, 'Q':12, 'R':13, 'K':14, 'H':15, 'F':16, 'Y':17, 'W':18, 'M':19, 'L':20, 'I':21, 'V':22, 'T':23, '-':24, 'X':25 }

input_aln = argv[1]

input_aln_file = open(input_aln)

count = 0
limit = 3000

for line in input_aln_file:

  if count < limit:
    i=0

    while i < len(line.rstrip()):

      try:
        number = letter_to_number[line[i]]
      except KeyError:
        number = 25

      i+=1

      print(str(number), end=' ')

    print('')
    count += 1


