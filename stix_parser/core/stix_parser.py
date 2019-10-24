#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @date         : Feb. 11, 2019
# @description:
#               STIX telemetry raw data parser
# @TODO
#              add checks for CRC for TC packet

import math
import os
import re
import struct as st
import binascii
import pathlib
import xmltodict
from scipy import interpolate
from dateutil import parser as dtparser
from . import stix_header
from . import stix_idb
from . import stix_global
from . import stix_logger
from . import stix_writer
from . import stix_context
from . import stix_parameter
from . import stix_decompressor
from . import stix_datetime

from pprint import pprint
CONTEXT_UNPACK_FORMAT = ['B', '>H', 'BBB', '>I']
UNSIGNED_UNPACK_FORMAT = ['B', '>H', 'BBB', '>I', 'BBBBB', '>IH']
SIGNED_UNPACK_FORMAT = ['b', '>h', 'bbb', '>i', 'bbbbb', '>ih']
HEX_SPACE = '0123456789ABCDEFabcdef'
PARMETERS_CALIBRATION_ENABLED = ['NIX00101', 'NIX00102']

STIX_IDB = stix_idb.stix_idb()
STIX_LOGGER = stix_logger.stix_logger()
STIX_DECOMPRESSOR = stix_decompressor.StixDecompressor()
stix_parameter.StixParameter.set_decompressor(STIX_DECOMPRESSOR)


def detect_filetype(filename):
    filetype = None
    extension = pathlib.Path(filename).suffix
    ext=extension[1:]
    
    if ext in ('xml', 'ascii', 'bin', 'hex'):
        return ext
    elif ext in ('binary', 'raw', 'BDF', 'dat'):
        return 'bin'
    try:
        f = open(filename, 'r')
        buf = f.read(1024).strip()
        data = re.sub(r"\s+", "", buf)
        filetype = 'hex'
        for c in data:
            if c not in HEX_SPACE:
                filetype = 'ascii'
                #possibly ASCII
                break
    except UnicodeDecodeError:
        filetype = 'bin'
    finally:
        f.close()
    return filetype


def get_bits(data, offset, length):
    return (data >> offset) & ((1 << length) - 1)


def unpack_integer(raw, structure):
    result = {}
    for name, bits in structure.items():
        result[name] = get_bits(raw, bits[0], bits[1])
    return result


def get_from_bytearray(buf, i, width=1):
    data = buf[i:i + width]
    length = len(data)
    if length != width:
        return False, i + length, data
    else:
        return True, i + length, data


def find_next_header(buf, i):
    length = len(buf)
    while i < length:
        x = buf[i]
        if x in stix_header.HEADER_FIRST_BYTE:
            return i
        else:
            i += 1
    return stix_global.EOF


