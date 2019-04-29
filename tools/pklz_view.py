import pprint
import gzip
import pickle
def view(file_in):
    f=gzip.open(file_in,'rb')
    raw=pickle.load(f)
    try:
        data=raw['packet']
        for p in data:
            print('*'*20)
            pprint.pprint(p['header'])
            print('-'*20)
            pprint.pprint(p['parameter'])
    except:
        pprint.pprint(raw)



import sys

if len(sys.argv[1])<2:
    print('pklz view <FILE>')
else:
    view(sys.argv[1])

