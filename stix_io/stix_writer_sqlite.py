#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_writer.py
# @description  : store header and parameters  into a sqlite3 database
#                 It can be used for further analysis.
#                 The database can be viewed with the tool sqlitebrowser
#                 Some analysis scripts are  available in the analysis/ folder
#                 sqlite3 python API can be found at https://docs.python.org/2/library/sqlite3.html
# @author       : Hualin Xiao
# @date         : March 18, 2019
#import json
import pprint

import sqlite3
import os

CREATE_TABLE_RUN_SQL = '''create table run(
        ID	INTEGER PRIMARY KEY AUTOINCREMENT,
        filename  TEXT,
        start_time DATE DEFAULT (datetime('now','localtime'))
        );'''
CREATE_TABLE_HEADER_SQL = """CREATE TABLE header (
	ID	INTEGER PRIMARY KEY AUTOINCREMENT,
	run_id  INTEGER NOT NULL,
	SPID	INTEGER NOT NULL,
	service_type	INTEGER NOT NULL,
	service_subtype	INTEGER NOT NULL,
	header_time	REAL NOT NULL,
	descr	TEXT,
	seg_flag INTEGER,
	data_length	INTEGER NOT NULL );"""
CREATE_TABLE_PARAMETER_SQL = """CREATE TABLE parameter (
            ID	INTEGER PRIMARY KEY AUTOINCREMENT,
            packet_id INTEGER NOT NULL,
            name TEXT,
            descr	TEXT,
            raw	TEXT,
            eng_value	TEXT
            );"""


class stix_writer:
    def __init__(self, filename):
        self.filename = filename
        self.current_packet_id = -1
        self.current_run_id = -1
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
        par_list = []
        if parameters:
            for par in parameters:
                if par:
                    par_list.append((self.current_packet_id, par['name'],
                                     par['descr'], str(par['raw']),str(par['value'])))
        self.insert_parameters(par_list)

    def insert_parameters(self, parlist):
        if self.cur and parlist:
            self.cur.executemany(
                'insert into parameter (packet_id, name,descr,raw,eng_value ) values(?,?,?,?,?,?)',
                parlist)
    def write(self, header, parameters, parameter_desc):
        #parameters description not used
        self.write_header(header)
        self.write_parameters(parameters)


def test():
    db = stix_writer('test_out.db')


if __name__ == '__main__':
    test()
