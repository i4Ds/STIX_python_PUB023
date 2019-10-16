#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : MongoDB.py
# @description  : Mongodb reader
# @author       : Hualin Xiao
# @date         : May. 12, 2019
#import json
import pprint
import datetime
import uuid
import bson
import pymongo

NUM_MAX_PACKETS = 10000


class MongoDB(object):
    def __init__(self, server='localhost', port=27017, user='', pwd=''):
        self.filename = None
        self.packets = []
        self.db = None
        self.collection_packets = None
        self.collection_processing_runs = None
        self.collection_calibration_runs= None
        try:
            if server == 'localhost' and user == '' and pwd == '':
                self.connect = pymongo.MongoClient(server, port)
            else:
                self.connect = pymongo.MongoClient(
                    server,
                    port,
                    username=user,
                    password=pwd,
                    authSource='stix')
            self.db = self.connect["stix"]
            self.collection_packets = self.db['packets']
            self.collection_processing_runs = self.db['processing_runs']
            self.collection_calibration_runs= self.db['calibration_runs']
        except Exception as e:
            print('can not connect to mongodb')

    def get_collection_calibration(self):
        return self.collection_calibration_runs
    def get_collection_processing(self):
        return self.collection_processing_runs

    def get_collection_packets(self):
        return self.collection_packets
    

    def is_connected(self):
        if self.db:
            return True
        else:
            return False

    def get_filename_of_run(self, run_id):
        if self.collection_processing_runs:
            cursor = self.collection_processing_runs.find({'_id': int(run_id)})
            for x in cursor:
                return x['filename']
        return ''

    def select_packets_by_id(self, pid):
        if self.collection_packets:
            cursor = self.collection_packets.find({'_id': int(pid)})
            return list(cursor)
        return []

    def delete_one_run(self, run_id):
        if self.collection_packets:
            cursor = self.collection_packets.delete_many(
                {'run_id': int(run_id)})

        if self.collection_processing_runs:
            cursor = self.collection_processing_runs.delete_many({'_id': int(run_id)})

    def delete_runs(self, runs):
        for run in runs:
            self.delete_one_run(run)

    def select_packets_by_run(self, run_id, nmax=NUM_MAX_PACKETS):
        if self.collection_packets:
            cursor = self.collection_packets.find({'run_id': int(run_id)}).sort('_id',1)
            return list(cursor)
        return []

    def close(self):
        if self.connect:
            self.connect.close()

    def select_all_runs(self, order=-1):
        if self.collection_processing_runs:
            runs = list(self.collection_processing_runs.find().sort('_id', order))
            return runs
        else:
            return None
    def get_unprocessed(self):
        unprocess_run_ids=[]
        if self.collection_processing_runs:
            unprocess_runs=self.collection_processing_runs.find({'quicklook_pdf':{'$exists':False}},{'_id':1})
            if unprocess_runs:
                return [x['_id'] for x in unprocess_runs]
        return []
    def set_run_ql_pdf(self, _id,  pdf_filename):
        if self.collection_processing_runs:
            run = self.collection_processing_runs.find_one({'_id': _id})
            run['quicklook_pdf']=pdf_filename
            self.collection_processing_runs.save(run)
    def get_run_ql_pdf(self, _id):
        if self.collection_processing_runs:
            run = self.collection_processing_runs.find_one({'_id': _id})
            if 'quicklook_pdf' in run:
                return run['quicklook_pdf']
        return None



if __name__ == '__main__':
    mdb = MongoDB()
    #print(mdb.get_packet_for_header(318))
    mdb.set_quicklook_pdf(0, '/data/a.pdf')
