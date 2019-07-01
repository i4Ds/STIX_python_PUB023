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
from core import stix_logger
_stix_logger = stix_logger._stix_logger


class StixPickleWriter:
    def __init__(self, filename):
        self.filename = filename
        self.packet_counter = 0
        self.fout = None
        self.packets = []
        if filename.endswith('.pklz'):
            self.fout = gzip.open(filename, 'wb')
        else:
            self.fout = open(filename, 'wb')

    def register_run(self, in_filename, filesize=0, comment=''):
        self.run = {
            'Input': in_filename,
            'Output': self.filename,
            'filsize': filesize,
            'comment':comment,
            'Date': datetime.datetime.now().isoformat()
        }

    def write_all(self, packets):
        if self.fout:
            data = {'run': self.run, 'packet': packets}
            pickle.dump(data,self.fout)
            self.fout.close()


class StixMongoWriter:
    """store data in  MongoDB"""

    def __init__(self, server='localhost',username='', password=''):

        self.packets = []
        self.db = None
        self.collection_packets = None
        self.collection_runs = None
        self.current_run_id=0
        self.current_header_id=0
        self.start = -1
        self.end = -1
        try:
            self.connect = pymongo.MongoClient(server, 
                    username=username, password=password)
            self.db = self.connect["stix"]

            self.collection_packets = self.db['packets']
            self.collection_headers = self.db['headers']
            self.collection_runs = self.db['runs']
            self.create_indexes()
        except Exception as e:
            raise (e)
            print('can not connect to mongodb')

    def create_indexes(self):
        """to speed up queries """
        if self.collection_headers:
            if self.collection_headers.count() == 0:
                self.collection_headers.create_index([('time', -1),
                                                      ('SPID', -1),
                                                      ('service_type', -1),
                                                      ('service_subtype', -1),
                                                      ('run_id', -1)],
                                                     unique=False)

        if self.collection_runs:
            if self.collection_runs.count() == 0:
                self.collection_runs.create_index([('file', -1), ('date', -1)],
                                                  unique=False)

        if self.collection_packets:
            if self.collection_packets.count() == 0:
                self.collection_packets.create_index([('header.time', -1),
                                                      ('header_id', -1),
                                                      ('run_id', -1)],
                                                     unique=False)

    def register_run(self, in_filename, filesize=0, comment=''):
        try:
            self.current_run_id= self.collection_runs.find().sort(
                '_id', -1).limit(1)[0]['_id']+1
        except IndexError:
            self.current_run_id=0
            #first entry
        try:
            self.current_header_id= self.collection_headers.find().sort(
                '_id', -1).limit(1)[0]['_id']+1
        except IndexError:
            self.current_header_id= 0

        try:
            self.current_packet_id= self.collection_packets.find().sort(
                '_id', -1).limit(1)[0]['_id']+1
        except IndexError:
            self.current_packet_id=0

        log_filename=_stix_logger.get_log_filename()

        self.run_info = {
            'filename': os.path.basename(in_filename),
            'path': os.path.dirname(in_filename),
            'comment':comment,
            'log':log_filename,
            'date': datetime.datetime.now().isoformat(),
            'filesize': filesize
        }


    def write_all(self, packets):
        if self.db and packets:
            self.run_info['start'] = packets[0]['header']['time']
            self.run_info['end'] = packets[-1]['header']['time']
            self.run_info['_id'] = self.current_run_id
            run_id=self.collection_runs.insert_one(self.run_info).inserted_id

            for packet in packets:
                header = packet['header']
                parameters = packet['parameters']

                header['run_id'] = run_id
                header['_id']=self.current_header_id
                header_id = self.collection_headers.insert_one(
                    header).inserted_id
                self.current_header_id += 1

                packet['header_id'] = header_id
                packet['run_id'] = self.current_run_id
                packet['_id']=self.current_packet_id

                result = self.collection_packets.insert_one(packet)
                self.current_packet_id+=1

            #self.collection_parameters.insert_many(self.packets)


