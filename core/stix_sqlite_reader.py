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

class StixSqliteReader(object):
    def __init__(self, filename):
        self.filename = filename
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.filename)
        except sqlite3.Error as er:
            #print(er.message)
            pass
        else:
            self.cur = self.conn.cursor()
    def __del__(self):
        if self.conn:
            self.conn.close()
    def execute(self, sql, args, result_type='list'):
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
            if args:
                self.cur.execute(sql,args)
            else:
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
    def get_parameter_values(self,name):
        sql=('select header.header_time, parameter.raw, parameter.eng_value,header.ID, parameter.descr from '
            'parameter join header on header.ID=parameter.packet_id and '
            'name=? order by header.ID asc')
        args=(name,)
        return self.execute(sql, args, 'dict')
    def get_packets(self):
        sql=('select * from header order by ID asc')
        headers=self.execute(sql, None, 'dict')
        data=[]
        for h in headers:
            header_id=h['ID']
            #print(header_id)
            parameters=self.get_parameters_by_header_ID(header_id)
            h['DESCR']=h['descr']
            h['time']=h['header_time']
            data.append({'header':h,'parameter':parameters})
        return data

    def get_parameters_by_header_ID(self,header_ID):
        sql=('select * from parameter where packet_id=? order by ID')
        parameters=self.execute(sql, (header_ID,), 'dict')
        return parameters

    def get_packet_spid(self):
        sql='select header_time, SPID  from header order by ID asc'
        return self.execute(sql,None)
    def get_operation_modes(self):
        sql='select header.header_time, parameter.raw from parameter join header on header.ID=parameter.packet_id and name="NIXD0023"' 
        return self.execute(sql,None)
    def get_headers(self):
        sql='select header_time, SPID from header'
        return self.execute(sql,None)
    def get_parameter_names_of_spid(self,spid):
        sql=('select distinct parameter.name,parameter.descr from ' 
                'parameter join header on header.ID=parameter.packet_id and header.SPID=?')
        args=(spid,)
        return self.execute(sql)
    def get_parameter_names_of_service(self,service):
        sql='select parameter.name from \
                parameter join header on header.ID=parameter.packet_id and header.service_type=?'
        args=(service,)
        return self.execute(sql,args)

    def get_parameter_of_spid(self,spid):
        sql='select parameter.* from \
                parameter join header on header.ID=parameter.packet_id and header.SPID=?'
        args=(spid,)
        return self.execute(sql,args,'dict')
    
#def test():
#    db=ODB('../a.db')
#    print(db.get_packets())
#test()

