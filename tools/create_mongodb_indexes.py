
server='localhost'
port=27017
username=''
password=''
try:
    self.connect = pymongo.MongoClient(
        server, port, username=username, password=password)
    self.db = self.connect["stix"]
    self.collection_packets = self.db['packets']
    self.collection_runs = self.db['processing_runs']
    self.collection_calibration = self.db['calibration_runs']
    print('creating indexes for runs')
    if self.collection_runs:
        indexes=['file','date']
        for index in indexes:
            self.collection_runs.create_index(indexes)

    print('creating indexes for packets')
    if self.collection_packets:
        if self.collection_packets.count() == 0:
            indexes=['header.unix_time','header.SPID','header.service_type',
                    'header.service_subtype','run_id','TMTC']
            for index in indexes:
                self.collection_packets.create_index(index)

except Exception as e:
    print(e)
