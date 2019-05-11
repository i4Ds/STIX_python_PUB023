#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_writer.py
# @description  : Write decoded parameters to a python pickle file
#                 see https://docs.python.org/2/library/pickle.html for descriptions of python pickle
#                 It can be further analyzed.
# @author       : Hualin Xiao
# @date         : Feb. 27, 2019
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
        self.packet_col=None
        self.file_col=None
        try :
            self.connect= pymongo.MongoClient('localhost', 27017)
            self.db = self.connect["stix"]
            self.packet_col=self.db['packets']
            self.file_col=self.db['files']
            
        except Exception as e:
            raise(e)
            print('can not connect to mongodb')
    def register_run(self,in_filename):
        self.run_uuid=uuid.uuid1()
        if self.file_col:
           self.file_col.insert_one({'file':in_filename,
               'date': datetime.datetime.now().isoformat(),
               'run_uuid':self.run_uuid
               })


    def write_header(self, header):
        pass
    def write(self,header, parameters, parameter_desc=dict()):
        packet={'header':header, 'parameter':parameters,
                'file':self.filename}
        #'parameter_desc':parameter_desc
        self.packets.append(packet)
    def done(self):
        if self.db:
            self.packet_col.insert_many(self.packets)
    def write_all(self, data):
        pass
    def write_parameters(self, parameters,spid=0):
        pass