class StixParameterParser(object):
    def __init__(self):
        pass
        #super(StixParameterParser, self).__init__()

    def set_parameter_format(self, fmt):
        """ define how parameters are stored: 
            tuples or hash table
            If it is 'tuple', the structure of a parameter will be:
            (PARAMETER_NAME, RAW_VALUE, ENGINEERING_VALUE, CHILDREN) 
            if it is 'dict', it will be:
            {
              'name': PARAMETER_NAME,
              'raw':  (RAW_VALUE,)
              'eng':  ENGINEERING_VALUE,
              'children':[ ] 
            }
        """
        stix_parameter.StixParameter.set_format(fmt)

    def decode_buffer(self,
                      in_data,
                      param_type,
                      offset,
                      offset_bits,
                      length,
                      param_name=''):
        """
        unpack binary
        parameter_type:
            parameter type
        offset:
            offset in units of bits
        offset_bits:
            bits offset
        """
        nbytes = math.ceil((length + offset_bits) / 8.)

        raw_bin = in_data[int(offset):int(offset + nbytes)]

        if nbytes != len(raw_bin):
            STIX_LOGGER.error(
                'Parameter {} length mismatch.  Expect: {} real: {}'.format(
                    param_name, nbytes, len(raw_bin)))
            return None
        bin_struct = str(nbytes) + 's' #signed char
        if param_type == 'U' and nbytes <= 6:
            bin_struct = UNSIGNED_UNPACK_FORMAT[nbytes - 1]
        elif param_type == 'I' and nbytes <= 6:
            bin_struct = SIGNED_UNPACK_FORMAT[nbytes - 1]
        elif param_type == 'T':
            bin_struct = '>IH'
        elif param_type == 'CONTEXT' and nbytes <= 4:
            bin_struct = CONTEXT_UNPACK_FORMAT[nbytes - 1]
        #elif param_type == 'O':
        #    bin_struct = str(nbytes) + 's'
        results = ()
        raw = st.unpack(bin_struct, raw_bin)
        if bin_struct == 'BBB':  # 24-bit integer, a timestamp probably
            value = (raw[0] << 16) | (raw[1] << 8) | raw[2]
            if length < 16 and length % 8 != 0:
                start_bit = nbytes * 8 - (offset_bits + length)
                value = get_bits(value, start_bit, length)
            results = (value, )
        elif length < 16 and length % 8 != 0:
            # bit-offset only for 8 bits or 16 bits integer
            start_bit = nbytes * 8 - (offset_bits + length)
            results = (get_bits(raw[0], start_bit, length), )
        else:
            results = raw
        return results

    def convert_raw_to_eng(self, param_name, ref, param_type, raw, tmtc='TM'):
        """convert parameter raw values to engineer values"""
        """
        Inputs:
            param_name:  
                parameter name
            ref:
                calibration reference name
            param_type:
                parameter type
            raw:
                parameter raw value
            TMTC:
                TC or TM
        Returns:
            engineering value
        """

        if not raw:
            return ''

        raw_value = raw[0]
        if tmtc == 'TC':
            if ref:
                return STIX_IDB.tcparam_interpret(ref, raw[0])
            return ''
        elif param_name == 'NIX00101':
            #conversion based on the equation in SIRIUS source code
            return (raw_value * 1.1 * 3.0 / 4095 - 1.281) * 213.17
        elif param_name == 'NIX00102':
            #temperature std. deviations
            return (raw_value * 1.1 * 3.0 / 4095) * 213.17
        elif not ref:
            if param_type == 'T':  # timestamp
                #coarse time + fine time/2^16
                return round(float(raw[0]) + float(raw[1]) / 65536., 3)
            return ''

        #other parameters
        prefix = re.split(r'\d+', ref)[0]
        if prefix in ['CIXTS', 'CAAT', 'CIXT']:
            # textual interpret
            rows = STIX_IDB.textual_interpret(ref, raw_value)
            if rows:
                return rows[0][0]
            STIX_LOGGER.warn(
                'Missing textual calibration info. for {}'.format(ref))
            return ''
        elif prefix == 'CIXP':
            #calibration
            rows = STIX_IDB.get_calibration_curve(ref)
            if rows:
                x_points = [float(row[0]) for row in rows]
                y_points = [float(row[1]) for row in rows]
                tck = interpolate.splrep(x_points, y_points)
                val = interpolate.splev(raw_value, tck)
                try:
                    ret = round(float(val), 3)
                except TypeError:
                    ret = ''
                return ret
            STIX_LOGGER.warn('No calibration factors for {}'.format(ref))
            return ''
        elif prefix == 'NIX':
            STIX_LOGGER.warn('{} not interpreted. '.format(ref))
            return ''
        elif prefix == 'CIX':
            rows = STIX_IDB.get_calibration_polynomial(ref)
            if rows:
                pol_coeff = ([float(x) for x in rows[0]])
                x_points = ([math.pow(raw_value, i) for i in range(0, 5)])
                sum_value = 0
                for coeff, xval in zip(pol_coeff, x_points):
                    sum_value += coeff * xval
                return round(sum_value, 3)
            STIX_LOGGER.warn('Missing calibration factors for {}'.format(ref))
            return ''
        return ''

    def decode_parameter(self,
                         buf,
                         name,
                         offset,
                         offset_bits,
                         width,
                         ptc,
                         pfc,
                         cal_ref='',
                         tmtc='TM',
                         calibration_enabled=True):
        """
            Decode and calibrate a parameter 
        """
        param_type = STIX_IDB.get_s2k_parameter_types(ptc, pfc)
        raw_values = self.decode_buffer(buf, param_type, offset, offset_bits,
                                        width, name)
        eng_values = ''
        if calibration_enabled:
            eng_values = self.convert_raw_to_eng(name, cal_ref, param_type,
                                                 raw_values, tmtc)

        return stix_parameter.StixParameter(name, raw_values,
                                            eng_values).parameter


