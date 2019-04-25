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
from stix_io import stix_writer
from stix_io import stix_logger
LOGGER = stix_logger.LOGGER
STIX_IDB = idb.STIX_IDB

UNSIGNED_UNPACK_STRING = ['B', '>H', 'BBB', '>I', 'BBBBB', '>IH']
SIGNED_UNPACK_STRING = ['b', '>h', 'bbb', '>i', 'bbbbb', '>ih']


def slice_bits(data, offset, length):
    """
     get the value of the bits between [offset, offset+length]
    """
    return (data >> offset) & ((1 << length) - 1)


def unpack_integer(raw, structure):
    """
    unpack a 16 bit or 32 bit  integer using the defined structure
    Args:
        structure:
        Structure is a dictionary describing the structure of the integer
    Returns:
        a dictionary 
    """
    result = {}
    for name, bits in structure.items():
        result[name] = slice_bits(raw, bits[0], bits[1])
    return result


def unpack_parameter(in_data, parameter_type, offset, offset_bit, data_length):
    """
    unpack a 'fixed'  parameter from a binary stream
    Args:
        in_data         : binary data
        offset          : offset 
        parameter_type  : parameter type known from the s2k table
        data_length     : data length in units of bits
    Results:
        unpacked data
    """
    data_type = ''
    nbytes = int(math.ceil((data_length + offset_bit) / 8.))
    # bytes to be read
    if parameter_type == 'U':
        if nbytes <= 6:
            data_type = UNSIGNED_UNPACK_STRING[nbytes - 1]
        else:
            data_type = str(nbytes) + 's'
    elif parameter_type == 'I':
        if nbytes <= 6:
            data_type = SIGNED_UNPACK_STRING[nbytes - 1]
        else:
            data_type = str(nbytes) + 's'
    elif parameter_type == 'T':
        data_type = '>IH'
    elif parameter_type == 'O':
        data_type = str(nbytes) + 's'
    else:
        data_type = str(nbytes) + 's'
    
    results = ()
    raw_data = in_data[offset:offset + nbytes]


    if nbytes != len(raw_data):
        LOGGER.error(
            'Invalid data length, expect {}, but real length is: {}'.format(
                nbytes, len(raw_data)))
        return None
    unpacked_values = st.unpack(data_type, raw_data)

    if data_type == 'BBB':  # 24-bit integer
        #there is a bug here 
        value = (unpacked_values[0] << 16)| (unpacked_values[1] << 8)| unpacked_values[2]
        results = (value, )
    elif data_length < 16 and data_length % 8 != 0:
        # bit-offset only for 8bits or 16 bits integer
        start_bit = nbytes * 8 - (offset_bit + data_length)
        results = (slice_bits(unpacked_values[0], start_bit, data_length), )
        # checked
    else:
        results = unpacked_values
    return results


def find_next_header(f):
    nbytes = 0
    bad_block = ''
    while True:
        x = f.read(1)
        if not x:
            break
        pos = f.tell()
        bad_block += ' ' + x.encode('hex')
        nbytes += 1
        if ord(x) == 0x0D:
            f.seek(pos - 1)
            return True, nbytes, bad_block
    return False, nbytes, bad_block

def get_parameter_physical_value(pcf_curtx, para_type, raw_values):
    """
    convert raw value  to physical value using the calibration factors in
    several IDB tables: txf, txp, pas, cap or mcf
    Args:
        pcf_curtx: parameter name known from pcf,such as CAAT1006TM
        raw_values:  raw value of the parameter,it is a tuple
        para_type:  parameter type
    Returns:
        physical values,eng_type (Float, Integral, String)
    """
    if not raw_values:
        return None,None

    if not pcf_curtx:
        if para_type == 'T':
            # timestamp
            return float(
                raw_values[0]) + float(raw_values[1]) / 65536.,'F'
        else:
            return raw_values,'I'
        # no need to interpret
    raw_value=raw_values[0]
    prefix = re.split('\d+', pcf_curtx)[0]
    if prefix in ['CIXTS', 'CAAT', 'CIXT']:
        # textual interpret
        sql = (
            'select TXP_ALTXT from TXP where  TXP_NUMBR=? and ?>=TXP_FROM '
            ' and TXP_TO>=? limit 1')
        args=(pcf_curtx, raw_value, raw_value)
        rows = STIX_IDB.execute(sql,args)
        if rows:
            return rows[0][0],'S'
    elif prefix == 'CIXP':
        sql = (
            'select cap_xvals, cap_yvals from cap '
            ' where cap_numbr=? order by cast(CAP_XVALS as double) asc'
        )
        args=(pcf_curtx,)
        # calibration curve defined in CAP database
        rows = STIX_IDB.execute(sql,args)
        if rows:
            x_points = [float(row[0]) for row in rows]
            y_points = [float(row[1]) for row in rows]
            tck = interpolate.splrep(x_points, y_points)
            # interpolate value using the calibration curve in CAP
            return interpolate.splev(raw_value, tck), 'F'
    elif prefix == 'NIX':
        # temperature
        # query PDI
        LOGGER.warning('{} not interpreted'.format(pcf_curtx))
        if pcf_curtx == 'NIX00101':
            #see SO-STIX-DS-30001_IDeF-X HD datasheet page 29
            pass


        return None,None
    elif prefix == 'CIX':
        # Polynomial
        sql = ('select MCF_POL1, MCF_POL2, MCF_POL3, MCF_POL4, MCF_POL5 '
               'from MCF where MCF_IDENT=? limit 1')
        args=(pcf_curtx)
        rows = STIX_IDB.execute(sql,args)
        if rows:
            pol_coeff = np.array([float(x) for x in rows[0]])
            x_points = np.array([math.pow(raw_value, i) for i in range(0, 5)])
            return np.dot(pol_coeff, x_points),'F'
        return None,None
    return None,None

