import pickle, gzip
import numpy as np
import math
from matplotlib import pyplot as plt

f=gzip.open('stix_out.pklz','rb')
data=pickle.load(f)
valid_packets=[]
for d in data:
    spectra=np.array(d['parameter']['NIX00158'])
    non_zero=spectra[np.nonzero(spectra)]
    if non_zero:
        print(non_zero)
    if np.all(spectra == 0):
        continue
    else:
        valid_packets.append(d)
print('Number of non-zero spectra:')
n=len(valid_packets)
print(n)
fig=plt.figure()
ncol=2
nrow=math.ceil(float(n)/ncol)
print 'nrow',nrow
for i, d in enumerate(valid_packets):
    spectra=np.array(d['parameter']['NIX00158'])
    plt.subplot(nrow,ncol,i+1)
    plt.plot(spectrum)
    plt.show()
