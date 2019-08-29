#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @date         : Feb. 11, 2019
# @description:
#               STIX telemetry raw data parser
# @TODO
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

_unsigned_format = ['B', '>H', 'BBB', '>I', 'BBBBB', '>IH']
_signed_format = ['b', '>h', 'bbb', '>i', 'bbbbb', '>ih']
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
                'Data length mismatch when unpacking parameter {}.  Expect: {} real: {}'
                .format(param_name, nbytes, len(raw_bin)))
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

    def convert_raw_to_eng(self, ref, param_type, raw, TMTC='TM'):
        """convert parameter raw values to engineer values"""
        if not raw:
            return ''
        if not ref:
            if param_type == 'T':  # timestamp
                return float(raw[0]) + float(raw[1]) / 65536.
            return ''
        if TMTC == 'TC':
            return _stix_idb.tcparam_interpret(ref, raw[0])

        raw_value = raw[0]
        prefix = re.split(r'\d+', ref)[0]
        if prefix in ['CIXTS', 'CAAT', 'CIXT']:
            # textual interpret
            rows = _stix_idb.textual_interpret(ref, raw_value)
            if rows:
                return rows[0][0]
            _stix_logger.warn('No textual calibration for {}'.format(ref))
            return ''
        elif prefix == 'CIXP':
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

    def parse_parameters(self, app_data, par, calibration=True, TMTC='TM'):
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
            eng_values = self.convert_raw_to_eng(par['cal_ref'], param_type,
                                                 raw_values, TMTC)
        return {
            'name': par['name'],
            'raw': raw_values,
            'desc': par['desc'],
            'value': eng_values
        }


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
                result_node = {
                    'name': node['name'],
                    'raw': result['raw'],
                    'desc': result['desc'],
                    'value': result['value'],
                    'children': []
                }
                if node['children']:
                    node['counter'] = result['raw'][0]
                    self.walk(node, result_node['children'])
                param.append(result_node)

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
        return self.parse_parameters(
            self.source_data, par, calibration, TMTC='TM')

class StixContextParser(StixParameterParser):
    '''Context file parser
    '''
    def __init__(self):
        pass
    def parse(self,buf):
        #based on the FSW source code  ContextMgmt
        #Tests needed!
        offset=0
        parameters=[]
        for name, width in stix_context._context_parameter_bit_size.items():
            offset_bytes=int(offset/8)
            offset_bits=offset%8
            children=[]
            raw_values=None
            if name in stix_context._asic_registers:
                children=self.parse_asic_registers(buf,offset)
                raw_values=(len(children),) #as a repeater
            else:
                raw_values=self.decode(buf, 'U',offset_bytes, offset_bits,width)
            if raw_values:
                parameters.append({'name':name,'desc':name,
                    'raw':raw_values, 'value':'', 'children':children})
            offset+= width

        return parameters
    def parse_asic_registers(self,buf,offset):
        parameters=[]
        for name, width in stix_context._context_register_bit_size.items():
            offset_bytes=int(offset/8)
            offset_bits=offset%8
            raw_values=self.decode(buf, 'U',offset_bytes, offset_bits,width)
            offset += width
            if raw_values:
                parameters.append({'name':name,
                    'desc':stix_context._context_register_desc[name],
                    'raw':raw_values, 'value':'','children':[]})
        return parameters


