import pymongo
import hashlib
connect = pymongo.MongoClient()
db = connect["stix"]
packet_db= db['packets']
cursor=packet_db.find()
#cursor=packet_db.find({'_id':771287})
total=cursor.count()
per=int(total/100)
i=0
for pkt in cursor:
    header_str=str(pkt['header']).encode('utf-8')
    pkt['hash']=hashlib.shake_256(header_str).hexdigest(8)
    packet_db.replace_one({'_id':pkt['_id']}, pkt)
    i+=1

    if i%per==0:
        print(total/i)
            


    

    
    
