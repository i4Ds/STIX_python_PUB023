#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @author       : Hualin Xiao
# @date         : Feb. 11, 2019
# @description:
#    The following information/database tables are used for extractions of stix parameters
#    header ->  service and sub service -> app header -> SPID ->
#    PLF (paramter list) ->
#    SOSW (parameter name) -> PCF (parameter length and position)  -> S2K_parameter ( type, length)
#    ->TXP, CAP , or MCF interpret parameter
from __future__ import (absolute_import, unicode_literals)
import os
import sys
import math
import re
from scipy import interpolate
import numpy as np
import struct as st
import pprint
from core import idb
from core import stix_global
from core import header as stix_header
STIX_IDB = idb.STIX_IDB

UNSIGNED_UNPACK_STRING = ['B', '>H', 'BBB', '>I', 'BBBBB', '>IH']
SIGNED_UNPACK_STRING = ['b', '>h', 'bbb', '>i', 'bbbbb', '>ih']


def slice_bits(data, offset, length):
    return (data >> offset) & ((1 << length) - 1)
def unpack_integer(raw, structure):
    result = {}
    for name, bits in structure.items():
        result[name] = slice_bits(raw, bits[0], bits[1])
    return result

class StixTelemetryParser:
    def __init__(self, stix_idb=STIX_IDB, logger=None):
        self.logger=logger
        self.idb=stix_idb
    def error(self,msg):
        if self.logger:
            self.logger.error(msg)
    def info(self,msg):
        if self.logger:
            self.logger.info(msg)
    def warning(self,msg):
        if self.logger:
            self.logger.warning(msg)

    def decode(self, in_data, param_type, offset, offset_bit, length):
        nbytes = int(math.ceil((length+ offset_bit) / 8.))
        raw_bin= in_data[int(offset):int(offset + nbytes)]
        if nbytes != len(raw_bin):
            self.error('Invalid data {} real: {}'.format(nbytes, 
                len(raw_bin)))
            return None
        upstr = ''
        if param_type == 'U':
            if nbytes <= 6:
                upstr = UNSIGNED_UNPACK_STRING[nbytes - 1]
            else:
                upstr = str(nbytes) + 's'
        elif param_type == 'I':
            if nbytes <= 6:
                upstr = SIGNED_UNPACK_STRING[nbytes - 1]
            else:
                upstr = str(nbytes) + 's'
        elif param_type == 'T':
            upstr = '>IH'
        elif param_type == 'O':
            upstr = str(nbytes) + 's'
        else:
            upstr = str(nbytes) + 's'
        results = ()
        raw= st.unpack(upstr, raw_bin)

        if upstr == 'BBB':  # 24-bit integer
            value = (raw[0] << 16)| (raw[1] << 8)| raw[2]
            if length< 16 and length% 8 != 0:
                start_bit = nbytes * 8 - (offset_bit + length)
                value= slice_bits(value, start_bit, length)
            results = (value, )
        elif length < 16 and length % 8 != 0:
            # bit-offset only for 8bits or 16 bits integer
            start_bit = nbytes * 8 - (offset_bit + length)
            results = (slice_bits(raw[0], start_bit, length), )
            # checked
        else:
            results = raw
    return results
    def find_next_header(f):
        nbytes = 0
        bad_block = ''
        while True:
            x = f.read(1)
            if not x:
                break
            pos = f.tell()
            bad_block += ' ' + x.hex()
            nbytes += 1
            if x == 0x0D:
                f.seek(pos - 1)
                return True, nbytes, bad_block
        return False, nbytes, bad_block

    def convert_raw_to_eng(self, pcf_curtx, param_type, raw):
        """convert parameter raw values to engineer values"""
        if not raw:
            return None
        if not pcf_curtx:
            if param_type == 'T': #timestamp
                return float(
                    raw[0]) + float(raw[1]) / 65536.
            else:
                return None
            # no need to interpret
        raw_value=raw[0]
        prefix = re.split('\d+', pcf_curtx)[0]
        if prefix in ['CIXTS', 'CAAT', 'CIXT']:
            # textual interpret
            rows = self.idb.get_parameter_textual_interpret(pcf_curtx,raw_value)
            if rows:
                return rows[0][0]

            self.warning('No textual calibration for {}'.format(pcf_curtx))
            return None
        elif prefix =='CIXP':
            rows = self.idb.get_calibration_curve(pcf_curtx)
            if rows:
                x_points = [float(row[0]) for row in rows]
                y_points = [float(row[1]) for row in rows]
                tck = interpolate.splrep(x_points, y_points)
                val=str(interpolate.splev(raw_value, tck))
                return val
            self.warning('No calibration factors for {}'.format(pcf_curtx))
            return None

        elif prefix == 'NIX':
            # temperature
            #if pcf_curtx == 'NIX00101':
                #see SO-STIX-DS-30001_IDeF-X HD datasheet page 29
            #    pass
            self.warning('{} not interpreted. '.format(pcf_curtx))
            return None
        elif prefix == 'CIX':
            rows=self.idb.get_calibration_polynomial(pcf_curtx)
            if rows:
                pol_coeff = ([float(x) for x in rows[0]])
                x_points = ([math.pow(raw_value, i) for i in range(0, 5)])
                sum_value=0
                for a, b in zip(pol_coeff,x_points):
                    sum_value+=a*b
                return sum_value
            self.warning('No calibration factors for {}'.format(pcf_curtx))
            return None
        return None

    def parse_telemetry_parameter(self, app_data, par, calibration=True):
        name = par['PCF_NAME']
        if name == 'NIX00299':
            return None
        offset = par['offset']
        offset_bit = int(par['offset_bit'])
        pcf_width = int(par['PCF_WIDTH'])
        ptc = int(par['PCF_PTC'])
        pfc = int(par['PCF_PFC'])

        s2k_table = self.idb.get_s2k_parameter_types(ptc, pfc)
        param_type = s2k_table['S2K_TYPE']
        raw_values = self.decode(app_data, param_type, offset,
                                      offset_bit, pcf_width)
        if not calibration:
            return {'name': name,
                    'raw': raw_values,
                    'value':None}

        pcf_curtx = par['PCF_CURTX']
        eng_values= self.convert_raw_to_eng(
            pcf_curtx, param_type, raw_values)
        return {
            'name': name,
            'raw': raw_values,
            'value': eng_values}

    def parse_telemetry_header(self,packet):
        """ see STIX ICD-0812-ESC  (Page # 57) """
        if packet[0] != 0x0D:
            return stix_global.HEADER_FIRST_BYTE_INVALID, None
        header_raw = st.unpack('>HHHBBBBIH', packet[0:16])
        header = {}
        for h, s in zip(header_raw, stix_header.telemetry_raw_structure):
            header.update(unpack_integer(h, s))
        status= self.check_header(header,'tm')
        if status == stix_global.OK:
            header.update({'segmentation': stix_header.packet_seg[header['seg_flag']]})
            header.update(
                {'time': header['fine_time'] / 65536. + header['coarse_time']})
        return status, header


    def check_header(self, header,tmtc='tm'):
        # header validate
        constrains=None
        if tmtc=='tm':
            constrains=stix_header.telemetry_header_constraints
        else:
            constrains=stix_header.telecommand_header_constraints
        for name, lim in constrains.items():
            if header[name] not in lim:
                return stix_global.HEADER_INVALID
        return stix_global.OK

    def decode_app_header(self, header, data, length):
        """ Decode the data field header  
        """
        service_type = header['service_type']
        service_subtype = header['service_subtype']
        offset, width = self.idb.get_packet_type_offset(service_type,
                                                        service_subtype)
        # see solar orbit ICD Page 36
        SSID= -1
        if offset != -1:
            start = offset - 16  # 16bytes read already
            end = start + width / 8  # it can be : 0, 16,8
            upstr= '>B'
            if width == 16:
                upstr= '>H'
            res = st.unpack(upstr, data[int(start):int(end)])
            SSID= res[0]
        info = self.idb.get_packet_type_info(service_type, service_subtype,
                                                  SSID)
        header['DESCR']=info['PID_DESCR']
        header['SPID']=info['PID_SPID']
        header['TPSD']=info['PID_TPSD']
        header['length']=length
        header['SSID']=SSID

    def parse_fixed_packet(self, buf, spid):
        param_struct= self.idb.get_fixed_packet_structure(spid)
        return self.get_fixed_packet_parameters(buf, param_struct)

    def get_fixed_packet_parameters(self, buf, param_struct):
        """ Extract parameters from a fixed data packet see Solar orbit IDB ICD section 3.3.2.5.1
        """
        params= []
        for par in param_struct:
            par['offset'] = int(par['PLF_OFFBY']) - 16
            par['offset_bit'] = int(par['PLF_OFFBI'])
            par['type'] = 'fixed'
            parameter = parse_telemetry_parameter(buf, par)
            params.append(parameter)
        return params

    def format_parse_result(self,status,length, header=None, header_raw=None,
            app_raw=None):
        return {'status': status,
                'header': header, 
                'header_raw':header_raw, 
                'app_raw':app_raw,
                'num_read': length
                }
    def read_one_packet(self, in_file):
        start_pos = in_file.tell()
        header_raw= in_file.read(16)
        cur_pos = in_file.tell()
        num_read=cur_pos-start_pos

        if not header_raw:
            return self.format_parse_result(stix_global.EOF, header_raw=header_raw, 
                    length=len(header_raw))

        header_status, header = self.parse_telemetry_header(header_raw)

        if header_status != stix_global.OK:
            self.warning('Bad header at {}, code {} '.format(in_file.tell(), header_status))
            found, num_skipped, bad_block = find_next_header(in_file)

            cur_pos = in_file.tell()
            num_read=cur_pos-start_pos
            self.warning('''Unexpected block around {}, 
                            Number of bytes skipped: {}'''.format(
                in_file.tell(),num_skipped))
            if found:
                self.info('New header at ', cur_pos)
                return self.format_parse_result(stix_global.NEXT_PACKET, 
                        num_read, header_raw=header_raw)
            else:
                return self.format_parse_result(stix_global.EOF, 
                        num_read, header_raw=header_raw)

        app_length =header['length']+9
        if app_length <= 0:  # wrong packet length
            self.warning('Source data length 0')
            return self.format_parse_result(stix_global.NEXT_PACKET,
                    num_read, header_raw=header_raw)

        app_data = in_file.read(app_length)

        num_read=in_file.tell()-start_pos

        actual_length=len(app_data)
        if actual_length != app_length:

        self.error("Incomplete data packet! pos:  {}, expect: {}, actual: {}, ".format(
            in_file.tell(), app_length, actual_length))
            return self.format_parse_result(stix_global.EOF, num_read,header_raw=header_raw)
        self.decode_app_header(header, app_data, app_length)
        return self.format_parse_result(stix_global.OK, num_read, 
                header, header_raw, app_data)


