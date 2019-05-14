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
from core import stix_logger
from core import stix_writer

_unsigned_format = ['B', '>H', 'BBB', '>I', 'BBBBB', '>IH']
_signed_format = ['b', '>h', 'bbb', '>i', 'bbbbb', '>ih']
_stix_idb = idb._stix_idb
_stix_logger=stix_logger._stix_logger


def slice_bits(data, offset, length):
    return (data >> offset) & ((1 << length) - 1)
def unpack_integer(raw, structure):
    result = {}
    for name, bits in structure.items():
        result[name] = slice_bits(raw, bits[0], bits[1])
    return result

class StixParameterParser:
    def __init__(self):
        pass
 
    def decode(self, in_data, param_type, offset, offset_bit, length):
        nbytes = int(math.ceil((length+ offset_bit) / 8.))
        raw_bin= in_data[int(offset):int(offset + nbytes)]
        if nbytes != len(raw_bin):
            _stix_logger.error('Data too short to unpack:  Expect: {} real: {}'.format(nbytes, 
                len(raw_bin)))
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
            rows = _stix_idb.get_parameter_textual_interpret(pcf_curtx,raw_value)
            if rows:
                return rows[0][0]

            _stix_logger.warn('No textual calibration for {}'.format(pcf_curtx))
            return None
        elif prefix =='CIXP':
            rows = _stix_idb.get_calibration_curve(pcf_curtx)
            if rows:
                x_points = [float(row[0]) for row in rows]
                y_points = [float(row[1]) for row in rows]
                tck = interpolate.splrep(x_points, y_points)
                val=str(interpolate.splev(raw_value, tck))
                return val
            _stix_logger.warn('No calibration factors for {}'.format(pcf_curtx))
            return None

        elif prefix == 'NIX':
            # temperature
            #if pcf_curtx == 'NIX00101':
                #see SO-STIX-DS-30001_IDeF-X HD datasheet page 29
            #    pass
            _stix_logger.warn('{} not interpreted. '.format(pcf_curtx))
            return None
        elif prefix == 'CIX':
            rows=_stix_idb.get_calibration_polynomial(pcf_curtx)
            if rows:
                pol_coeff = ([float(x) for x in rows[0]])
                x_points = ([math.pow(raw_value, i) for i in range(0, 5)])
                sum_value=0
                for a, b in zip(pol_coeff,x_points):
                    sum_value+=a*b
                return sum_value
            _stix_logger.warn('No calibration factors for {}'.format(pcf_curtx))
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

        s2k_table = _stix_idb.get_s2k_parameter_types(ptc, pfc)
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