class StixVariableTelemetryPacketParser(StixParameterParser):
    """
        Variable length telemetry packet parser
    """

    def __init__(self):
        super(StixVariableTelemetryPacketParser, self).__init__()
        self.debug = False
        self.last_spid = -1
        self.last_num_bits = 0
        self.last_data_width = 0
        self.current_offset_bit = 0
        self.length_min = 0
        self.nodes = []
        self.buffer = None
        self.spid = 0
        self.current_offset = 0
        self.last_offset = 0
        self.results_tree = []
        self.results_dict = {}

    def debug_enabled(self):
        self.debug = True

    def init_nodes(self):
        self.nodes = []
        self.nodes.append(self.create_parse_node('top', counter=1))
        self.nodes[0]['children'] = []
        self.length_min = 0

    def parse(self, data, spid):
        self.last_data_width = 0
        self.last_num_bits = 0
        self.buffer = data
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
            self.build_parse_tree()

        self.last_spid = spid
        packet_length = len(self.buffer)
        if self.length_min > packet_length:
            return 0, None, stix_global.VARIABLE_PACKET_LENGTH_MISMATCH
        self.walk(self.nodes[0], self.results_tree)
        return self.current_offset, self.results_tree, stix_global.OK

    def create_parse_node(self, name, parameter=None, counter=0,
                          children=None):

        if children is None:
            children = []
        node = {
            'name': name,
            'counter': counter,
            'parameter': parameter,
            'children': children
        }
        return node

    def register_parameter(self, mother, param_PCF):
        children = []
        name = param_PCF['PCF_NAME']
        node = self.create_parse_node(name, param_PCF, 0, children)
        width = param_PCF['PCF_WIDTH']
        if width % 8 == 0:
            self.length_min += width / 8
        mother['children'].append(node)
        return node

    def build_parse_tree(self):
        """
        To build a parameter parse tree
        """
        param_pcf_structures = STIX_IDB.get_variable_packet_structure(
            self.spid)

        mother = self.nodes[0]
        repeater = [{
            'node': mother,
            'counter': stix_global.MAX_NUM_PARAMETERS
        }]
        for par in param_pcf_structures:
            if repeater:
                for e in reversed(repeater):
                    e['counter'] -= 1
                    if e['counter'] < 0:
                        repeater.pop()
                        #root will be never popped
            mother = repeater[-1]['node']
            node = self.register_parameter(mother, par)

            rpsize = par['VPD_GRPSIZE']
            if rpsize > 0:
                mother = node
                repeater.append({'node': node, 'counter': rpsize})

    def walk(self, mother, parameter_list):
        if not mother:
            return
        counter = mother['counter']
        for i in range(0, counter):
            for pnode in mother['children']:
                if not pnode or self.current_offset > len(self.buffer):
                    return
                ret = self.decode_parameter_for(pnode)
                param = stix_parameter.StixParameter()
                param.clone(ret)
                if pnode['children']:
                    raw = param.get('raw')
                    if raw:
                        pnode['counter'] = raw[0]
                        self.walk(pnode, param.children)
                    else:
                        STIX_LOGGER.warn(
                            'Children of {} are not decoded.'.format(
                                pnode['name']))
                parameter_list.append(param.parameter)

    def decode_parameter_for(self, node):
        """
        decode a parameter.
        The offset, offset bit and parameter name are described in 'node'
        """
        par = node['parameter']

        offset_bits = int(par['VPD_OFFSET'])
        width = int(par['PCF_WIDTH'])
        ptc = int(par['PCF_PTC'])
        pfc = int(par['PCF_PFC'])
        cal_ref = par['PCF_CURTX']
        name = node['name']

        if width % 8 != 0:
            if offset_bits < 0:
                self.current_offset_bit = self.last_data_width + offset_bits
            else:
                self.current_offset_bit += self.last_num_bits + offset_bits
            self.last_num_bits = width
        elif width % 8 == 0:
            self.current_offset_bit = 0
            self.last_offset = self.current_offset
            self.current_offset += width / 8
            self.last_num_bits = 0
            self.last_data_width = width

        offset = self.last_offset
        offset_bits = self.current_offset_bit
        calibration_enabled = False
        if name in PARMETERS_CALIBRATION_ENABLED:
            calibration_enabled = True

        #Not to convert raw to eng for variable length packet
        return self.decode_parameter(self.buffer, name, offset, offset_bits,
                                     width, ptc, pfc, cal_ref, 'TM',
                                     calibration_enabled)