class StixTelecommandParser(StixTelemetryParser):
    def __init__(self, stix_idb=STIX_IDB, logger=None):
        supper().__init__(stix_idb,logger)
    def parse_telecommand_header(self, packet):
        # see STIX ICD-0812-ESC  (Page
        # 56)
        if packet[0] != 0x1D:
            return stix_global.HEADER_FIRST_BYTE_INVALID, None
        header_raw = st.unpack('>HHHBBBB', packet[0:10])
        header = {}
        for h, s in zip(header_raw, stix_header.telecommand_raw_structure):
            header.update(unpack_integer(h, s))
        status= check_header(header,'tc')
        info=self.idb.get_telecommand_characteristics(header['service_type'],
                header['service_subtype'], header['source_id'])
        header['DESCR']=info['CCF_DESCR']+' - ' +info['CCF_DESCR2']
        header['SPID']=''
        header['name']=info['CCF_CNAME']
        if status == stix_global.OK:
            try:
                header['ACK_DESC']=stix_header.ACK_mapping[header['ACK']]
            except KeyError:
                status=stix_global.HEADER_KEY_ERROR
        return status, header

    def parse_telecommand_parameter(self.header,packet):
        pass
    def parse_telecommand_packet(self, buf, logger=None):
        header_status,header=self.parse_telecommand_header(buf)
        if header_status != stix_global.OK and logger:
            logger.warning('Bad telecommand header ')
        else:
            pprint.pprint(header)
        return header,None

