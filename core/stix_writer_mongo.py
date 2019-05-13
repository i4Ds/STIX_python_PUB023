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

class stix_writer:
    def __init__(self):

        self.filename=None
        self.packets=[]
        self.db=None
        self.packet_col=[]
        self.runs_col=None
        self.start=-1
        self.end=-1
        try :
            self.connect= pymongo.MongoClient('localhost', 27017)
            self.db = self.connect["stix"]
            self.packet_col=self.db['packets']
            self.runs_col=self.db['runs']
            
        except Exception as e:
            raise(e)
            print('can not connect to mongodb')
    def register_run(self,in_filename):
        try:
            self.last_run_id=self.runs_col.find().sort('_id',-1).limit(1)[0]['_id']
        except :
            self.last_run_id=-1
        
        self.this_run_id=self.last_run_id+1
        self.run_info={'file':in_filename,
               'date': datetime.datetime.now().isoformat(),
               }

    def write_header(self, header):
        pass
    def write(self,header, parameters, parameter_desc=dict()):
        packet={'header':header, 'parameter':parameters,
                'run_id':self.this_run_id}
        #self.packets.append(packet)
        if self.db:
            self.packet_col.insert_one(packet)
        if self.start<0:
            self.start=header['time']
        self.end=header['time']
    def done(self):
        self.run_info['start']=self.start
        self.run_info['end']=self.end
        self.run_info['_id']=self.this_run_id
        if self.db:
            self.runs_col.insert_one(self.run_info)
            #self.packet_col.insert_many(self.packets)
    def write_all(self, data):
        pass
    def write_parameters(self, parameters,spid=0):
        pass
