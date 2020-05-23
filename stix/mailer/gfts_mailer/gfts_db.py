#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import pprint
import sqlite3
from gfts_config  import config

CREATE_TABLE_SQL='''CREATE TABLE if not exists gfts 
(
	id	INTEGER PRIMARY KEY AUTOINCREMENT,
	filename	TEXT NOT NULL,
	filetype TEXT,
	entryTime	datetime DEFAULT CURRENT_TIMESTAMP
);'''


class GFTSDB(object):
    def __init__(self, filename=config['SqlDatabaseFileName']):
        self.filename = filename
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.filename)
        except sqlite3.Error as er:
            raise Exception('Failed to connect to IDB !')
        else:
            self.cur = self.conn.cursor()
            self.execute(CREATE_TABLE_SQL)
    def __del__(self):
        if self.conn:
            self.conn.close()

    def execute(self, sql,arguments=None, result_type='list', commit=False):
        """
        execute sql and return results in a list or a dictionary
        Args:
            sql: sql
            result_type: type of results. It can be list or dict
        return:
            database query result
        N
        """
        if not self.cur:
            raise Exception('IDB is not initialized!')
        else:
            rows = None
            if arguments:
                self.cur.execute(sql,arguments)
            else:
                self.cur.execute(sql)
            if commit:
                self.conn.commit()
                return 
            else:
                if result_type == 'list':
                    rows = self.cur.fetchall()
                else:
                    rows = [
                        dict(
                            zip([column[0]
                                 for column in self.cur.description], row))
                        for row in self.cur.fetchall()
                    ]
                return rows
        
    def exist(self,filename):
        sql=('select * from gfts where filename=?')
        rows=self.execute(sql,(filename,))
        if rows:
            return True
        return False
    def insert(self, filename,filetype=''):
        exist=self.exist(filename)
        if not exist:
            sql=('insert into gfts (filename, filetype) values (?,?)')
            self.execute(sql,arguments=(filename,filetype),commit=True)
            return True
        return False
        
