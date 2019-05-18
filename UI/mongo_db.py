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

class MongoDB(object):
    def __init__(self, server='localhost',port=27017, user='',pwd=''):
        self.filename=None
        self.packets=[]
        self.db=None
        self.collection_packets=None
        self.collection_runs=None
        self.collection_headers=None
        try :
            if server=='localhost' and user=='' and pwd=='':
                self.connect= pymongo.MongoClient(server, port)
            else:
                self.connect= pymongo.MongoClient(server, port,username=user,
                        password=pwd,authSource='stix')
            self.db = self.connect["stix"]
            self.collection_packets=self.db['packets']
            self.collection_headers=self.db['headers']
            self.collection_runs=self.db['runs']
        except Exception as e:
            #print('can not connect to mongodb: {}'.format(str(e)))
            raise(e)
    def get_headers(self,run_id):
        if self.collection_headers:
            cursor=self.collection_headers.find({'run_id':int(run_id)})
            data=[x for x in cursor]
            return data
        else:
            return None

    def get_packet_for_header(self,hid, objID=False):
        header_id=hid
        if not objID:
            header_id=bson.ObjectId(hid)

        if self.collection_packets:
            cursor=self.collection_packets.find({'header_id':header_id})
            data=[x for x in cursor]
            return data
        else:
            return None

    def get_packets(self,run_id):
        if self.collection_packets:
            cursor=self.collection_packets.find({'run_id':int(run_id)})
            data=[x for x in cursor]
            return data
        else:
            return None
    def close(self):
        if self.connect:
            self.connect.close()
    def get_last_run_packet(self):
        if self.collection_runs:
            last_run_id=(self.collection_runs.find().sort('_id',-1).limit(1)[0]['_id'])
            self.get_packet(last_run_id)
    def get_runs(self):
        if self.collection_runs:
            runs=list(self.collection_runs.find().sort('_id',-1))
            return runs
        else:
            return None




if __name__=='__main__':
    mdb=MongoDB()
    print(mdb.get_runs())
