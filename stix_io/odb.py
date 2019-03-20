#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @title        : ODB.py
# @description  : stix_write_sqlite.py
# @author       : Hualin Xiao
# @date         : Feb. 15, 2019
from __future__ import (absolute_import, unicode_literals)

import pprint
import sqlite3

class ODB(object):
    def __init__(self, filename):
        self.filename = filename
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.filename)
        except sqlite3.Error as er:
            print(er.message)
        else:
            self.cur = self.conn.cursor()
    def __del__(self):
        if self.conn:
            self.conn.close()
    def execute(self, sql, result_type='list'):
        """
        execute sql and return results in a list or a dictionary
        Args:
            sql: sql
            result_type: type of results. It can be list or dict
        return:
            database query result
        """
        if not self.cur:
            return None
        else:
            rows = None
            self.cur.execute(sql)
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
    def get_parameter_raw_values(self,name, timestamps=False):
        if timestamps:
            sql=('select parameter.raw, header.header_time from '
                'parameter join header on header.ID=parameter.packet_id and '
                'name="{}" order by header.ID asc').format(name)
        else:
            sql='select raw from parameter where name="{}" order by ID asc'.format(name)
        return self.execute(sql)

    def get_packet_spid(self):
        sql='select header_time, SPID  from header order by ID asc'
        return self.execute(sql)
    def get_operation_modes(self):
        sql='select header.header_time, parameter.raw from parameter join header on header.ID=parameter.packet_id and name="NIXD0023"' 
        return self.execute(sql)
    def get_headers(self):
        sql='select header_time,SPID from header'
        return self.execute(sql)
    def get_parameter_of_spid(self,spid):
        sql='select parameter.* from \
                parameter join header on header.ID=parameter.packet_id and header.SPID={}'.format(spid)
        return self.execute(sql,'dict')
    