class StixContextParser(StixParameterParser):
    '''Context file parser
       As Context file structure is not described in IDB,
       we define the structure in stix_context.py
       
    '''

    def __init__(self):
        super(StixContextParser, self).__init__()

    def parse(self, buf):
        #based on the FSW source code  ContextMgmt

        offset = 0
        #offset in units of bits
        parameters = []
        param_id = 0
        for name, width in stix_context.CONTEXT_PARAMETER_BIT_SIZE:
            #width also in units of bits
            offset_bytes = int(offset / 8)
            offset_bits = offset % 8
            children = []
            raw_values = None
            if name in stix_context.ASIC_REGISTERS:
                children = self.parse_asic_registers(buf, offset)
                raw_values = (len(children), )  #as a repeater
            else:
                raw_values = self.decode_buffer(buf, 'CONTEXT', offset_bytes,
                                                offset_bits, width)
            #if raw_values:
            param = stix_parameter.StixParameter(name, raw_values, '',
                                                 children)
            parameters.append(param.parameter)

            offset += width

            param_id += 1
        return parameters

    def parse_asic_registers(self, buf, offset):
        parameters = []
        for name, width in stix_context.CONTEXT_REGISTER_BIT_SIZE:
            offset_bytes = int(offset / 8)
            offset_bits = offset % 8
            raw_values = self.decode_buffer(buf, 'CONTEXT', offset_bytes,
                                            offset_bits, width)
            offset += width
            if raw_values:
                param = stix_parameter.StixParameter(
                    stix_context.CONTEXT_REGISTER_DESC[name], raw_values)
                parameters.append(param.parameter)
        return parameters


class StixTelecommandParser(StixParameterParser):
    """
        STIX telecommand packet parser
    """

    def __init__(self):
        super(StixTelecommandParser, self).__init__()
        self.length_min = 0
        self.nodes = []
        self.last_tc_name = ''
        self.tc_name = ''
        self.current_bit_offset = 0
        self.results_tree = []
        self.param_structure = []
        self.buffer = None



    def parse(self, name, buf):
        """
            To parse a telecommand
        """
        self.buffer = buf
        self.tc_name = name
        self.param_structure = []
        self.current_bit_offset = 0
        is_variable = STIX_IDB.is_variable_length_telecommand(name)
        self.param_structure = STIX_IDB.get_telecommand_structure(name)
        if is_variable:
            return self.parse_variable_telecommand()
        return self.parse_fixed_telecommand()



    def parse_fixed_telecommand(self):
        params = []
        for par in self.param_structure:
            result = self.parse_one(par, is_fixed = True, calibration_enabled = True)
            params.append(result)
        return int(self.current_bit_offset / 8), params, stix_global.OK

    def parse_one(self, par, is_fixed = True, calibration_enabled = True):
        cdf_type = par['CDF_ELTYPE']
        param_name = ''
        ptc = 0
        pfc = 0
        if cdf_type == 'A':
            #fixed area SCOS-2000 ICD page 63
            param_name = par['CDF_DESCR']
            ptc = 3  # works for STIX
            pfc = 4
        else:
            ptc = int(par['CPC_PTC'])
            pfc = int(par['CPC_PFC'])
            param_name = par['CDF_PNAME']
        cal_ref = par['CPC_PAFREF']
        width = int(par['CDF_ELLEN'])

        if is_fixed:
            offset = int(int(par['CDF_BIT']) / 8)
            offset_bits = int(par['CDF_BIT']) % 8
            self.current_bit_offset = int(par['CDF_BIT']) + width
        else:
            #CDF_ELLIEN is not respected  for variable telecommand
            offset = int(self.current_bit_offset / 8)
            offset_bits = int(self.current_bit_offset % 8)
            # need to be checked, may be wrong
            self.current_bit_offset += width

        parameter = self.decode_parameter(
            self.buffer,
            param_name,
            offset,
            offset_bits,
            width,
            ptc,
            pfc,
            cal_ref,
            'TC',
            calibration_enabled=calibration_enabled)
        return parameter

    def parse_variable_telecommand(self):
        self.current_bit_offset = 0
        self.length_min = 0
        self.results_tree = []
        self.nodes = []
        self.nodes.append(self.create_parse_node('top', counter=1))
        self.nodes[0]['children'] = []
        self.length_min = 0
        self.build_parse_tree()
        packet_length = len(self.buffer)
        if self.length_min > packet_length:
            return 0, None, stix_global.VARIABLE_PACKET_LENGTH_MISMATCH
        self.walk(self.nodes[0], self.results_tree)
        return int(
            self.current_bit_offset / 8), self.results_tree, stix_global.OK

    def create_parse_node(self, name, parameter=None, counter=0,
                          children=None):
        if children is None:
            children = []
        node = {
            'name': name,
            'counter': counter,
            'parameter': parameter,
            'children': children
        }
        return node

    def register_parameter(self, mother, idb_param):
        children = []
        name = idb_param['CDF_PNAME']
        node = self.create_parse_node(name, idb_param, 0, children)
        width = idb_param['CDF_ELLEN']
        if width % 8 == 0:
            self.length_min += width / 8
        mother['children'].append(node)
        return node

    def build_parse_tree(self):
        """
        To build a parameter parse tree
        """
        mother = self.nodes[0]
        repeater = [{
            'node': mother,
            'counter': stix_global.MAX_NUM_PARAMETERS
        }]
        for par in self.param_structure:
            if repeater:
                for e in reversed(repeater):
                    e['counter'] -= 1
                    if e['counter'] < 0:
                        repeater.pop()
            mother = repeater[-1]['node']
            node = self.register_parameter(mother, par)
            rpsize = par['CDF_GRPSIZE']
            if rpsize > 0:
                mother = node
                repeater.append({'node': node, 'counter': rpsize})

    def walk(self, mother, parameter_list):
        if not mother:
            return
        counter = mother['counter']
        for i in range(0, counter):
            for pnode in mother['children']:
                if not pnode or self.current_bit_offset > 8 * len(self.buffer):
                    return
                ret = self.parse_one(
                    pnode['parameter'], False, calibration_enabled=True)
                param = stix_parameter.StixParameter()
                param.clone(ret)
                if pnode['children']:
                    raw = param.get('raw')
                    if raw:
                        pnode['counter'] = raw[0]
                        self.walk(pnode, param.children)
                    else:
                        STIX_LOGGER.warn(
                            'Children of TC {} are not decoded.'.format(
                                pnode['name']))
                parameter_list.append(param.parameter)


