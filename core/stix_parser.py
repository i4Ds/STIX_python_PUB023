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
#from __future__ import (absolute_import, unicode_literals)
import os
import sys
import math
import re
from scipy import interpolate
import numpy as np
import struct as st
import pprint
import binascii
from core import idb
from core import stix_global
from core import header as stix_header
from core import stix_logger
from core import stix_writer

_unsigned_format = ['B', '>H', 'BBB', '>I', 'BBBBB', '>IH']
_signed_format = ['b', '>h', 'bbb', '>i', 'bbbbb', '>ih']
_stix_idb = idb._stix_idb
_stix_logger = stix_logger._stix_logger


def slice_bits(data, offset, length):
    return (data >> offset) & ((1 << length) - 1)


def unpack_integer(raw, structure):
    result = {}
    for name, bits in structure.items():
        result[name] = slice_bits(raw, bits[0], bits[1])
    return result


def substr(buf, i, width=1):
    data = buf[i:i + width]
    length = len(data)
    if length != width:
        return False, i + length, data
    else:
        return True, i + length, data


def find_next_header(buf, i):
    nbytes = 0
    bad_block = ''
    length = len(buf)
    while i < length:
        x = buf[i]
        if x == 0x0D or x == 0x1D:
            return i
        else:
            i += 1
    return stix_global._eof


class StixParameterParser:
    def __init__(self):
        pass

    def decode(self, in_data, param_type, offset, offset_bit, length,param_name=''):
        nbytes = int(math.ceil((length + offset_bit) / 8.))
        raw_bin = in_data[int(offset):int(offset + nbytes)]
        if nbytes != len(raw_bin):
            _stix_logger.error(
                'Data length mismatch when unpacking parameter {}.  Expect: {} real: {}'.format(
                    param_name, nbytes, len(raw_bin)))
            return None
        upstr = ''
        if param_type == 'U':
            if nbytes <= 6:
                upstr = _unsigned_format[nbytes - 1]
            else:
                upstr = str(nbytes) + 's'
        elif param_type == 'I':
            if nbytes <= 6:
                upstr = _signed_format[nbytes - 1]
            else:
                upstr = str(nbytes) + 's'
        elif param_type == 'T':
            upstr = '>IH'
        elif param_type == 'O':
            upstr = str(nbytes) + 's'
        else:
            upstr = str(nbytes) + 's'
        results = ()
        raw = st.unpack(upstr, raw_bin)

        if upstr == 'BBB':  # 24-bit integer
            value = (raw[0] << 16) | (raw[1] << 8) | raw[2]
            if length < 16 and length % 8 != 0:
                start_bit = nbytes * 8 - (offset_bit + length)
                value = slice_bits(value, start_bit, length)
            results = (value, )
        elif length < 16 and length % 8 != 0:
            # bit-offset only for 8bits or 16 bits integer
            start_bit = nbytes * 8 - (offset_bit + length)
            results = (slice_bits(raw[0], start_bit, length), )
            # checked
        else:
            results = raw

        return results

    def convert_raw_to_eng(self, pcf_curtx, param_type, raw):
        """convert parameter raw values to engineer values"""
        if not raw:
            return None
        if not pcf_curtx:
            if param_type == 'T':  #timestamp
                return float(raw[0]) + float(raw[1]) / 65536.
            else:
                return ''
            # no need to interpret
        raw_value = raw[0]
        prefix = re.split('\d+', pcf_curtx)[0]
        if prefix in ['CIXTS', 'CAAT', 'CIXT']:
            # textual interpret
            rows = _stix_idb.get_parameter_textual_interpret(
                pcf_curtx, raw_value)
            if rows:
                return rows[0][0]

            _stix_logger.warn(
                'No textual calibration for {}'.format(pcf_curtx))
            return ''
        elif prefix == 'CIXP':
            rows = _stix_idb.get_calibration_curve(pcf_curtx)
            if rows:
                x_points = [float(row[0]) for row in rows]
                y_points = [float(row[1]) for row in rows]
                tck = interpolate.splrep(x_points, y_points)
                val = str(interpolate.splev(raw_value, tck))
                return val
            _stix_logger.warn(
                'No calibration factors for {}'.format(pcf_curtx))
            return ''

        elif prefix == 'NIX':
            # temperature
            #if pcf_curtx == 'NIX00101':
            #see SO-STIX-DS-30001_IDeF-X HD datasheet page 29
            #    pass
            _stix_logger.warn('{} not interpreted. '.format(pcf_curtx))
            return ''
        elif prefix == 'CIX':
            rows = _stix_idb.get_calibration_polynomial(pcf_curtx)
            if rows:
                pol_coeff = ([float(x) for x in rows[0]])
                x_points = ([math.pow(raw_value, i) for i in range(0, 5)])
                sum_value = 0
                for a, b in zip(pol_coeff, x_points):
                    sum_value += a * b
                return sum_value
            _stix_logger.warn(
                'No calibration factors for {}'.format(pcf_curtx))
            return ''
        return ''

    def parse_telemetry_parameter(self, app_data, par, calibration=True):

        name = par['PCF_NAME']
        offset = par['offset']
        offset_bit = int(par['offset_bit'])
        pcf_width = int(par['PCF_WIDTH'])
        ptc = int(par['PCF_PTC'])
        pfc = int(par['PCF_PFC'])

        s2k_table = _stix_idb.get_s2k_parameter_types(ptc, pfc)
        param_type = s2k_table['S2K_TYPE']
        raw_values = self.decode(app_data, param_type, offset, offset_bit,
                                 pcf_width, param_name=name)
        if not calibration:
            return {
                'name': name,
                'raw': raw_values,
                'desc': par['PCF_DESCR'],
                'value': ''
            }

        pcf_curtx = par['PCF_CURTX']
        eng_values = self.convert_raw_to_eng(pcf_curtx, param_type, raw_values)
        return {
            'name': name,
            'raw': raw_values,
            'desc': par['PCF_DESCR'],
            'value': eng_values
        }


