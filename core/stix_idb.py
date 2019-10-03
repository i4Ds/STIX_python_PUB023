#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @title        : IDB.py
# @description  : STIX idb python interface
# @author       : Hualin Xiao
# @date         : Feb. 15, 2019
from __future__ import (absolute_import, unicode_literals)
import os
import sqlite3
import threading
IDB_POSSIBLE_FILENAMES = [
    'idb/idb.sqlite', '../idb/idb.sqlite', '../idb/idb.db', '../idb.sqlite',
    '../idb.db'
]


def find_idb(filename):
    if filename:
        if os.path.exists(filename):
            return filename
    for fname in IDB_POSSIBLE_FILENAMES:
        if os.path.exists(fname):
            return fname
    return None


LOCK = threading.Lock()


class _IDB(object):
    __instance = None

    @staticmethod
    def get_instance(filename):
        if not _IDB.__instance:
            _IDB(filename)
        return _IDB.__instance

    #singleton
    #make sure only one instance is created
    def __init__(self, filename=''):
        if _IDB.__instance:
            raise Exception('IDB already initialized')
        else:
            _IDB.__instance = self
        self.conn = None
        self.cur = None
        self.parameter_structures = dict()
        self.calibration_polynomial = dict()
        self.calibration_curves = dict()
        self.textual_parameter_lut = dict()
        self.soc_descriptions = dict()
        self.parameter_descriptions = dict()
        self.s2k_table_contents = dict()
        self.filename = find_idb(filename)
        if self.filename:
            self.connect_database(self.filename)

    def is_connected(self):
        if self.cur:
            return True
        return False

    def reload(self, filename):
        self.filename = filename
        self.close()
        self.parameter_structures = dict()
        self.calibration_polynomial = dict()
        self.calibration_curves = dict()
        self.textual_parameter_lut = dict()
        self.soc_descriptions = dict()
        self.parameter_descriptions = dict()
        self.s2k_table_contents = dict()
        if self.filename:
            self.connect_database(self.filename)

    def get_idb_filename(self):
        return os.path.abspath(self.filename)

    def connect_database(self, filename):
        try:
            self.conn = sqlite3.connect(filename, check_same_thread=False)
        except sqlite3.Error:
            raise Exception('Failed to connect to IDB !')
        self.cur = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def execute(self, sql, arguments=None, result_type='list'):
        """
        execute sql and return results in a list or a dictionary
        """
        if not self.cur:
            raise Exception('IDB is not initialized!')

        else:
            rows = None

            try:
                LOCK.acquire(True)
                #sqlite doesn't like multi-threads

                if arguments:
                    self.cur.execute(sql, arguments)
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
            finally:
                LOCK.release()
            return rows

    def get_spid_info(self, spid):
        """ get SPID description """
        sql = 'select PID_DESCR,PID_TYPE,PID_STYPE from PID where PID_SPID=? limit 1'
        return self.execute(sql, (spid, ))

    def print_all_spid_desc(self):
        sql = 'select PID_DESCR,PID_SPID from PID'
        rows = self.execute(sql, None)
        for row in rows:
            print('"{}":"{}",'.format(row[1], row[0]))

    def get_scos_description(self, name):
        """ get scos long description """
        if name in self.soc_descriptions:
            return self.soc_descriptions[name]
        else:
            rows = self.execute(
                'select SW_DESCR from sw_para where scos_name=? ', (name, ))
            if rows:
                res = rows[0][0]
                self.soc_descriptions[name] = res
                return res
            return ''

    def get_telemetry_description(self, spid):
        """get telemetry data information """
        sql = ('select sw_para.SW_DESCR, tpcf.tpcf_name  '
               ' from sw_para join tpcf '
               'on tpcf.tpcf_name=sw_para.scos_name and tpcf.tpcf_spid= ?')
        return self.execute(sql, (spid, ))

    def get_packet_type_offset(self, packet_type, packet_subtype):
        sql = ('select PIC_PI1_OFF, PIC_PI1_WID from PIC '
               'where PIC_TYPE=? and PIC_STYPE=? limit 1')
        args = (packet_type, packet_subtype)
        rows = self.execute(sql, args)
        if rows:
            return rows[0]
        return 0, 0

    def get_parameter_description(self, name):
        """ get scos long description """
        if name in self.parameter_descriptions:
            return self.parameter_descriptions[name]
        else:
            rows = self.execute('select PCF_DESCR from PCF where PCF_NAME=? ',
                                (name, ))
            if not rows:
                rows = self.execute('select CPC_DESCR from CPC where CPC_PNAME=? ',
                                (name, ))
            if rows:
                res = rows[0][0]
                self.parameter_descriptions[name] = res
                return res
            return ''



    def get_packet_type_info(self, packet_type, packet_subtype, pi1_val=-1):
        """
        Identify packet type using service, service subtype and information in IDB table PID
        """
        args = None
        if pi1_val == -1:
            sql = ('select PID_SPID, PID_DESCR, PID_TPSD from PID '
                   'where PID_TYPE=? and PID_STYPE=? limit 1')
            args = (packet_type, packet_subtype)
        else:
            sql = (
                'select PID_SPID, PID_DESCR, PID_TPSD from PID '
                'where PID_TYPE=? and PID_STYPE=? and PID_PI1_VAL=? limit 1')
            args = (packet_type, packet_subtype, pi1_val)
        rows = self.execute(sql, args, 'dict')
        if rows:
            return rows[0]
        else:
            print(
                "No information in IDB for service {}, service_subtype {}  and pi1_val: {} "
                .format(packet_type, packet_subtype, pi1_val))
            return None

    def get_s2k_parameter_types(self, ptc, pfc):
        """ get parameter type """
        if (ptc, pfc) in self.s2k_table_contents:
            return self.s2k_table_contents[(ptc, pfc)]
        else:
            sql = ('select S2K_TYPE from '
                   ' tblConfigS2KParameterTypes where PTC = ? '
                   ' and ? >= PFC_LB and  PFC_UB >= ? limit 1')
            args = (ptc, pfc, pfc)
            rows = self.execute(sql, args, 'list')
            s2k_type = rows[0][0]
            self.s2k_table_contents[(ptc, pfc)] = s2k_type
            return s2k_type

    def convert_NIXG_NIXD(self, name):
        sql = (
            'select PDI_GLOBAL, PDI_DETAIL, PDI_OFFSET from PDI where PDI_GLOBAL=? '
        )
        args = (name, )
        rows = self.execute(sql, args, 'dict')
        return rows

    def get_fixed_packet_structure(self, spid):
        """
        get parameter structures using SCO ICD (page 39)
        Args:
            spid: SPID
        Returns:
            is_fixed: whether it is a fixed length packet
            parameter structures
         """
        if spid in self.parameter_structures:
            return self.parameter_structures[spid]
        sql = (
            'select PCF.PCF_DESCR, PLF.PLF_OFFBY, PLF.PLF_OFFBI, PCF.PCF_NAME,'
            ' PCF.PCF_WIDTH, PCF.PCF_PFC,PCF.PCF_PTC, PCF.PCF_CURTX '
            ' from PLF   inner join PCF  on PLF.PLF_NAME = PCF.PCF_NAME '
            ' and PLF.PLF_SPID=? order by PLF.PLF_OFFBY asc')
        args = (spid, )
        res = self.execute(sql, args, 'dict')
        self.parameter_structures[spid] = res
        return res

    def get_telecommand_info(self,
                             service_type,
                             service_subtype,
                             command_subtype=-1):
        """
            get TC description
        """
        sql = (
            # ,CCF_TYPE, CCF_STYPE, CCF_APID,'
            'select  CCF_CNAME, CCF_DESCR, CCF_DESCR2, '
            ' CCF_NPARS from CCF where CCF_TYPE=? and CCF_STYPE =? order by CCF_CNAME asc'
        )
        res = self.execute(sql, (service_type, service_subtype), 'dict')
        # if command_subtype >= 0 and len(res) > 1:
        # if False:
        # for TC(237,7) , ZIX37701 -- ZIX37724
        # source_id in the header is needed to identify the packet type
        #    return res[command_subtype - 1]
        # command subtype is only used for 237, 7
        # else:
        try:
            return res[0]
        except IndexError:
            return None

    def get_telecommand_structure(self, name):
        """
            Get the structure of a telecommand  by its name
            The structure will be used to decode the TC packet.
        """
        sql = (
            'select CDF_PNAME, CPC_DESCR, CDF_ELTYPE, CDF_ELLEN, CDF_BIT, CDF_GRPSIZE, CDF_INTER,'
            ' CPC_DISPFMT, CPC_CATEG, CPC_PRFREF,CPC_CCAREF, CPC_PAFREF,'
            ' CPC_PTC, CPC_PFC from CPC join CDF on CDF_CNAME=? and '
            'CDF_PNAME=CPC_PNAME  order by CDF_BIT asc')
        args = (name, )
        res = self.execute(sql, args, 'dict')
        return res

    def get_variable_packet_structure(self, spid):
        if spid in self.parameter_structures:
            return self.parameter_structures[spid]
        sql = (
            'select PCF.PCF_NAME,  VPD.VPD_POS,PCF.PCF_WIDTH,PCF.PCF_PFC, PCF.PCF_PTC,VPD.VPD_OFFSET,'
            ' VPD.VPD_GRPSIZE,PCF.PCF_DESCR ,PCF.PCF_CURTX '
            ' from VPD inner join PCF on  VPD.VPD_NAME=PCF.PCF_NAME and VPD.VPD_TPSD=? order by '
            ' VPD.VPD_POS asc')
        res = self.execute(sql, (spid, ), 'dict')
        self.parameter_structures[spid] = res
        return res

    def tcparam_interpret(self, ref, raw):
        """
         interpret telecommand parameter by using the table PAS  
        """
        sql = 'select PAS_ALTXT from PAS where PAS_NUMBR=? and PAS_ALVAL=?'
        args = (ref, raw)
        rows = self.execute(sql, args)
        try:
            return rows[0][0]
        except (TypeError, IndexError):
            return ''
        return ''

    def get_calibration_curve(self, pcf_curtx):
        """ calibration curve defined in CAP database """
        if pcf_curtx in self.calibration_curves:
            return self.calibration_curves[pcf_curtx]
        else:
            sql = ('select cap_xvals, cap_yvals from cap '
                   ' where cap_numbr=? order by cast(CAP_XVALS as double) asc')
            args = (pcf_curtx, )
            rows = self.execute(sql, args)
            self.calibration_curves[pcf_curtx] = rows
            return rows

    def textual_interpret(self, pcf_curtx, raw_value):
        if (pcf_curtx, raw_value) in self.textual_parameter_lut:
            #build the lookup table
            return self.textual_parameter_lut[(pcf_curtx, raw_value)]

        sql = ('select TXP_ALTXT from TXP where  TXP_NUMBR=? and ?>=TXP_FROM '
               ' and TXP_TO>=? limit 1')
        args = (pcf_curtx, raw_value, raw_value)
        rows = self.execute(sql, args)
        self.textual_parameter_lut[(pcf_curtx, raw_value)] = rows
        # lookup table
        return rows

    def get_calibration_polynomial(self, pcf_curtx):
        if pcf_curtx in self.calibration_polynomial:
            return self.calibration_polynomial[pcf_curtx]
        else:
            sql = ('select MCF_POL1, MCF_POL2, MCF_POL3, MCF_POL4, MCF_POL5 '
                   'from MCF where MCF_IDENT=? limit 1')
            args = (pcf_curtx, )
            rows = self.execute(sql, args)
            self.calibration_polynomial[pcf_curtx] = rows
            return rows


def stix_idb(filename=''):
    return _IDB.get_instance(filename)


if __name__ == '__main__':
    """ test  the database interface"""
    import sys
    idb = stix_idb()
    if len(sys.argv) > 1:
        ret = idb.get_variable_packet_structure(sys.argv[1])
        for row in ret:
            print('{}  {} {} {}'.format(row['PCF_NAME'], row['PCF_DESCR'],
                                        row['VPD_POS'], row['PCF_WIDTH']))
