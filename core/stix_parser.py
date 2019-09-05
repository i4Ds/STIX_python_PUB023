#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @date         : Feb. 11, 2019
# @description:
#               STIX telemetry raw data parser
# @TODO
#              checks for CRC for each packet
#              parse variable length TC

import binascii
import math
import os
import re
import struct as st
import xmltodict
from scipy import interpolate

from core import header as stix_header
from core import idb
from core import stix_global
from core import stix_logger
from core import stix_writer
from core import stix_context

_context_format = ['B', '>H', 'BBB', '>I']
_unsigned_format = ['B', '>H', 'BBB', '>I', 'BBBBB', '>IH']
_signed_format = ['b', '>h', 'bbb', '>i', 'bbbbb', '>ih']
_parameter_default_type = 'tuple'

#binary structure used to unpack binaryarray
_stix_idb = idb._stix_idb
_stix_logger = stix_logger._stix_logger


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
        if x == 0x0D or x == 0x1D:
            return i
        else:
            i += 1
    return stix_global._eof


class StixParameterNode:
    """ define decoded parameter structure """

    def __init__(self,
                 name='',
                 raw='',
                 eng='',
                 children=None,
                 node_type=_parameter_default_type):
        #node_type can be tuple or dict
        self._name = name
        self._raw = raw
        self._eng = eng
        self._children = []
        if children:
            self._children = children
        self._node_type = node_type

    def set_node_type(self, node_type):
        """can be dictionary or tuple"""
        self._node_type = node_type

    def get_node_type(self):
        return self._node_type

    def get(self, item=None):
        if item == 'name':
            return self._name
        elif item == 'raw':
            return self._raw
        elif item == 'eng':
            return self._eng
        elif item == 'children':
            return self._children
        elif item == 'desc':
            return _stix_idb.get_PCF_description(param_name)
        else:
            return self.get_node(self._node_type)

    def get_node(self, node_type):
        if node_type == 'tuple':
            return (self._name, self._raw, self._eng, self._children)
        else:
            return {
                'name': self._name,
                'raw': self._raw,
                'eng': self._eng,
                'children': self._children
            }

    def isa(self, name):
        if self._name == name:
            return True
        else:
            return False

    def from_node(self, node):
        if type(node) is dict:
            self._name = node['name']
            self._raw = node['raw']
            self._eng = node['eng']
            self._children = node['children']
        elif type(node) is tuple:
            self._name = node[0]
            self._raw = node[1]
            self._eng = node[2]
            self._children = node[3]

    def to_dict(self, node=None):
        self.from_node(node)
        return get_node('dict')

    def to_tuple(self, node=None):
        self.from_node(node)
        return get_node('tuple')

    def set_children(self, children=[]):
        self._children[:] = children

    @property
    def name(self):
        return self._name

    @property
    def raw(self):
        return self._raw

    @property
    def eng(self):
        return self._eng

    @property
    def children(self):
        return self._children

    @property
    def desc(self):
        if self._name:
            return _stix_idb.get_PCF_description(self._name)
        else:
            return ''

    @property
    def node(self):
        return self.get_node(self._node_type)