class StixTelemetryParser(StixParameterParser):
    def __init__(self):
        self.vp_parser=StixVariablePacketParser()

    def find_next_header(self,f):
        nbytes = 0
        bad_block = ''

        while True:
            x = f.read(1)
            if not x:
                break
            pos = f.tell()
            if nbytes<256:
                bad_block += ' ' + x.hex()
            nbytes += 1
            xval=st.unpack('>B',x)[0]
            if xval == 0x0D:
                f.seek(pos - 1)
                return True, nbytes, bad_block

        return False, nbytes, bad_block


    def parse_telemetry_header(self,packet):
        """ see STIX ICD-0812-ESC  (Page # 57) """

        if packet[0] != 0x0D:
            return stix_global._header_first_byte_invalid, None
        header_raw = st.unpack('>HHHBBBBIH', packet[0:16])
        header = {}
        for h, s in zip(header_raw, stix_header._telemetry_raw_structure):
            header.update(unpack_integer(h, s))
        status= self.check_header(header,'tm')
        if status == stix_global._ok:
            header.update({'segmentation': stix_header._packet_seg[header['seg_flag']]})
            header.update(
                {'time': header['fine_time'] / 65536. + header['coarse_time']})
        return status, header


    def check_header(self, header,tmtc='tm'):
        # header validate
        constrains=None
        if tmtc=='tm':
            constrains=stix_header._telemetry_header_constraints
        else:
            constrains=stix_header._telecommand_header_constraints
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
        offset, width = _stix_idb.get_packet_type_offset(service_type,
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
        info = _stix_idb.get_packet_type_info(service_type, service_subtype,
                                                  SSID)
        header['DESCR']=info['PID_DESCR']
        header['SPID']=info['PID_SPID']
        header['TPSD']=info['PID_TPSD']
        header['length']=length
        header['SSID']=SSID

    def parse_fixed_packet(self, buf, spid):
        param_struct= _stix_idb.get_fixed_packet_structure(spid)
        return self.get_fixed_packet_parameters(buf, param_struct, calibration=True)

    def get_fixed_packet_parameters(self, buf, param_struct,calibration):
        """ Extract parameters from a fixed data packet see Solar orbit IDB ICD section 3.3.2.5.1
        """
        params= []
        for par in param_struct:
            par['offset'] = int(par['PLF_OFFBY']) - 16
            par['offset_bit'] = int(par['PLF_OFFBI'])
            par['type'] = 'fixed'
            parameter = self.parse_telemetry_parameter(buf, par, calibration)
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

    def read_packet(self, in_file):
        start_pos = in_file.tell()
        header_raw= in_file.read(16)
        cur_pos = in_file.tell()
        num_read=len(header_raw)
        if not header_raw or num_read<16:
            return self.format_parse_result(stix_global._eof, num_read, None, header_raw)
        header_status, header = self.parse_telemetry_header(header_raw)

        if header_status != stix_global._ok:
            _stix_logger.warn('Bad header at {}, code {} '.format(in_file.tell(), header_status))

            found, num_skipped, bad_block = self.find_next_header(in_file)


            cur_pos = in_file.tell()
            num_read=cur_pos-start_pos
            _stix_logger.warn('''Unexpected block around {}, 
                            Number of bytes skipped: {}'''.format(
                in_file.tell(),num_skipped))
            if found:
                _stix_logger.info('New header at {}'.format(cur_pos))
                return self.format_parse_result(stix_global._next_packet, 
                        num_read, header_raw=header_raw)
            else:
                print('not found next header')

                return self.format_parse_result(stix_global._eof, 
                        num_read, header_raw=header_raw)

        app_length =header['length']-9


        if app_length <= 0:  # wrong packet length
            _stix_logger.warn('Source data length 0')
            return self.format_parse_result(stix_global._next_packet,
                    num_read, header_raw=header_raw)
        app_data = in_file.read(app_length)


        num_read=in_file.tell()-start_pos
        actual_length=len(app_data)
        if actual_length != app_length:
            _stix_logger.error("Incomplete data packet! pos:  {}, expect: {}, actual: {}, ".format(
            in_file.tell(), app_length, actual_length))
            return self.format_parse_result(stix_global._eof, num_read,header_raw=header_raw)

        self.decode_app_header(header, app_data, app_length)
        return self.format_parse_result(stix_global._ok, num_read, 
                header, header_raw, app_data)


    def parse_packet(self,buf,output_param_type='tree'):
        if len(buf)<=16:
            return {'status':stix_global._bad_packet, 
                    'header':None,
                    'parameters':None}
        header_raw=buf[0:16]
        header_status, header = self.parse_telemetry_header(header_raw)
        app_length = header['length']-9
        app_raw=buf[17:]
        self.decode_app_header(header, app_raw, app_length)
        tpsd = header['TPSD']
        spid= header['SPID']
        if tpsd == -1:
            parameters = self.parse_fixed_packet(app_raw, spid)
        else:
            self.vp_parser.parse(app_raw,spid, output_param_type)
            num_read, parameters, status = self.vp_parser.get_parameters()
        return {'status': stix_global._ok and status, 
                'header':header, 
                'parameters':parameters
                }


    def parse_one_packet_from_file(self,in_file,selected_spid=0, output_param_type='tree'):
        result= self.read_packet(in_file)
        status=result['status']
        header=result['header'] 
        header_raw=result['header_raw']
        app_raw=result['app_raw']
        num_read=result['num_read']

        parameters = None
        param_type=stix_global._unknown_packet_type
        param_desc=dict()
        if status!= stix_global._next_packet and status != stix_global._eof and header:
            spid = header['SPID']
            tpsd = header['TPSD']
            if selected_spid == 0 or spid == selected_spid:
                buffer_length = len(app_raw)
                if tpsd == -1:
                    parameters = self.parse_fixed_packet(
                        app_raw, spid)
                    param_type=stix_global._fix_length_packet_type
                else:
                    param_type=stix_global._variable_length_packet_type
                    self.vp_parser.parse(app_raw, spid, output_param_type)
                    app_num_read, parameters,status = self.vp_parser.get_parameters()
                    param_desc=None
                    if app_num_read!= buffer_length:
                        _stix_logger.warn("Variable packet length inconsistent! SPID: {}, Actual: {}, IDB: {}".format(
                            spid, buffer_length, app_num_read))
        return {'status':status, 
                    'header':header,
                    'parameters':parameters, 
                    'parameter_type':param_type,
                    'num_read':num_read
                    }


    def parse_file(self,in_filename, out_filename=None, selected_spid=0,
            pstruct='tree'):
        with open(in_filename, 'rb') as in_file:
            st_writer=None
            if  out_filename.endswith(('.pkl','.pklz')):
                st_writer = stix_writer.StixPickleWriter(out_filename)
            elif out_filename.endswith(('.db','.sqlite')):
                st_writer = stix_writer.StixSqliteWriter(out_filename)
            elif  'mongo' in out_filename:
                st_writer = stix_writer.StixMongoWriter()

            if st_writer:
                st_writer.register_run(in_filename)
            
            fix=0
            total=0
            var=0

            while True:
                result=self.parse_one_packet_from_file(in_file, selected_spid, pstruct)

                status=result['status']
                header=result['header']
                parameters=result['parameters']
                param_type=result['parameter_type']
                bytes_read=result['num_read']
                total+=1
                
                if status == stix_global._next_packet:
                    continue
                if status == stix_global._eof:
                    break

                if param_type ==stix_global._fix_length_packet_type:
                    fix+=1
                elif param_type == stix_global._variable_length_packet_type: 
                    var+=1
                if status and parameters and st_writer:
                    st_writer.write(header,parameters)
            if st_writer:
                st_writer.done()
            _stix_logger.info('{} packets found in the file: {}'.format(total,in_filename))
            _stix_logger.info('{} ({} fixed and {} variable) packets processed.'.format(
                    fix+var,fix,var))
            _stix_logger.info('Writing parameters to file {} ...'.format(out_filename))
            _stix_logger.info('Done.')



class StixVariablePacketParser(StixParameterParser):
    """
    Variable length packet parser
    """
    def __init__(self):
        pass
    def debug_enabled(self):
        self.debug=True
    def parse(self,data, spid, output_type='tree'):
        """
        """
        self.root = None
        self.source_data = data
        self.spid = spid
        self.nodes = []
        self.results_tree = []
        self.num_nodes = 0
        self.nodes.append(
            self.create_node('top', 0, 0, 0, stix_global._max_parameters, None,
                             1))
        self.current_offset = 0
        self.last_offset = 0
        self.current_offset_bit = 0
        self.length_min = 0
        self.output_type =output_type
        self.results_dict={}
        self.debug=False
        #self.parameter_desc={}

    #def start(self):
        self.nodes[0]['child']=[]
        self.results_tree[:]=[]
        self.results_dict.clear()
        #self.parameter_desc.clear()
        #self.current_offset = 0
        #self.last_offset = 0
        #self.current_offset_bit = 0
        #self.length_min = 0
        

    def get_parameters(self):
        self.build_tree()
        packet_length = len(self.source_data)
        if self.length_min > packet_length:
            return 0, None, stix_global._variable_packet_length_mismatch 
        if self.output_type=='tree':
            self.walk_to_tree(self.nodes[0], self.results_tree)
            return self.current_offset, self.results_tree, stix_global._ok
        else:
            self.walk_to_array(self.nodes[0])
            return self.current_offset, self.results_dict,stix_global._ok


    def create_node(self,
                    name,
                    position,
                    width,
                    offset_bit,
                    repeat_size,
                    parameter,
                    counter=0,
                    desc='',
                    child=[]):
        node = {
            'name': name,
            'offset_bit': offset_bit,
            'position': position,
            'repeat_size': repeat_size,
            'counter': counter,
            #'width': width,
            'parameter': parameter,
            'ID': self.num_nodes,
            'child': child,
            #'desc': desc
        }
        self.num_nodes += 1
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
                           child=[]):
        node = self.create_node(name, position, width, offset_bit, repeat_size,
                                parameter, counter, desc, child)
        if width % 8 == 0:
            self.length_min += width / 8
        mother['child'].append(node)
        return node
    def build_tree(self):
        """
        To build a parameter tree 
        """
        #self.start()
        self.structures = _stix_idb.get_variable_packet_structure(self.spid)

        mother = self.nodes[0]
        repeater = [{'node': mother, 'counter': stix_global._max_parameters}]
        #counter:  number of repeated times

        for par in self.structures:
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




    def pprint_par(self,st):
        if self.debug:
            print(('%s %s  %s %s %s %s %s %s\n')%(str(st['VPD_POS']), st['VPD_NAME'], st['VPD_GRPSIZE'], 
                st['VPD_OFFSET'],  str(st['PCF_WIDTH']),str(st['offset']),str(st['offset_bit']), st['PCF_DESCR']))

    def pprint_structure(self,structures):
        if self.debug:
            pprint.pprint(structures)
            for st in structures:
                print(('%s %s  %s %s %s %s\n')%(str(st['VPD_POS']), st['VPD_NAME'], st['VPD_GRPSIZE'], 
                    st['VPD_OFFSET'],  str(st['PCF_WIDTH']), st['PCF_DESCR']))

    def walk_to_array(self, mother):
        """
        Parameter tree traversal
        """
        if not mother:
            return
        result_node = None
        counter = mother['counter']
        parameter_values={}
        for i in range(0, counter):
            for node in mother['child']:
                if not node or self.current_offset > len(self.source_data):
                    return None
                result = self.parse_parameter(node)
                value=result['raw'][0]
                name=node['name']
                if name in self.results_dict:
                    self.results_dict[name].append(value)
                else:
                    self.results_dict[name]=[value]
                if node['child']:
                    node['counter'] = value
                    self.walk_to_array(node)

    def walk_to_tree(self, mother, para):
        if not mother:
            return
        result_node = None
        counter = mother['counter']
        for i in range(0, counter):
            for node in mother['child']:
                if not node or self.current_offset > len(self.source_data):
                    return
                result = self.parse_parameter(node)
                result_node = {
                    'name': node['name'],
                    'raw': result['raw'],
                    'value': result['value'],
                    #'eng_value_type': result['eng_value_type'],
                    #'descr': result['descr'],
                    'child': []
                }
                if node['child']:
                    node['counter'] = result['raw'][0]
                    self.walk_to_tree(node, result_node['child'])
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

        #print('###{},{}, {},{}'.format(par['PCF_NAME'],self.last_offset,self.current_offset_bit,width))
        calibration=False
        if self.output_type == 'tree':
            calibration=True
            #not to interpret a raw value to physical value
        return self.parse_telemetry_parameter(
            self.source_data, par, calibration)