def interpret_telemetry_parameter(app_data, par, parameter_interpret=True):
    name = par['PCF_NAME']
    if name == 'NIX00299':
        return None
    sw_desc = STIX_IDB.get_scos_description(name)
    desc = par['PCF_DESCR']
    offset = par['offset']
    offset_bit = int(par['offset_bit'])
    pcf_width = int(par['PCF_WIDTH'])
    ptc = int(par['PCF_PTC'])
    pfc = int(par['PCF_PFC'])
    pcf_curtx = par['PCF_CURTX']
    unit = par['PCF_UNIT']
    s2k_table = STIX_IDB.get_s2k_parameter_types(ptc, pfc)
    para_type = s2k_table['S2K_TYPE']
    raw_values = unpack_parameter(app_data, para_type, offset,
                                  offset_bit, pcf_width)

    if not parameter_interpret:
        return {'name': name,
                'raw': raw_values,
                'descr':desc,
                'value':None,
                'eng_value_type':None}

    physical_values, phys_value_type = get_parameter_physical_value(
        pcf_curtx, para_type, raw_values)
    if not physical_values:
        LOGGER.warning(
            'Parameter {} is not converted to physical value'.format(name))
    return {
        'name': name,
        'descr': desc,
        #'sw_desc': sw_desc,
        'raw': raw_values,
        #'pos': offset,
        #'offbit': offset_bit,
        #'width': pcf_width,
        #'unit': unit,
        'eng_value_type': phys_value_type,
        'value': physical_values
    }



def parse_telemetry_header(packet):
    # see STIX ICD-0812-ESC  (Page
    # 57)
    if ord(packet[0]) != 0x0D:
        return stix_global.HEADER_FIRST_BYTE_INVALID, None
    header_raw = st.unpack('>HHHBBBBIH', packet[0:16])
    header = {}
    for h, s in zip(header_raw, stix_header.telemetry_raw_structure):
        header.update(unpack_integer(h, s))
    status= check_header(header,'tm')
    if status == stix_global.OK:
        header.update({'segmentation': stix_header.packet_seg[header['seg_flag']]})
        header.update(
            {'time': header['fine_time'] / 65536. + header['coarse_time']})
    return status, header


def check_header(header,tmtc='tm'):
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


def parse_app_header(header, data, data_length):
    """
    Decode the data field header  and
    identify package types using
    Service type and service subtype 

    Args:
        header: a dictionary describe the header
        data: Application raw data
    Returns:

    """
    service_type = header['service_type']
    service_subtype = header['service_subtype']
    offset, width = STIX_IDB.get_packet_type_offset(service_type,
                                                    service_subtype)
    # see solar orbit ICD Page 36
    # width is in units of bits
    pi1_val = -1
    if offset != -1:
        start = offset - 16  # 16bytes read already
        end = start + width / 8  # it can be : 0, 16,8
        data_structure = '>B'
        if width == 16:
            data_structure = '>H'
        res = st.unpack(data_structure, data[start:end])
        pi1_val = res[0]
    type_info = STIX_IDB.get_packet_type_info(service_type, service_subtype,
                                              pi1_val)
    info = [{
        'DESCR': type_info['PID_DESCR']
    }, {
        'SPID': type_info['PID_SPID']
    }, {
        'TPSD': type_info['PID_TPSD']
    }, {
        'data_length': data_length
    }, {
        'SSID': pi1_val
    }]
    for e in info:
        header.update(e)

