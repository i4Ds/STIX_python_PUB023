#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_writer.py
# @description  : Write decoded parameters to a mongo database 
# @author       : Hualin Xiao
# @date         : May. 12, 2019
#import json
import pprint
import pymongo
import datetime
import uuid

class MongoDB(object):
    def __init__(self, server='localhost',port=27017):
        self.filename=None
        self.packets=[]
        self.db=None
        self.packet_col=None
        self.runs_col=None
        try :
            self.connect= pymongo.MongoClient(server, port)
            self.db = self.connect["stix"]
            self.packet_col=self.db['packets']
            self.runs_col=self.db['runs']
        except Exception as e:
            raise(e)
            print('can not connect to mongodb')
    def get_packets(self,run_id):
        if self.packet_col:
            cursor=self.packet_col.find({'run_id':int(run_id)})
            data=[x for x in cursor]
            #for x in cursor:
            #    data.append
            #packets=list(cursor)
            return data
            #return packets
        else:
            return None
    def close(self):
        if self.connect:
            self.connect.close()
    def get_last_run_packet(self):
        if self.runs_col:
            last_run_id=(self.runs_col.find().sort('_id',-1).limit(1)[0]['_id'])
            self.get_packet(last_run_id)
    def get_runs(self):
        if self.runs_col:
            runs=list(self.runs_col.find().sort('_id',-1))
            return runs
        else:
            return None




if __name__=='__main__':
    mdb=MongoDB()
    print(mdb.get_runs())