class StixVariablePacketParser(StixParameterParser):
    """
    Variable length packet parser
    """

    def __init__(self):
        self.debug = False
        self.nodes_LUT = []
        self.last_spid = -1

    def debug_enabled(self):
        self.debug = True

    def init_nodes(self):
        self.nodes = []
        self.nodes.append(
            self.create_node('top', 0, 0, 0, stix_global._max_parameters, None,
                             1))
        self.nodes[0]['children'] = []
        self.length_min = 0

    def load_nodes(self, spid):
        for node in self.nodes_LUT:
            if spid == node['spid']:
                self.nodes = node['nodes']
                self.length_min = node['length_min']
                return True
        return False

    def store_current_nodes(self):
        node = {
            'spid': self.spid,
            'nodes': self.nodes,
            'length_min': self.length_min
        }

        self.nodes_LUT.append(node)  #copy

    def parse(self, data, spid, output_type='tree'):
        """
        """
        self.output_type = output_type
        self.source_data = data
        self.spid = spid
        self.current_offset = 0
        self.last_offset = 0
        self.current_offset_bit = 0
        self.results_tree = []
        self.results_tree[:] = []
        self.results_dict = {}
        self.results_dict.clear()

        if spid != self.last_spid:
            self.init_nodes()
            self.build_tree()

        #    if not self.load_nodes(spid):
        #        self.init_nodes()
        #        self.build_tree()
        #        self.store_current_nodes()

        self.last_spid = spid

    def get_parameters(self):

        packet_length = len(self.source_data)
        if self.length_min > packet_length:
            return 0, None, stix_global._variable_packet_length_mismatch
        if self.output_type == 'tree':
            self.walk_to_tree(self.nodes[0], self.results_tree)
            return self.current_offset, self.results_tree, stix_global._ok
        else:
            self.walk_to_array(self.nodes[0])
            return self.current_offset, self.results_dict, stix_global._ok

    def create_node(self,
                    name,
                    position,
                    width,
                    offset_bit,
                    repeat_size,
                    parameter,
                    counter=0,
                    desc='',
                    children=[]):
        node = {
            'name': name,
            'offset_bit': offset_bit,
            'position': position,
            'repeat_size': repeat_size,
            'counter': counter,
            #'width': width,
            'parameter': parameter,
            'children': children,
            #'desc': desc
        }
        return node

    def get_parameter_description(self):
        #return self.parameter_desc
        pass

    def register_parameter(self,
                           mother,
                           name,
                           position,
                           width,
                           offset_bit,
                           repeat_size,
                           parameter,
                           counter,
                           desc='',
                           children=[]):
        node = self.create_node(name, position, width, offset_bit, repeat_size,
                                parameter, counter, desc, children)
        if width % 8 == 0:
            self.length_min += width / 8
        mother['children'].append(node)
        return node

    def build_tree(self):
        """
        To build a parameter tree 
        """
        structures = _stix_idb.get_variable_packet_structure(self.spid)

        mother = self.nodes[0]
        repeater = [{'node': mother, 'counter': stix_global._max_parameters}]
        #counter:  number of repeated times

        for par in structures:
            #self.parameter_desc[par['PCF_NAME']]=par['PCF_DESCR']
            if repeater:
                for e in reversed(repeater):
                    e['counter'] -= 1
                    if e['counter'] < 0:
                        repeater.pop()
            mother = repeater[-1]['node']
            node = self.register_parameter(
                mother, par['PCF_NAME'], par['VPD_POS'], par['PCF_WIDTH'],
                par['VPD_OFFSET'], par['VPD_GRPSIZE'], par, 0,
                par['PCF_DESCR'], [])
            rpsize = par['VPD_GRPSIZE']
            if rpsize > 0:
                mother = node
                repeater.append({'node': node, 'counter': rpsize})

    def pprint_par(self, st):
        if self.debug:
            print(('%s %s  %s %s %s %s %s %s\n') %
                  (str(st['VPD_POS']), st['VPD_NAME'], st['VPD_GRPSIZE'],
                   st['VPD_OFFSET'], str(st['PCF_WIDTH']), str(st['offset']),
                   str(st['offset_bit']), st['PCF_DESCR']))

    def pprint_structure(self, structures):
        if self.debug:
            pprint.pprint(structures)
            for st in structures:
                print(
                    ('%s %s  %s %s %s %s\n') %
                    (str(st['VPD_POS']), st['VPD_NAME'], st['VPD_GRPSIZE'],
                     st['VPD_OFFSET'], str(st['PCF_WIDTH']), st['PCF_DESCR']))

    def walk_to_array(self, mother):
        """
        Parameter tree traversal
        """
        if not mother:
            return
        result_node = None
        counter = mother['counter']
        parameter_values = {}
        for i in range(0, counter):
            for node in mother['children']:
                if not node or self.current_offset > len(self.source_data):
                    return None
                result = self.parse_parameter(node)
                value = result['raw'][0]
                name = node['name']
                if name in self.results_dict:
                    self.results_dict[name].append(value)
                else:
                    self.results_dict[name] = [value]
                if node['children']:
                    node['counter'] = value
                    self.walk_to_array(node)

    def walk_to_tree(self, mother, para):
        if not mother:
            return
        result_node = None
        counter = mother['counter']
        for i in range(0, counter):
            for node in mother['children']:
                if not node or self.current_offset > len(self.source_data):
                    return
                result = self.parse_parameter(node)
                result_node = {
                    'name': node['name'],
                    'raw': result['raw'],
                    'desc': result['desc'],
                    'value': result['value'],
                    'children': []
                }
                if node['children']:
                    node['counter'] = result['raw'][0]
                    self.walk_to_tree(node, result_node['children'])
                para.append(result_node)

    def parse_parameter(self, node):
        """
        parse a parameter. 
        The offset, offset bit and parameter name are described in 'node'
        """
        par = node['parameter']
        width = par['PCF_WIDTH']
        vpd_offset = par['VPD_OFFSET']
        if width % 8 != 0:
            if vpd_offset < 0:
                self.current_offset_bit = self.last_data_width + vpd_offset
            else:
                self.current_offset_bit += self.last_num_bits + vpd_offset
            self.last_num_bits = width
        elif width % 8 == 0:
            self.current_offset_bit = 0
            self.last_offset = self.current_offset
            self.current_offset += width / 8
            self.last_num_bits = 0
            self.last_data_width = width

        par['offset'] = self.last_offset
        par['offset_bit'] = self.current_offset_bit

        calibration = False
        if self.output_type == 'tree':
            calibration = True
        return self.parse_telemetry_parameter(self.source_data, par,
                                              calibration)