def parse_fixed_packet(app_data,spid):
    parameter_structures = STIX_IDB.get_fixed_packet_structure(spid)
    return get_fixed_packet_parameters(app_data, parameter_structures)


def get_fixed_packet_parameters(app_data, parameter_structure_list):
    """
    Extract parameters from a fixed data packet
    Structures of parameters are defined in the database PLF
    see Solar orbit IDB ICD section 3.3.2.5.1
    Args:
        app_data: application data
        parameter_structures :  [
                [PLF_NAME, PLF_OFFBY, PLF_OFFBI, PLF_NBOCC, PLF_LGOCC,'
                PLF_TIME, PLF_TDOCC, SDB_IMPORTED],
                ...
                ]
    Returns:
        A dictionary containing the extracted parameters, e.g.
        {
            para1: value1,
            para2: value2,
            ...
        }
    """
    parameters = []
    for par in parameter_structure_list:
        par['offset'] = int(par['PLF_OFFBY']) - 16
        # offset is known from the PLF table
        par['offset_bit'] = int(par['PLF_OFFBI'])
        par['type'] = 'fixed'
        parameter = interpret_telemetry_parameter(app_data, par,True)
        parameters.append(parameter)
    return parameters



def read_one_packet(in_file, logger):
    """
    Read one telemetry packet and parse the header
    Args:
       in_file: a python file object 
       logger:  STIX logger
    Returns:
       (status, header, header_raw, app_data, number_of_processed_bytes)

    """
    file_start_pos = in_file.tell()
    header_raw = in_file.read(16)
    if not header_raw:
        return stix_global.EOF, None, None, None, len(header_raw)
    header_status, header = parse_telemetry_header(header_raw)
    if header_status != stix_global.OK:
        if logger:
            logger.warning('Bad header around {}, error code: '.format(in_file.tell()), header_status)

        is_found, bytes_skipped, bad_block = find_next_header(in_file)
        if logger:
            logger.warning('Unexpected block around {}:'.format(in_file.tell()), bad_block)

        cur_pos = in_file.tell()
        if is_found and logger:
            logger.info('New header at ', cur_pos)
            logger.info('Bytes skipped ', bytes_skipped)
            return stix_global.NEXT_PACKET, None, header_raw,\
                None, cur_pos - file_start_pos
        else:
            return stix_global.EOF, None, header_raw,\
                None, cur_pos - file_start_pos
    data_length = header['length']
    app_length = (data_length + 1) - 10

    if app_length <= 0:  # wrong packet length
        logger.warning('Source data length 0')
        return stix_global.NEXT_PACKET, None, header_raw,None,\
                in_file.tell() - file_start_pos
    app_data = in_file.read(app_length)
    if len(app_data) != app_length:
        if logger:
            logger.error("No enough data was read")
        return stix_global.EOF, None, header_raw,\
            None, in_file.tell() - file_start_pos
    parse_app_header(header, app_data,app_length)
    return stix_global.OK, header, header_raw, app_data, \
        in_file.tell() - file_start_pos

def parse_telecommand_header(packet):
    # see STIX ICD-0812-ESC  (Page
    # 56)
    if ord(packet[0]) != 0x1D:
        return stix_global.HEADER_FIRST_BYTE_INVALID, None
    header_raw = st.unpack('>HHHBBBB', packet[0:10])
    header = {}
    for h, s in zip(header_raw, stix_header.telecommand_raw_structure):
        header.update(unpack_integer(h, s))
    status= check_header(header,'tc')
    info=STIX_IDB.get_telecommand_characteristics(header['service_type'],
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

def parse_telecommand_parameter(header,packet):
    pass


def parse_telecommand_packet(buf, logger):
    header_status,header=parse_telecommand_header(buf)
    if header_status != stix_global.OK:
        logger.warning('Bad telecommand header ')
    else:
        pprint.pprint(header)

    return header,None

def parse_telemetry_packet(buf):
    if len(buf)<=16:
        return stix_global.BAD_PACKET, None, None
    header_raw=buf[0:16]
    header_status, header = parse_telemetry_header(header_raw)
    app_length = header['length']-9
    app_raw=buf[17:]
    parse_app_header(header, app_raw, app_length)
    tpsd = header['TPSD']
    spid= header['SPID']
    if tpsd == -1:
        parameters = parse_fixed_packet(app_raw, spid)
    else:
        vpd_parser = vp.variable_parameter_parser(app_raw, spid)
        bytes_parsed, parameters = vpd_parser.get_parameters()
    return stix_global.OK, header, parameters


 