class StixTCTMParser(StixParameterParser):
    def __init__(self):
        super(StixTCTMParser, self).__init__()
        self.vp_tm_parser = StixVariableTelemetryPacketParser()
        self.tc_parser = StixTelecommandParser()
        self.context_parser = StixContextParser()
        self.selected_services = []
        self.selected_spids = []
        self.store_binary = True
        #self.decoded_packets = []
        self.in_filename = ''
        self.in_filesize = 0

        self.num_tm = 0
        self.num_tc = 0

        self.num_tm_parsed = 0
        self.num_tc_parsed = 0

        self.num_bad_bytes = 0
        self.num_bad_headers = 0
        self.packet_reception_utc = ''
        self.total_length = 0
        self.num_filtered = 0
        self.report_progress_enabled = True

        self.store_packet_enabled = True
        self.packet_writer = None

    def set_store_packet_enabled(self, status):
        """
            store packets in a list
        """
        self.store_packet_enabled = status

    def reset_parser(self):
        self.num_tm = 0
        self.num_tc = 0
        self.num_tm_parsed = 0
        self.num_tc_parsed = 0
        self.num_bad_bytes = 0
        self.num_bad_headers = 0
        self.total_length = 0
        self.num_filtered = 0

    def set_report_progress_enabled(self, status):
        self.report_progress_enabled = status

    def set_packet_filter(self, selected_services=None, selected_spids=None):
        """ only decoded packets with the given services or spids
        """
        if selected_spids is None:
            selected_spids = []
        if selected_services is None:
            selected_services = []

        self.selected_services = selected_services
        self.selected_spids = selected_spids

    def set_store_binary_enabled(self, status):
        """
          store raw binary  in the output 
        """
        self.store_binary = status

    def get_summary(self):
        return {
            'total_length': self.total_length,
            'num_tc': self.num_tc,
            'num_tm': self.num_tm,
            'num_tc_parsed': self.num_tc_parsed,
            'num_tm_parsed': self.num_tm_parsed,
            'num_filtered': self.num_filtered,
            'num_bad_bytes': self.num_bad_bytes,
            'num_bad_headers': self.num_bad_headers
        }

    def parse_telemetry_header(self, packet):
        """ see STIX ICD-0812-ESC  (Page # 57) """
        if len(packet) < 16:
            STIX_LOGGER.warn("Packet length < 16. Packet ignored!")
            return stix_global.PACKET_TOO_SHORT, None
        if ord(packet[0:1]) not in stix_header.TM_HEADER_FIRST_BYTE:
            return stix_global.HEADER_FIRST_BYTE_INVALID, None
        header_raw = st.unpack('>HHHBBBBIH', packet[0:16])
        header = {}
        for h, s in zip(header_raw, stix_header.TELEMETRY_RAW_STRUCTURE):
            header.update(unpack_integer(h, s))
        status = self.check_header(header, 'tm')
        if status == stix_global.OK:
            header.update(
                {'segmentation': stix_header.PACKET_SEG[header['seg_flag']]})
            header['TMTC'] = 'TM'
            header.update(
                {'SCET': header['fine_time'] / 65536. + header['coarse_time']})
        return status, header

    def check_header(self, header, tmtc='tm'):
        # header validation
        constrains = None
        if tmtc == 'tm':
            constrains = stix_header.TELEMETRY_HEADER_CONSTRAINTS
        else:
            constrains = stix_header.TELECOMMAND_HEADER_CONSTRAINTS
        for name, lim in constrains.items():
            if header[name] not in lim:
                STIX_LOGGER.warn(
                    'Header {} value {} violates the range: {} '.format(
                        name, header[name], lim))
                return stix_global.HEADER_INVALID
        return stix_global.OK

    def parse_data_field_header(self, header, data, length):
        """ Decode the data field header
        """
        service_type = header['service_type']
        service_subtype = header['service_subtype']
        offset, width = STIX_IDB.get_packet_type_offset(
            service_type, service_subtype)
        # see solar orbit ICD Page 36
        ssid = -1
        if offset != -1:
            start = offset - 16  # 16bytes read already
            end = start + width / 8  # it can be : 0, 16,8
            bin_struct = '>B'
            if width == 16:
                bin_struct = '>H'
            raw = data[int(start):int(end)]
            if not raw:
                return stix_global.PACKET_TOO_SHORT
            res = st.unpack(bin_struct, raw)
            ssid = res[0]
        info = STIX_IDB.get_packet_type_info(service_type, service_subtype,
                                             ssid)
        if not info:
            return stix_global.NO_PID_INFO_IN_IDB
        header['descr'] = info['PID_DESCR']
        header['SPID'] = info['PID_SPID']
        header['TPSD'] = info['PID_TPSD']
        header['length'] = length
        header['SSID'] = ssid
        return stix_global.OK

    def parse_fixed_telemetry_packet(self, buf, spid):
        """ Extract parameters for a fixed data packet 
            see Solar orbit IDB.ICD section 3.3.2.5.1
        """
        if spid == 54331:
            #context file report parsing
            # not to use IDB
            return self.context_parser.parse(buf)
        parameters = []
        param_structures = STIX_IDB.get_fixed_packet_structure(spid)
        for par in param_structures:
            offset = int(par['PLF_OFFBY']) - 16
            offset_bits = int(par['PLF_OFFBI'])
            width = int(par['PCF_WIDTH'])
            ptc = int(par['PCF_PTC'])
            pfc = int(par['PCF_PFC'])
            name = par['PCF_NAME']
            cal_ref = par['PCF_CURTX']
            param = self.decode_parameter(buf, name, offset, offset_bits,
                                          width, ptc, pfc, cal_ref, 'TM', True)
            parameters.append(param)
        return parameters

    def parse_telecommand_header(self, buf, ipos):
        # see STIX ICD-0812-ESC  (Page 56)
        if buf[ipos] not in  stix_header.TC_HEADER_FIRST_BYTE:
            return stix_global.HEADER_FIRST_BYTE_INVALID, None
        try:
            header_raw = st.unpack('>HHHBBBB', buf[ipos:ipos+10])
        except Exception as e:
            STIX_LOGGER.error(str(e))
            return stix_global.HEADER_RAW_LENGTH_VALID, None, None
        header = {}
        for h, s in zip(header_raw, stix_header.TELECOMMAND_RAW_STRUCTURE):
            header.update(unpack_integer(h, s))
        status = self.check_header(header, 'tc')
        subtype = -1
        if (header['service_type'], header['service_subtype']) in [(237, 7),
                                                                   (236, 6)]:
            try:
                subtype = st.unpack('B', buf[ipos+10:ipos+11])[0]
                header['subtype'] = subtype
            except Exception as e:
                STIX_LOGGER.warn(
                    'Error occurred when parsing TC({},{}) due to {}'.format(
                        header['service_type'], header['service_subtype'],
                        str(e)))
        info = STIX_IDB.get_telecommand_info(header)
        if not info:
            return stix_global.HEADER_KEY_ERROR, header

        header['descr'] = info['CCF_DESCR']
        header['DESCR2'] = info['CCF_DESCR2']
        header['SPID'] = ''
        header['name'] = info['CCF_CNAME']
        header['TMTC'] = 'TC'
        header['SCET'] = 0
        if status == stix_global.OK:
            try:
                header['ACK_DESC'] = stix_header.ACK_MAPPING[header['ACK']]
            except KeyError:
                status = stix_global.HEADER_KEY_ERROR
        return status, header

    def parse_S20(self, parameters):
        """
          The detailed structure of S20 is not defined in IDB
        """
        try:
            param_hb=parameters[9]
            #platform data parser to be added
        except IndexError:
            return
        param_obj=stix_parameter.StixParameter()
        param_obj.clone(param_hb)
        raw_bin=b'\x04'+param_obj.raw[0]
        #add one byte to make it the same as  HK4
        hb_param_children= self.parse_fixed_telemetry_packet(
               raw_bin, 54103)
        #parse them as for HK4
        param_obj.set_children(hb_param_children)

    def parse_binary(self, buf, i=0):
        """
        Inputs:
            buffer, i.e., the input binary array
            i: starting offset
        Returns:
            decoded packets in python list if ret_packets=True
        """
        packets = []
        length = len(buf)
        self.total_length += length
        if i >= length:
            return []
        last = 0
        while i < length:
            packet = None
            if buf[i] in stix_header.TM_HEADER_FIRST_BYTE :
                status, i, header_raw = get_from_bytearray(buf, i, 16)
                if status == stix_global.EOF:
                    break
                header_status, header = self.parse_telemetry_header(header_raw)
                if header_status != stix_global.OK:
                    STIX_LOGGER.warn('Bad header at {}, code {} '.format(
                        i, header_status))
                    self.num_bad_headers += 1
                    continue

                self.num_tm += 1

                data_field_length = header['length'] - 9
                status, i, data_field_raw = get_from_bytearray(
                    buf, i, data_field_length)
                if status == stix_global.EOF:
                    STIX_LOGGER.warn(
                        "Incomplete packet, the last {} bytes  were not parsed"
                        .format(len(data_field_raw)))
                    break
                ret = self.parse_data_field_header(header, data_field_raw,
                                                   data_field_length)
                if ret != stix_global.OK:
                    STIX_LOGGER.warn(
                        'Missing information in the IDB to decoded the data starting at {} '
                        .format(i))
                    continue
                tpsd = header['TPSD']
                spid = header['SPID']
                if self.selected_services:
                    if header['service_type'] not in self.selected_services:
                        self.num_filtered += 1
                        continue
                if self.selected_spids:
                    if spid not in self.selected_spids:
                        self.num_filtered += 1
                        continue

                STIX_DECOMPRESSOR.initialize_decompressor(spid)

                parameters = None
                if tpsd == -1:
                    #it is a fixed length telemetry packet
                    parameters = self.parse_fixed_telemetry_packet(
                        data_field_raw, spid)
                else:
                    # variable length telemetry packet
                    num_read, parameters, status = self.vp_tm_parser.parse(
                        data_field_raw, spid)
                    if num_read != data_field_length:
                        STIX_LOGGER.warn(
                            ' Packet (SPID {}) data field size: {}B, actual read: {}B'
                            .format(spid, data_field_length, num_read))
                packet = {'header': header, 'parameters': parameters}
                self.num_tm_parsed += 1
                STIX_LOGGER.pprint(packet)
                if self.store_binary:
                    packet['bin'] = header_raw + data_field_raw

            elif buf[i] in stix_header.TC_HEADER_FIRST_BYTE:
                if len(buf)-i < 10:
                    STIX_LOGGER.warn(
                        "Incomplete packet. The last {} bytes  were not parsed"
                        .format(len(buf)))
                    break
                header_status, header = self.parse_telecommand_header(buf,i)
                i += 10
                #head length is 10 bytes
                if header_status != stix_global.OK:
                    self.num_bad_headers += 1
                    STIX_LOGGER.warn(
                        "Invalid telecommand header. ERROR code: {}, Current cursor at {} "
                        .format(header_status, i - 10))
                    continue
                self.num_tc += 1
                data_field_length = header['length'] + 1 - 4
                status, i, data_field_raw = get_from_bytearray(
                    buf, i, data_field_length)
                if status == stix_global.EOF:
                    break

                telecommand_name = header['name']
                num_read, parameters, status = self.tc_parser.parse(
                    telecommand_name, data_field_raw)
                if num_read != data_field_length - 2:  #the last two bytes is CRC
                    STIX_LOGGER.warn(
                        ' TC {} data field size: {}B, actual read: {}B'.format(
                            telecommand_name, data_field_length, num_read))


                if telecommand_name == 'ZIX20128' and parameters:
                    #S20 detailed structure  not defined in ICD
                    self.parse_S20(parameters)


                packet = {'header': header, 'parameters': parameters}
                self.num_tc_parsed += 1
                STIX_LOGGER.pprint(packet)
                if self.store_binary:
                    packet['bin'] = buf[i:i+10] + data_field_raw

            else:
                old_i = i
                STIX_LOGGER.warn('Unrecognized byte: {} at Pos {}'.format(hex(buf[i]), i))
                i = find_next_header(buf, i)
                if i == stix_global.EOF:
                    break
                self.num_bad_bytes += i - old_i
                STIX_LOGGER.warn(
                    'New header found at Pos {}, {} bytes ignored!'.format(
                        i, i - old_i))

            if packet:
                self.attach_timestamps(packet)
                if self.store_packet_enabled:
                    packets.append(packet)
                if self.packet_writer:
                    self.packet_writer.write_one(packet)

            if self.report_progress_enabled:
                current = int(100. * i / length)
                if current > last:
                    STIX_LOGGER.info('{}% processed.'.format(current))
                last = current

        return packets

    def parse_hex(self, raw_hex):
        hex_string = re.sub(r"\s+", "", raw_hex)
        try:
            raw = binascii.unhexlify(hex_string)
        except Exception as e:
            STIX_LOGGER.error(str(e))
            return []
        return self.parse_binary(raw)

    def parse_hex_file(self, filename):
        with open(filename, 'r') as f:
            raw_hex = f.read()
            return self.parse_hex(raw_hex)

    def parse_moc_ascii(self, filename):
        packets = []
        self.set_report_progress_enabled(False)
        with open(filename) as filein:
            STIX_LOGGER.info(
                'Reading packets from the file {}'.format(filename))
            idx = 0
            for line in filein:
                [self.packet_reception_utc, data_hex] = line.strip().split()
                data_binary = binascii.unhexlify(data_hex)
                packet = self.parse_binary(data_binary)
                if packet:
                    packets.extend(packet)
                if idx % 10 == 0:
                    STIX_LOGGER.info('{} packets processed.'.format(idx))
                idx += 1
        return packets

    def attach_timestamps(self, packet):
        #attach timestamp
        pkt_header = packet['header']
        if not self.packet_reception_utc:
            pkt_header[
                'unix_time'] = stix_datetime.convert_SCET_to_unixtimestamp(
                    pkt_header['SCET'])
            pkt_header['UTC'] = stix_datetime.convert_SCET_to_UTC(
                pkt_header['SCET'])
            return
        try:
            dt = dtparser.parse(self.packet_reception_utc)
            pkt_header['UTC'] = dt
            pkt_header['unix_time'] = dt.timestamp()
        except ValueError:
            #packet['header']['UTC'] = T0
            pkt_header['UTC'] = stix_datetime.convert_SCET_to_UTC(
                pkt_header['SCET'])

    def parse_moc_xml(self, in_filename):
        #parse a MOC xml file
        packets = []
        results = []
        self.set_report_progress_enabled(False)

        with open(in_filename) as filein:
            STIX_LOGGER.info('Parsing {}'.format(in_filename))
            doc = xmltodict.parse(filein.read())
            for e in doc['ns2:ResponsePart']['Response']['PktRawResponse'][
                    'PktRawResponseElement']:
                packet = {'id': e['@packetID'], 'raw': e['Packet']}
                packets.append(packet)
        num = len(packets)
        freq = 1
        if num > 100:
            freq = num / 100
        for i, packet in enumerate(packets):
            data_hex = packet['raw']
            data_binary = binascii.unhexlify(data_hex)
            data = data_binary[76:]
            result = self.parse_binary(data)
            if i % freq == 0:
                STIX_LOGGER.info("{:.0f}% processed.".format(100 * i / num))
            if not result:
                continue
            results.extend(result)
        return results

    def parse_file(self, in_filename, file_type=None, clear=True):
        packets = []
        if clear:
            self.reset_parser()

        if self.packet_writer:
            self.packet_writer.set_filename(in_filename)

        STIX_LOGGER.info('Processing file: {}'.format(in_filename))
        self.in_filename = in_filename
        self.in_filesize = os.path.getsize(in_filename)

        if not file_type:
            file_type = detect_filetype(in_filename)

        if file_type == 'bin':
            with open(in_filename, 'rb') as in_file:
                data = in_file.read()
                packets = self.parse_binary(data)
        elif file_type == 'ascii':
            packets = self.parse_moc_ascii(in_filename)
        elif file_type == 'xml':
            packets = self.parse_moc_xml(in_filename)
        elif file_type == 'hex':
            packets = self.parse_hex_file(in_filename)
        else:
            STIX_LOGGER.error(
                '{} has unknown input file type'.format(in_filename))
            return []

        summary = self.get_summary()
        STIX_LOGGER.print_summary(summary)
        if self.packet_writer:
            self.packet_writer.set_summary(summary)

        return packets

    def set_pickle_writer(self, out_filename, comment=''):
        self.packet_writer = stix_writer.StixPickleWriter(out_filename)
        self.packet_writer.register_run(self.in_filename, self.in_filename,
                                        comment)

    def set_MongoDB_writer(self,
                           server='localhost',
                           port=27017,
                           username='',
                           password='',
                           comment=''):
        self.packet_writer = stix_writer.StixMongoDBWriter(
            server, port, username, password)
        self.packet_writer.register_run(self.in_filename, self.in_filesize,
                                        comment)

    def done(self):
        if self.packet_writer:
            self.packet_writer.close()