class StixTCTMParser(StixParameterParser):
    def __init__(self):
        self.vp_parser = StixVariablePacketParser()

    def parse_telemetry_header(self, packet):
        """ see STIX ICD-0812-ESC  (Page # 57) """

        if ord(packet[0:1]) != 0x0D:
            return stix_global._header_first_byte_invalid, None

        header_raw = st.unpack('>HHHBBBBIH', packet[0:16])
        header = {}
        for h, s in zip(header_raw, stix_header._telemetry_raw_structure):
            header.update(unpack_integer(h, s))
        status = self.check_header(header, 'tm')
        if status == stix_global._ok:
            header.update(
                {'segmentation': stix_header._packet_seg[header['seg_flag']]})
            header['TMTC'] = 'TM'
            header.update(
                {'time': header['fine_time'] / 65536. + header['coarse_time']})
        return status, header

    def check_header(self, header, tmtc='tm'):
        # header validate
        constrains = None
        if tmtc == 'tm':
            constrains = stix_header._telemetry_header_constraints
        else:
            constrains = stix_header._telecommand_header_constraints
        for name, lim in constrains.items():
            if header[name] not in lim:
                print("header invalide")
                print(name)
                return stix_global._header_invalid
        return stix_global._ok

    def decode_app_header(self, header, data, length):
        """ Decode the data field header  
        """
        service_type = header['service_type']
        service_subtype = header['service_subtype']
        offset, width = _stix_idb.get_packet_type_offset(
            service_type, service_subtype)
        # see solar orbit ICD Page 36
        SSID = -1
        if offset != -1:
            start = offset - 16  # 16bytes read already
            end = start + width / 8  # it can be : 0, 16,8
            upstr = '>B'
            if width == 16:
                upstr = '>H'
            res = st.unpack(upstr, data[int(start):int(end)])
            SSID = res[0]
        info = _stix_idb.get_packet_type_info(service_type, service_subtype,
                                              SSID)
        header['DESCR'] = info['PID_DESCR']
        header['SPID'] = info['PID_SPID']
        header['TPSD'] = info['PID_TPSD']
        header['length'] = length
        header['SSID'] = SSID

    def parse_fixed_packet(self, buf, spid):
        param_struct = _stix_idb.get_fixed_packet_structure(spid)
        return self.get_fixed_packet_parameters(
            buf, param_struct, calibration=True)

    def get_fixed_packet_parameters(self, buf, param_struct, calibration):
        """ Extract parameters from a fixed data packet see Solar orbit IDB ICD section 3.3.2.5.1
        """
        params = []
        for par in param_struct:
            par['offset'] = int(par['PLF_OFFBY']) - 16
            par['offset_bit'] = int(par['PLF_OFFBI'])
            par['type'] = 'fixed'
            parameter = self.parse_telemetry_parameter(buf, par, calibration)
            params.append(parameter)
        return params

    def parse_telecommand_header(self, packet):
        # see STIX ICD-0812-ESC  (Page
        # 56)
        if packet[0] != 0x1D:
            return stix_global._header_first_byte_invalid, None
        header_raw = st.unpack('>HHHBBBB', packet[0:10])
        header = {}
        for h, s in zip(header_raw, stix_header._telecommand_raw_structure):
            header.update(unpack_integer(h, s))
        status = self.check_header(header, 'tc')
        info = _stix_idb.get_telecommand_characteristics(
            header['service_type'], header['service_subtype'],
            header['source_id'])
        if not info:
            return stix_global._header_key_error, header

        header['DESCR'] = info['CCF_DESCR'] + ' - ' + info['CCF_DESCR2']
        header['SPID'] = ''
        header['name'] = info['CCF_CNAME']
        header['TMTC'] = 'TC'
        header['time'] = 0
        if status == stix_global._ok:
            try:
                header['ACK_DESC'] = stix_header._ACK_mapping[header['ACK']]
            except KeyError:
                status = stix_global._header_key_error
        return status, header

    def parse_telecommand_parameter(self, header, packet):
        pass

    def parse_telecommand_packet(self, buf):
        pass

    def parse_file(self,
                   in_filename,
                   out_filename=None,
                   selected_spid=0,
                   pstruct='tree', file_type='binary', comment=''):
        _stix_logger.info('Processing file: {}'.format(in_filename))
        packets=[]
        file_size=os.path.getsize(in_filename)
        if file_type=='binary':
            with open(in_filename, 'rb') as in_file:
                data = in_file.read()
                _stix_logger.info("File size:{} kB ".format(len(data) / 1024))
                packets = self.parse_binary(data, 0, pstruct, selected_spid)
        elif file_type=='ascii':
            packets = self.parse_moc_ascii(in_filename, pstruct, selected_spid)
        else:
            _stix_logger.error('{} has unknown input file type'.format(in_filename))



        st_writer = None
        if out_filename.endswith(('.pkl', '.pklz')):
            st_writer = stix_writer.StixPickleWriter(out_filename)
        elif out_filename.endswith(('.db', '.sqlite')):
            st_writer = stix_writer.StixSqliteWriter(out_filename)
        elif 'mongo' in out_filename:
            st_writer = stix_writer.StixMongoWriter()
        else:
            _stix_logger.warn('Result will not be saved.')

        if st_writer:
            st_writer.register_run(in_filename, file_size, comment)
            _stix_logger.info(
                'Writing parameters to file {} ...'.format(out_filename))
            st_writer.write_all(packets)
            _stix_logger.info('Done.')
        else:
            return packets

    def parse_binary(self, buf, i=0, pstruct='tree', selected_spid=0):
        length = len(buf)
        if i >= length:
            return
        packets = []
        fix = 0
        total = 0
        var = 0
        tc = 0
        last = 0
        while i < length:
            if buf[i] == 0x0D:
                total += 1
                status, i, header_raw = substr(buf, i, 16)
                if status == stix_global._eof:
                    break
                header_status, header = self.parse_telemetry_header(header_raw)
                if header_status != stix_global._ok:
                    _stix_logger.warn('Bad header at {}, code {} '.format(
                        i, header_status))
                    continue

                app_length = header['length'] - 9
                status, i, app_raw = substr(buf, i, app_length)
                if status == stix_global._eof:
                    break

                self.decode_app_header(header, app_raw, app_length)
                tpsd = header['TPSD']
                spid = header['SPID']
                if selected_spid > 0 and selected_spid != spid:
                    continue
                parameters = None
                if tpsd == -1:
                    parameters = self.parse_fixed_packet(app_raw, spid)
                    fix += 1
                else:
                    var += 1
                    self.vp_parser.parse(app_raw, spid, pstruct)
                    num_read, parameters, status = self.vp_parser.get_parameters(
                    )
                    if num_read != app_length:
                        _stix_logger.warn(
                            "Variable packet length inconsistent! SPID: {}, Actual: {}, IDB: {}"
                            .format(spid, num_read, app_length))
                packets.append({'header': header, 'parameters': parameters})
            elif buf[i] == 0x1D:
                total += 1
                tc += 1
                status, i, header_raw = substr(buf, i, 12)
                if status == stix_global._eof:
                    break
                header_status, header = self.parse_telecommand_header(
                    header_raw)

                if header_status != stix_global._ok:
                    _stix_logger.warn(
                        "A bad telecommand packet found, cursor at: {} ".
                        format(i - 12))
                    continue
                app_length = header['length'] - 6 + 1
                status, i, app_raw = substr(buf, i, app_length)
                if status == stix_global._eof:
                    break
                packets.append({'header': header, 'parameters': None})

            else:
                old_i = i
                _stix_logger.warn('bad header {} at {}!'.format(buf[i], i))
                i = find_next_header(buf, i)
                if i == stix_global._eof:
                    break
                _stix_logger.warn(
                    'New header find at {}, {} bytes skipped!'.format(
                        i, i - old_i))

            current = int(100. * i / length)
            if current > last:
                _stix_logger.info('{}% loaded'.format(current))
            last = current

        _stix_logger.info(
            'total packets: {}; TM: {} (fix:{} variable: {}); TC:{}'.format(
                total, fix + var, fix, var, tc))
        return packets
    def parse_moc_ascii(self, filename, pstruct='tree', selected_spid=0):
        packets=[]
        with open(filename) as fd:
            _stix_logger.info('Reading packets from the file {}'.format(filename))
            idx=0
            for line in fd:
                [utc_timestamp, data_hex] = line.strip().split()
                data_binary = binascii.unhexlify(data_hex)
                packet=self.parse_binary(data_binary,0,'tree',selected_spid)
                if packet:
                    packet[0]['header']['utc']=utc_timestamp
                    packets.extend(packet)
                if idx%10==0:
                    _stix_logger.info('{} packet have been read'.format(idx))
                idx+=1
        return packets




