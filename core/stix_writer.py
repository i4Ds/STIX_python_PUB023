#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_writer.py
# @description  : Write decoded data to a python pickle file, sqlite database or mongo database
# @author       : Hualin Xiao
# @date         : Feb. 27, 2019
#import json
import pprint
import pickle
import gzip
import datetime
import pymongo
import datetime
import uuid
import sqlite3
import os


class StixPickleWriter:
    def __init__(self, filename):
        self.filename = filename
        self.packet_counter = 0
        self.fout=None
        self.packets=[]
        if filename.endswith('.pklz'):
            self.fout=gzip.open(filename,'wb')
        else:
            self.fout=open(filename,'wb')

    def register_run(self,in_filename):
        self.run={'Input':in_filename,
                   'Output':self.filename,
                   'Date': datetime.datetime.now().isoformat()
                  }

    def write_header(self, header):
        """
        it is called for every telemetry data header
        """
        msg = [
            self.packet_counter, header['service_type'],
            header['service_subtype'], header['SPID'],header['SSID'], header['DESCR'],
            header['time'], header['coarse_time'], header['fine_time'],header['segmentation'],header['data_length']
        ]
        line=(','.join(map(str, msg)))
        self.packet_counter += 1
    def write(self,header, parameters):
        packet={'header':header, 'parameter':parameters}
        self.packets.append(packet)

    def done(self):
        data={'run':self.run, 'packet':self.packets}
        pickle.dump(data,self.fout)
        self.fout.close()
    def write_all(self, data):
        for p in data:
            self.write(p['header'],p['parameter'])


    def write_parameters(self, parameters,spid=0):
        pprint.pprint(parameters)



class StixMongoWriter:
    """store data in  a NoSQL database"""
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


''' sqlite schema '''

CREATE_TABLE_RUN_SQL = '''create table run(
        ID	INTEGER PRIMARY KEY AUTOINCREMENT,
        filename  TEXT,
        start_time DATE DEFAULT (datetime('now','localtime'))
        );'''
CREATE_TABLE_HEADER_SQL = """CREATE TABLE header (
	ID	INTEGER PRIMARY KEY AUTOINCREMENT,
	run_id  INTEGER NOT NULL,
	SPID	INTEGER NOT NULL,
        descr	TEXT,
	service_type	INTEGER NOT NULL,
	service_subtype	INTEGER NOT NULL,
	header_time	REAL NOT NULL,
	seg_flag INTEGER,
	data_length	INTEGER NOT NULL );"""
CREATE_TABLE_PARAMETER_SQL = """CREATE TABLE parameter (
            ID	INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id INTEGER NOT NULL,
            name TEXT,
            raw	TEXT,
            parent, INTEGER,
            value TEXT
            );"""

            #descr	TEXT,


class StixSqliteWriter:
    def __init__(self, filename):
        self.filename = filename
        self.current_packet_id = -1
        self.current_run_id = -1
        self.current_parent_id=0
        if filename:
            db_exist = os.path.isfile(filename)
            self.conn = sqlite3.connect(filename)
            self.cur = self.conn.cursor()
            if not db_exist and self.cur:
                self.cur.execute(CREATE_TABLE_RUN_SQL)
                self.cur.execute(CREATE_TABLE_HEADER_SQL)
                self.cur.execute(CREATE_TABLE_PARAMETER_SQL)

    def update_packet_id(self):
        if self.cur:
            self.cur.execute('select max(ID) from header')
            row = self.cur.fetchone()
            if row:
                self.current_packet_id = row[0]

    def update_run_id(self):
        if self.cur:
            self.cur.execute('select max(ID) from run')
            row = self.cur.fetchone()
            if row:
                self.current_run_id = row[0]
    def get_last_parameter_id(self):
        if self.cur:
            self.cur.execute('select max(ID) from parameter')
            row = self.cur.fetchone()
            if row:
                self.current_parent_id= row[0]
            else:
                return 0

    def register_run(self, filename):
        self.cur.execute('insert into run (filename) values(?)', (filename, ))
        self.update_run_id()

    def write_header(self, header):
        if self.cur:
            row = (header['SPID'], self.current_run_id, header['service_type'],
                   header['service_subtype'], header['time'], header['DESCR'],
                   header['seg_flag'], header['data_length'])
            self.cur.execute(
                'insert into header (SPID, run_id, service_type, service_subtype,header_time, descr, \
                        seg_flag, data_length) values( ?,?, ?,?,?,?,?,?)', row)
            self.update_packet_id()

    def done(self):
        self.conn.commit()
        #self.conn.execute("VACUUM")
        self.conn.close()

    def write_parameters(self, parameters):
        if parameters:
            for par in parameters:
                if par:
                    par_list=(self.current_packet_id, par['name'],
                                     #par['descr'],
                                     str(par['raw']),str(par['value']),self.current_packet_id)
                    if  'child' in par:
                       if par['child']:
                            self.get_last_parameter_id()
                            self.write_parameters(par['child'])
                    self.insert_parameters(par_list)

    def insert_parameters(self, parlist):
        self.cur.execute(
                'insert into parameter (packet_id, name,raw,  value,parent) values(?,?,?,?,?)',
                parlist)
                #'insert into parameter (packet_id, name,descr,raw,  value,parent) values(?,?,?,?,?,?)',
                #parlist)

    def write(self, header, parameters, parameter_desc):
        #parameters description not used
        self.write_header(header)
        self.write_parameters(parameters)
    def write_all(self,data):
        for e in data:
            self.write_header(e['header'])
            self.write_parameters(e['parameter'])
        


from ROOT import TFile, TTree
from array import array

class StixROOTWriter:
    def __init__(self, filename):
        self.filename = filename
        self.packet_counter = 0
        self.fout=None
        if filename:
            #self.out=open(filename,'w')
            self.fout=TFile(filename,'recreate')
            self.tree=TTree('header','header')
            self.seg_flag=array('B',[0])
            self.seq_count=array('I',[0])
            self.service_subtype=array('B',[0])
            self.service_type=array('B',[0])
            self.SPID=array('I',[0])
            self.length=array('I',[0])
            self.des=array('B',[0])
            self.desc=array('c','\0'*64)
            self.timestamp=array('f',[0])
            self.tree.Branch('seg_flag',self.seg_flag,'seg_flag/B')
            self.tree.Branch('seq_count',self.seq_count,'seq_count/I')
            self.tree.Branch('service_type',self.service_type,'service_type/B')
            self.tree.Branch('service_subtype',self.service_subtype,'service_subtype/B')
            self.tree.Branch('SPID',self.SPID,'SPID/I')
            self.tree.Branch('length',self.length,'length/I')
            self.tree.Branch('desc',self.desc,'desc[64]/C')
            self.tree.Branch('timestamp',self.timestamp,'timestamp/f')
            self.tree.Branch('des',self.des,'des/B')

    def done(self):
        self.tree.Write()
        self.fout.Close()

    def write_header(self, header):
        """
        it is called for every telemetry data header
        """
        if self.fout:
            self.seg_flag[0]=header['seg_flag']
            self.seq_count[0]=header['seq_count']
            self.service_subtype[0]=header['service_subtype']
            self.service_type[0]=header['service_type']
            self.SPID[0]=header['SPID']
            self.length[0]=header['data_length']
            self.timestamp[0]=header['time']
            for i,c in enumerate(header['DESCR'][0:64]):
                self.desc[i]=str(c)
            self.tree.Fill()

    def write_parameters(self, parameters):
        pprint.pprint(parameters)
        #if self.out:
            #pp = pprint.PrettyPrinter(indent=4, stream=self.out)
            #pp.pprint(parameters)