''' sqlite schema '''

CREATE_TABLE_RUN_SQL = '''create table run(
        ID	INTEGER PRIMARY KEY AUTOINCREMENT,
        filename  TEXT,
        filesize INTEGER NULL,
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
	length	INTEGER NOT NULL );"""
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
        self.current_parent_id = 0
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
                self.current_parent_id = row[0]
            else:
                return 0

    def register_run(self, filename, filesize=0, comment=''):
        self.cur.execute('insert into run (filename, filesize) values(?,?)',
                         (filename, filesize))
        self.update_run_id()

    def write_header(self, header):
        if self.cur:
            row = (header['SPID'], self.current_run_id, header['service_type'],
                   header['service_subtype'], header['time'], header['DESCR'],
                   header['seg_flag'], header['length'])
            self.cur.execute(
                'insert into header (SPID, run_id, service_type, service_subtype,header_time, descr, \
                        seg_flag, length) values( ?,?, ?,?,?,?,?,?)', row)
            self.update_packet_id()

    def done(self):
        self.conn.commit()
        #self.conn.execute("VACUUM")
        self.conn.close()

    def write_parameters(self, parameters):
        if parameters:
            for par in parameters:
                if par:
                    par_list = (
                        self.current_packet_id,
                        par['name'],
                        #par['descr'],
                        str(par['raw']),
                        str(par['value']),
                        self.current_packet_id)
                    if 'children' in par:
                        if par['children']:
                            self.get_last_parameter_id()
                            self.write_parameters(par['children'])
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

    def write_all(self, packets):
        for e in packets:
            self.write_header(e['header'])
            self.write_parameters(e['parameter'])


try:
    from ROOT import TFile, TTree
    from array import array

    class StixROOTWriter:
        """Write to root"""

        def __init__(self, filename):
            self.filename = filename
            self.packet_counter = 0
            self.fout = None
            if filename:
                #self.out=open(filename,'w')
                self.fout = TFile(filename, 'recreate')
                self.tree = TTree('header', 'header')
                self.seg_flag = array('B', [0])
                self.seq_count = array('I', [0])
                self.service_subtype = array('B', [0])
                self.service_type = array('B', [0])
                self.SPID = array('I', [0])
                self.length = array('I', [0])
                self.des = array('B', [0])
                self.desc = array('c', '\0' * 64)
                self.timestamp = array('f', [0])
                self.tree.Branch('seg_flag', self.seg_flag, 'seg_flag/B')
                self.tree.Branch('seq_count', self.seq_count, 'seq_count/I')
                self.tree.Branch('service_type', self.service_type,
                                 'service_type/B')
                self.tree.Branch('service_subtype', self.service_subtype,
                                 'service_subtype/B')
                self.tree.Branch('SPID', self.SPID, 'SPID/I')
                self.tree.Branch('length', self.length, 'length/I')
                self.tree.Branch('desc', self.desc, 'desc[64]/C')
                self.tree.Branch('timestamp', self.timestamp, 'timestamp/f')
                self.tree.Branch('des', self.des, 'des/B')

        def done(self):
            self.tree.Write()
            self.fout.Close()

        def write_all(self, packets):
            pass

        def write_header(self, header):
            """
            it is called for every telemetry data header
            """
            if self.fout:
                self.seg_flag[0] = header['seg_flag']
                self.seq_count[0] = header['seq_count']
                self.service_subtype[0] = header['service_subtype']
                self.service_type[0] = header['service_type']
                self.SPID[0] = header['SPID']
                self.length[0] = header['length']
                self.timestamp[0] = header['time']
                for i, c in enumerate(header['DESCR'][0:64]):
                    self.desc[i] = str(c)
                self.tree.Fill()

        def write_parameters(self, parameters):
            pprint.pprint(parameters)
            #if self.out:
            #pp = pprint.PrettyPrinter(indent=4, stream=self.out)
            #pp.pprint(parameters)
except ImportError:
    pass
