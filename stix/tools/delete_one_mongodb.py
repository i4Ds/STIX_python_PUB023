import sys
import os
sys.path.append('.')
from stix.core import mongo_db 
def delete_one(run):
    ret=input('Do you want to delete run:{}? Y/N \n'.format(run))
    if ret=='Y':
        mdb = mongo_db.MongoDB()
        mdb.delete_runs([run])
        print('deleted')
        

if __name__=='__main__':
    if len(sys.argv)==1:
        print("usage: ./delete_on_run <run>")
    else:
        delete_one(int(sys.argv[1]))