class StixTCTMParser(StixParameterParser):
    def __init__(self):
        self.vp_parser = StixVariablePacketParser()
        self.context_parser=StixContextParser()

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
            upstr = '>B'
            if width == 16:
                upstr = '>H'
            res = st.unpack(upstr, data[int(start):int(end)])
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
        if spid==54331:
            #it is a context report. 
            #The structure is not defined in IDB
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
            parameter = self.parse_parameters(buf, par, calibration, TMTC='TM')
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
                _stix_logger.info('variable TC skipped')
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
            parameter = self.parse_parameters(
                buf, par, calibration=True, TMTC='TC')
            params.append(parameter)
        return params

    def parse_file(self,
                   in_filename,
                   out_filename=None,
                   selected_spids=[],
                   file_type='binary',
                   comment=''):
        _stix_logger.info('Processing file: {}'.format(in_filename))
        packets = []
        file_size = os.path.getsize(in_filename)
        summary = dict()
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
                packets = self.parse_binary(data, 0, selected_spids, summary)

        elif file_type == 'ascii':
            packets = self.parse_moc_ascii(in_filename, selected_spids,
                                           summary)
        elif file_type == 'xml':
            packets = self.parse_moc_xml(in_filename, selected_spids, summary)
        else:
            _stix_logger.error(
                '{} has unknown input file type'.format(in_filename))
        _stix_logger.parser_summary(summary)
        if st_writer:
            st_writer.register_run(in_filename, file_size, comment)
            _stix_logger.info(
                'Writing parameters to {} ...'.format(out_filename))
            st_writer.write_all(packets)
            _stix_logger.info('Done.')
        else:
            return packets

    def parse_binary(self,
                     buf,
                     i=0,
                     selected_spids=[],
                     summary=None,
                     store_binary=False):

        length = len(buf)
        if i >= length:
            return None, None
        packets = []
        num_tc = 0
        num_tm = 0
        last = 0
        num_bad_bytes = 0
        num_bad_headers = 0
        while i < length:
            if buf[i] == 0x0D:
                # telemetry
                status, i, header_raw = get_from_bytearray(buf, i, 16)
                if status == stix_global._eof:
                    break
                header_status, header = self.parse_telemetry_header(header_raw)
                if header_status != stix_global._ok:
                    _stix_logger.warn('Bad header at {}, code {} '.format(
                        i, header_status))
                    num_bad_headers += 1
                    continue
                app_length = header['length'] - 9
                status, i, app_raw = get_from_bytearray(buf, i, app_length)
                if status == stix_global._eof:
                    break
                ret = self.decode_app_header(header, app_raw, app_length)
                if ret != stix_global._ok:
                    _stix_logger.warn(
                        'Lack of information in the IDB to decoded the packet at: {} '
                        .format(i))
                    continue
                tpsd = header['TPSD']
                spid = header['SPID']
                if selected_spids:
                    if spid not in selected_spids:
                        continue
                parameters = None
                num_tm += 1
                if tpsd == -1:
                    parameters = self.parse_fixed_packet(app_raw, spid)
                else:
                    self.vp_parser.init_telemetry_parser(app_raw, spid)
                    num_read, parameters, status = self.vp_parser.get_parameters(
                    )
                    if num_read != app_length:
                        _stix_logger.warn(
                            ' Packet length inconsistent!  SPID: {}, Actual: {}, IDB: {}'
                            .format(spid, num_read, app_length))
                packet = {'header': header, 'parameters': parameters}
                if store_binary:
                    packet['bin'] = header_raw + app_raw
                packets.append(packet)
            elif buf[i] == 0x1D:
                # telecommand
                num_tc += 1
                status, i, header_raw = get_from_bytearray(buf, i, 10)
                # header 10 bytes, the last two bytes are crc
                if status == stix_global._eof:
                    break
                header_status, header = self.parse_telecommand_header(
                    header_raw)

                if header_status != stix_global._ok:
                    num_bad_headers += 1
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
                if store_binary:
                    packet['bin'] = header_raw + app_raw
                packets.append(packet)
            else:
                old_i = i
                _stix_logger.warn('Unknown packet {} at {}'.format(buf[i], i))
                i = find_next_header(buf, i)
                if i == stix_global._eof:
                    break
                num_bad_bytes += i - old_i
                _stix_logger.warn(
                    'New header found at {}, {} bytes skipped!'.format(
                        i, i - old_i))
            current = int(100. * i / length)
            if current > last:
                _stix_logger.info('{}% processed!'.format(current))
            last = current

        if summary is not None:
            smr = {
                'TM': num_tm,
                'TC': num_tc,
                'size': length - i,
                'bad_bytes': num_bad_bytes,
                'bad_headers': num_bad_headers
            }
            if not summary:
                summary.update(smr)
            else:
                for k in summary.keys():
                    summary[k] += smr[k]
        return packets

    def parse_moc_ascii(self, filename, selected_spids=[], summary=None):
        packets = []
        with open(filename) as fd:
            _stix_logger.info(
                'Reading packets from the file {}'.format(filename))
            idx = 0
            for line in fd:
                [utc_timestamp, data_hex] = line.strip().split()
                data_binary = binascii.unhexlify(data_hex)
                packet = self.parse_binary(data_binary, 0, selected_spids,
                                           summary)
                if packet:
                    packet[0]['header']['UTC'] = utc_timestamp
                    packets.extend(packet)
                if idx % 10 == 0:
                    _stix_logger.info('{} packet have been read'.format(idx))
                idx += 1
        return packets

    def parse_hex(self, hex_text, summary=None):
        raw = binascii.unhexlify(hex_text)
        return self.parse_binary(raw, i=0, summary=summary)

    def parse_moc_xml(self, in_filename, selected_spids=[], summary=None):
        packets = []
        results = []
        try:
            fd = open(in_filename)
        except Exception as e:
            _stix_logger.error('Failed to open {}'.format(str(e)))
        else:
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
            result = self.parse_binary(data, 0, selected_spids, summary)
            if i % freq == 0:
                _stix_logger.info("{:.0f}% loaded".format(100 * i / num))
            if not result:
                continue
            results.extend(result)
        return results