class StixParameterParser:
    def __init__(self):
        pass

    def decode(self,
               in_data,
               param_type,
               offset,
               offset_bits,
               length,
               param_name=''):
        """
        decode a parameter
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
            _stix_logger.error(
                'Parameter {} length mismatch.  Expect: {} real: {}'.format(
                    param_name, nbytes, len(raw_bin)))
            return None
        bin_struct = str(nbytes) + 's'
        if param_type == 'U' and nbytes <= 6:
            bin_struct = _unsigned_format[nbytes - 1]
        elif param_type == 'I' and nbytes <= 6:
            bin_struct = _signed_format[nbytes - 1]
        elif param_type == 'T':
            bin_struct = '>IH'
        elif param_type == 'CONTEXT' and nbytes <= 4:
            bin_struct = _context_format[nbytes - 1]
        #elif param_type == 'O':
        #    bin_struct = str(nbytes) + 's'
        results = ()
        raw = st.unpack(bin_struct, raw_bin)
        if bin_struct == 'BBB':  # 24-bit integer
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

    def convert_raw_to_eng(self, param_name, ref, param_type, raw, TMTC='TM'):
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
        if TMTC == 'TC':
            return _stix_idb.tcparam_interpret(ref, raw[0])
        elif param_name == 'NIX00101':
            #conversion based on the equation in SIRIUS source code
            return (raw_value * 1.1 * 3.0 / 4095 - 1.281) * 213.17
        elif param_name == 'NIX00102':
            #temperature std. deviations
            return (raw_value * 1.1 * 3.0 / 4095) * 213.17
        elif not ref:
            if param_type == 'T':  # timestamp
                #coarse time + fine time/2^16
                return float(raw[0]) + float(raw[1]) / 65536.
            return ''

        #other parameters
        prefix = re.split(r'\d+', ref)[0]
        if prefix in ['CIXTS', 'CAAT', 'CIXT']:
            # textual interpret
            rows = _stix_idb.textual_interpret(ref, raw_value)
            if rows:
                return rows[0][0]
            _stix_logger.warn('No textual calibration for {}'.format(ref))
            return ''
        elif prefix == 'CIXP':
            #calibration
            rows = _stix_idb.get_calibration_curve(ref)
            if rows:
                x_points = [float(row[0]) for row in rows]
                y_points = [float(row[1]) for row in rows]
                tck = interpolate.splrep(x_points, y_points)
                val = str(interpolate.splev(raw_value, tck))
                return val
            _stix_logger.warn('No calibration factors for {}'.format(ref))
            return ''
        elif prefix == 'NIX':
            _stix_logger.warn('{} not interpreted. '.format(ref))
            return ''
        elif prefix == 'CIX':
            rows = _stix_idb.get_calibration_polynomial(ref)
            if rows:
                pol_coeff = ([float(x) for x in rows[0]])
                x_points = ([math.pow(raw_value, i) for i in range(0, 5)])
                sum_value = 0
                for coeff, xval in zip(pol_coeff, x_points):
                    sum_value += coeff * xval
                return sum_value
            _stix_logger.warn('No calibration factors for {}'.format(ref))
            return ''
        return ''

    def parse_one_parameter(self, app_data, par, calibration=True, TMTC='TM'):
        s2k_LUT = _stix_idb.get_s2k_parameter_types(par['ptc'], par['pfc'])
        param_type = s2k_LUT['S2K_TYPE']
        raw_values = self.decode(
            app_data,
            param_type,
            int(par['offset']),
            int(par['offset_bits']),
            par['width'],
            param_name=par['name'])
        eng_values = ''
        if not calibration:
            eng_values = ''
        else:
            eng_values = self.convert_raw_to_eng(par['name'], par['cal_ref'],
                                                 param_type, raw_values, TMTC)
        return StixParameterNode(par['name'], raw_values, eng_values).node


class StixVariablePacketParser(StixParameterParser):
    """
    Variable length packet parser
    """

    def __init__(self):
        self.debug = False
        self.last_spid = -1
        self.last_num_bits = 0

    def debug_enabled(self):
        self.debug = True

    def init_nodes(self):
        self.nodes = []
        self.nodes.append(
            self.create_node('top', 0, 0, 0, stix_global._max_parameters, None,
                             1))
        self.nodes[0]['children'] = []
        self.length_min = 0

    def init_telemetry_parser(self, data, spid):
        self.last_num_bits = 0
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
        self.last_spid = spid

    def get_parameters(self):
        packet_length = len(self.source_data)
        if self.length_min > packet_length:
            return 0, None, stix_global._variable_packet_length_mismatch
        self.walk(self.nodes[0], self.results_tree)
        return self.current_offset, self.results_tree, stix_global._ok

    def create_node(self,
                    name,
                    position,
                    width,
                    offset_bits,
                    repeat_size,
                    parameter,
                    counter=0,
                    desc='',
                    children=[]):
        node = {
            'name': name,
            'offset_bits': offset_bits,
            'position': position,
            'repeat_size': repeat_size,
            'counter': counter,
            'parameter': parameter,
            'children': children
        }
        return node

    def register_parameter(self,
                           mother,
                           name,
                           position,
                           width,
                           offset_bits,
                           repeat_size,
                           parameter,
                           counter,
                           desc='',
                           children=[]):
        node = self.create_node(name, position, width, offset_bits,
                                repeat_size, parameter, counter, desc,
                                children)
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
        for par in structures:
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

    def walk(self, mother, param):
        if not mother:
            return
        result_node = None
        counter = mother['counter']
        for i in range(0, counter):
            for node in mother['children']:
                if not node or self.current_offset > len(self.source_data):
                    return
                result = self.parse_parameter(node)
                result_node = StixParameterNode()
                result_node.from_node(result)
                if node['children']:
                    raw = result_node.get('raw')
                    if raw:
                        node['counter'] = raw[0]
                        self.walk(node, result_node.children)
                    else:
                        _stix_logger.warn(
                            'A repeater {} is not decoded.'.format(
                                node['name']))
                param.append(result_node.node)

    def parse_parameter(self, node):
        """
        decode a parameter.
        The offset, offset bit and parameter name are described in 'node'
        """
        par = node['parameter']
        width = int(par['PCF_WIDTH'])
        vpd_offset = int(par['VPD_OFFSET'])
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
        par['offset_bits'] = self.current_offset_bit
        par['width'] = int(par['PCF_WIDTH'])
        par['ptc'] = int(par['PCF_PTC'])
        par['pfc'] = int(par['PCF_PFC'])
        par['name'] = par['PCF_NAME']
        par['desc'] = par['PCF_DESCR']
        par['cal_ref'] = par['PCF_CURTX']
        calibration = False
        calibration = True
        return self.parse_one_parameter(
            self.source_data, par, calibration, TMTC='TM')


class StixContextParser(StixParameterParser):
    '''Context file parser
    '''

    def __init__(self):
        pass

    def parse(self, buf):
        #based on the FSW source code  ContextMgmt

        offset = 0
        parameters = []
        param_id = 0
        for name, width in stix_context._context_parameter_bit_size.items():
            offset_bytes = int(offset / 8)
            offset_bits = offset % 8
            children = []
            raw_values = None
            if name in stix_context._asic_registers:
                children = self.parse_asic_registers(buf, offset)
                raw_values = (len(children), )  #as a repeater
            else:
                raw_values = self.decode(buf, 'CONTEXT', offset_bytes,
                                         offset_bits, width)
            if raw_values:
                param = StixParameterNode(name, raw_values, '', children)
                parameters.append(param.node)
            offset += width
            param_id += 1
        return parameters

    def parse_asic_registers(self, buf, offset):
        parameters = []
        for name, width in stix_context._context_register_bit_size.items():
            offset_bytes = int(offset / 8)
            offset_bits = offset % 8
            raw_values = self.decode(buf, 'CONTEXT', offset_bytes, offset_bits,
                                     width)
            offset += width
            if raw_values:
                param = StixParameterNode(
                    stix_context._context_register_desc[name], raw_values)
                parameters.append(param.node)
        return parameters


class StixTCTMParser(StixParameterParser):
    def __init__(self):
        self.vp_parser = StixVariablePacketParser()
        self.context_parser = StixContextParser()

        self.selected_services = []
        self.selected_spids = []
        self.store_binary = True

        self.num_tm = 0
        self.num_tc = 0
        self.num_bad_bytes = 0
        self.num_bad_headers = 0
        self.total_length = 0
        self.num_filtered = 0
        self.report_progress_enabled = True
        #counters
    def set_report_progress_enabled(self, status):
        self.report_progress_enabled = status

    def set_packet_filter(self, selected_services=[], selected_spids=[]):
        """ only decoded packets with the given services or spids
        """
        self.selected_services = selected_services
        self.selected_spids = selected_spids

    def set_store_binary_enabled(self, status):
        """
          store raw binary  in the outputs 
        """
        self.store_binary = status

    def get_summary(self):
        return {
            'total_length': self.total_length,
            'num_tc': self.num_tc,
            'num_tm': self.num_tm,
            'num_filtered': self.num_filtered,
            'num_bad_bytes': self.num_bad_bytes,
            'num_bad_headers': self.num_bad_headers
        }

    def parse_telemetry_header(self, packet):
        """ see STIX ICD-0812-ESC  (Page # 57) """
        if len(packet) < 16:
            _stix_logger.warn("Packet length < 16. Packet ignored!")
            return stix_global._packet_too_short, None
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
            bin_struct = '>B'
            if width == 16:
                bin_struct = '>H'
            res = st.unpack(bin_struct, data[int(start):int(end)])
            SSID = res[0]
        info = _stix_idb.get_packet_type_info(service_type, service_subtype,
                                              SSID)
        if not info:
            return stix_global._no_PID_info_in_IDB
        header['DESCR'] = info['PID_DESCR']
        header['SPID'] = info['PID_SPID']
        header['TPSD'] = info['PID_TPSD']
        header['length'] = length
        header['SSID'] = SSID
        return stix_global._ok

    def parse_fixed_packet(self, buf, spid):
        if spid == 54331:
            #context file report.
            return self.context_parser.parse(buf)
        param_struct = _stix_idb.get_fixed_packet_structure(spid)
        return self.get_fixed_packet_parameters(
            buf, param_struct, calibration=True)

    def get_fixed_packet_parameters(self, buf, param_struct, calibration):
        """ Extract parameters from a fixed data packet see Solar orbit IDB ICD section 3.3.2.5.1
        """
        params = []
        for par in param_struct:
            par['offset'] = int(par['PLF_OFFBY']) - 16
            par['offset_bits'] = int(par['PLF_OFFBI'])
            par['type'] = 'fixed'
            par['width'] = int(par['PCF_WIDTH'])
            par['ptc'] = int(par['PCF_PTC'])
            par['pfc'] = int(par['PCF_PFC'])
            par['name'] = par['PCF_NAME']
            par['desc'] = par['PCF_DESCR']
            par['cal_ref'] = par['PCF_CURTX']
            parameter = self.parse_one_parameter(
                buf, par, calibration, TMTC='TM')
            params.append(parameter)
        return params

    def parse_telecommand_header(self, packet):
        # see STIX ICD-0812-ESC  (Page 56)
        if packet[0] != 0x1D:
            return stix_global._header_first_byte_invalid, None
        try:
            header_raw = st.unpack('>HHHBBBB', packet[0:10])
        except Exception as e:
            _stix_logger.error(str(e))
            return stix_global._header_raw_length_valid, None
        header = {}
        for h, s in zip(header_raw, stix_header._telecommand_raw_structure):
            header.update(unpack_integer(h, s))
        status = self.check_header(header, 'tc')
        info = _stix_idb.get_telecommand_info(header['service_type'],
                                              header['service_subtype'],
                                              header['source_id'])
        if not info:
            return stix_global._header_key_error, header

        header['DESCR'] = info['CCF_DESCR']
        header['DESCR2'] = info['CCF_DESCR2']
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

    def get_telecommand_parameters(self, header, buf):
        name = header['name']
        param_structure = _stix_idb.get_telecommand_structure(name)
        params = []
        for par in param_structure:
            if int(par['CDF_GRPSIZE']) > 0:
                _stix_logger.info('variable length TC skipped')
                break
            par['offset'] = int(int(par['CDF_BIT']) / 8)
            par['offset_bits'] = int(par['CDF_BIT']) % 8
            par['type'] = 'fixed'
            par['width'] = int(par['CDF_ELLEN'])
            par['ptc'] = int(par['CPC_PTC'])
            par['pfc'] = int(par['CPC_PFC'])
            par['name'] = par['CDF_PNAME']
            par['desc'] = par['CPC_DESCR']
            par['cal_ref'] = par['CPC_PAFREF']
            parameter = self.parse_one_parameter(
                buf, par, calibration=True, TMTC='TC')
            params.append(parameter)
        return params

    def parse_file(self,
                   in_filename,
                   out_filename=None,
                   file_type='binary',
                   comment=''):
        _stix_logger.info('Processing file: {}'.format(in_filename))

        packets = []
        file_size = os.path.getsize(in_filename)
        st_writer = None
        if out_filename.endswith(('.pkl', '.pklz')):
            st_writer = stix_writer.StixPickleWriter(out_filename)
        elif 'mongo' in out_filename:
            st_writer = stix_writer.StixMongoWriter()
        else:
            _stix_logger.warn('Decoded packet will not stored.')

        if file_type == 'binary':
            with open(in_filename, 'rb') as in_file:
                data = in_file.read()
                _stix_logger.info("File size:{} kB ".format(len(data) / 1024))
                packets = self.parse_binary(data, 0)
        elif file_type == 'ascii':
            packets = self.parse_moc_ascii(in_filename)
        elif file_type == 'xml':
            packets = self.parse_moc_xml(in_filename)
        else:
            _stix_logger.error(
                '{} has unknown input file type'.format(in_filename))

        _stix_logger.print_summary(self.get_summary())

        if st_writer:
            st_writer.register_run(in_filename, file_size, comment)
            _stix_logger.info(
                'Writing parameters to {} ...'.format(out_filename))
            st_writer.write_all(packets)
            _stix_logger.info('Done.')
        else:
            return packets

    def parse_binary(self, buf, i=0):
        """
        Inputs:
            buffer, i.e., the input binary array
            i: starting offset
        Returns:
            decoded packets in python list
        """

        length = len(buf)
        self.total_length += length
        if i >= length:
            return []

        packets = []
        last = 0
        while i < length:
            if buf[i] == 0x0D:
                status, i, header_raw = get_from_bytearray(buf, i, 16)
                if status == stix_global._eof:
                    break
                header_status, header = self.parse_telemetry_header(header_raw)
                if header_status != stix_global._ok:
                    _stix_logger.warn('Bad header at {}, code {} '.format(
                        i, header_status))
                    self.num_bad_headers += 1
                    continue
                app_length = header['length'] - 9
                status, i, app_raw = get_from_bytearray(buf, i, app_length)
                if status == stix_global._eof:
                    break
                ret = self.decode_app_header(header, app_raw, app_length)
                if ret != stix_global._ok:
                    _stix_logger.warn(
                        'Missing information in the IDB to decoded the data starting at {} '
                        .format(i))
                    continue
                tpsd = header['TPSD']
                spid = header['SPID']
                #packet filter
                if self.selected_services:
                    if header['service_type'] not in self.selected_services:
                        self.num_filtered += 1
                        continue
                if self.selected_spids:
                    if spid not in self.selected_spids:
                        self.num_filtered += 1
                        continue
                self.num_tm += 1
                parameters = None
                if tpsd == -1:
                    parameters = self.parse_fixed_packet(app_raw, spid)
                else:
                    self.vp_parser.init_telemetry_parser(app_raw, spid)
                    num_read, parameters, status = self.vp_parser.get_parameters(
                    )
                    if num_read != app_length:
                        _stix_logger.warn(
                            ' Packet (SPID {}) length mismatch. Actual length: {}, IDB: {}'
                            .format(spid, num_read, app_length))
                packet = {'header': header, 'parameters': parameters}
                if self.store_binary:
                    packet['bin'] = header_raw + app_raw
                packets.append(packet)
            elif buf[i] == 0x1D:
                # telecommand
                self.num_tc += 1
                status, i, header_raw = get_from_bytearray(buf, i, 10)
                # header 10 bytes, the last two bytes are crc
                if status == stix_global._eof:
                    break
                header_status, header = self.parse_telecommand_header(
                    header_raw)
                if header_status != stix_global._ok:
                    self.num_bad_headers += 1
                    _stix_logger.warn(
                        "Invalid telecommand header. Cursor at {} ".format(i -
                                                                           12))
                    continue
                app_length = header['length'] + 1 - 4
                status, i, app_raw = get_from_bytearray(buf, i, app_length)
                if status == stix_global._eof:
                    break
                parameters = self.get_telecommand_parameters(header, app_raw)
                packet = {'header': header, 'parameters': parameters}
                if self.store_binary:
                    packet['bin'] = header_raw + app_raw
                packets.append(packet)
            else:
                old_i = i
                _stix_logger.warn('Unknown packet {} at {}'.format(buf[i], i))
                i = find_next_header(buf, i)
                if i == stix_global._eof:
                    break
                self.num_bad_bytes += i - old_i
                _stix_logger.warn(
                    'New header found at {}, {} bytes skipped!'.format(
                        i, i - old_i))

            if self.report_progress_enabled:
                current = int(100. * i / length)
                if current > last:
                    _stix_logger.info('{}% processed!'.format(current))
                last = current

        return packets

    def parse_moc_ascii(self, filename):
        packets = []
        self.set_report_progress_enabled(False)
        with open(filename) as fd:
            _stix_logger.info(
                'Reading packets from the file {}'.format(filename))
            idx = 0
            for line in fd:
                [utc_timestamp, data_hex] = line.strip().split()
                data_binary = binascii.unhexlify(data_hex)
                packet = self.parse_binary(data_binary, 0)
                if packet:
                    packet[0]['header']['UTC'] = utc_timestamp
                    packets.extend(packet)
                if idx % 10 == 0:
                    _stix_logger.info('{} packet have been read'.format(idx))
                idx += 1
        return packets

    def parse_hex(self, hex_string):
        raw = binascii.unhexlify(hex_string)
        return self.parse_binary(raw, i=0)

    def parse_moc_xml(self, in_filename):
        packets = []
        results = []
        self.set_report_progress_enabled(False)

        with open(in_filename) as fd:
            _stix_logger.info('Parsing {}'.format(in_filename))
            doc = xmltodict.parse(fd.read())
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
            result = self.parse_binary(data, 0)
            if i % freq == 0:
                _stix_logger.info("{:.0f}% loaded".format(100 * i / num))
            if not result:
                continue
            results.extend(result)
        return results
