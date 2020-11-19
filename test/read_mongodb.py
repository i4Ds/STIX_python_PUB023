from pymongo import MongoClient
import pprint
import timeit
from stix.core import stix_datetime
client = MongoClient()
db = client['stix']
forms= db['bsd_req_forms']
#timeit.timeit(packet_col.find({}, {"header_id": 100000}), number=1000)
runs=forms.find()

for run in runs:
    run['end_utc']=stix_datetime.unix2utc(stix_datetime.utc2unix(run['start_utc'])+int(run['duration']))
    print(run['_id'])
    forms.save(run)

