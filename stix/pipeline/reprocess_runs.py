import sys
import os
sys.path.append('.')
from stix.core import mongo_db 
from stix.pipeline import parser_pipeline as pp
mdb = mongo_db.MongoDB()
log=open('log.txt','w')
def delete_one(start_run, end_run=-1):
    runs=[]
    if end_run==-1:
        runs=[start_run]
    else:
        runs=range(start_run,end_run)
    print('runs to delete:{}'.format(str(runs)))
    ret=input('Are you sure to delete them ? Y/N: ')
    if ret=='Y':
        raw_db=mdb.get_collection('raw_files')
        filenames=[]
        docs=raw_db.find({'file_id':{'$gte':start_run, '$lte':end_run},'hidden':False}).sort('_id',1)
        filenames = [ os.path.join(doc['path'], doc['filename']) for doc in docs]
        log.write(str(filenames))
        print(filenames)
        mdb.delete_runs(runs)
        print('deleted')
        print('Processing files...')
        try:
            for fn in filenames:
                print(filename)
                pp.process_one(fn)



if __name__=='__main__':
    if len(sys.argv)==1:
        print("usage: ./delete_files_from_mongodb <run_begin> [run_end]")
    elif len(sys.argv)==2:
        delete_one(int(sys.argv[1]))
    elif len(sys.argv)==3:
        delete_one(int(sys.argv[1]), int(sys.argv[2]))
