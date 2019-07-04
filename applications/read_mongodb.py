from pymongo import MongoClient
import pprint
client = MongoClient()
db = client['stix']
packets_col = db['packets']
runs_col = db['runs']
#last_run_id=runs_col.find()#.sort({'_id':-1})#.limit(1)
#pprint.pprint(last_run_id)
#packets=runs_col.find().sort({'run_id', last_run_id})
#pprint.pprint(packets)

print(runs_col.find({}, {"_id": -1}))
print(list(packets_col.find({'run_id': 29}))[0])
