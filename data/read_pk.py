import pickle
import pprint
#import matplotlib.pyplot as plt
#import numpy as np
#import matplotlib
import sys

#matplotlib.rcParams['figure.figsize'] = [12, 12]


def show(fname):
    f = open(fname, 'r')
    data = pickle.load(f)
    pprint.pprint(data[0])


#print data[0]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('read_pk filename')
    else:
        show(sys.argv[1])
