#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @description  : STIX TM packet parser 
# @author       : Hualin Xiao
# @date         : Feb. 11, 2019
#

from __future__ import (absolute_import, unicode_literals)
import argparse
import pprint
from core import idb
from core import stix_global
#from core import variable_parameter_parser as vp
from core import variable_parameter_parser_tree_struct as vp
#from stix_io import stix_writer
from stix_io import stix_writer_sqlite as stw
from stix_io import stix_logger
from core import stix_parser

LOGGER = stix_logger.LOGGER

def parse_one_packet(in_file,logger,selected_spid=0):
    status, header, header_raw, app_raw, num_read = stix_parser.read_one_packet_from_binary_file(
                in_file, logger)
    parameters = None
    param_type=-1
    if status!= stix_global.NEXT_PACKET and status != stix_global.EOF and header:
        spid = header['SPID']
        tpsd = header['TPSD']
        if selected_spid == 0 or spid == selected_spid:
            app_raw_length = len(app_raw)
            if tpsd == -1:
                parameters = stix_parser.parse_fixed_packet(
                    app_raw, spid)
                param_type=1
            else:
                vpd_parser = vp.variable_parameter_parser(
                    app_raw, spid)
                bytes_parsed, parameters = vpd_parser.get_parameters()
                if bytes_parsed!= app_raw_length:
                    logger.info("Packet length invalid, data length: {}, processed: {}".format(
                        app_raw_length, bytes_parsed))
                param_type=2

    return status, header, parameters, param_type, num_read


def parse_stix_raw_file(in_filename, out_filename=None, selected_spid=0):
    """
    Parse STIX raw TM packets 
    Args:
     in_filename: input filename
     out_filename: output filename
     selected_spid: filter data packets by  SPID. 0  means to select all packets
    Returns:

    """
    with open(in_filename, 'rb') as in_file:
        num_packets = 0
        num_fix_packets=0
        num_variable_packets=0
        num_bytes_read = 0
        st_writer = stw.stix_writer(out_filename)
        st_writer.register_run(in_filename)

        total_packets=0
        while True:
            status, header, parameters, param_type, num_bytes_read = parse_one_packet(in_file, LOGGER,selected_spid)
            total_packets += 1
            if status == stix_global.NEXT_PACKET:
                continue
            if status == stix_global.EOF:
                break
            if param_type ==1:
                num_fix_packets += 1
            elif param_type == 2: 
                num_variable_packets += 1
            
            LOGGER.pprint(header,parameters)
            if status and parameters:
                st_writer.write_header(header)
                st_writer.write_parameters(parameters)

        LOGGER.info('{} packets found in the file: {}'.format(total_packets,in_filename))
        LOGGER.info('{} ({} fixed and {} variable) packets processed.'.format(num_packets,\
                num_fix_packets,num_variable_packets))
        LOGGER.info('Writing parameters to file {} ...'.format(out_filename))
        st_writer.done()
        LOGGER.info('Done.')


def main():
    in_filename = 'test/stix.dat'
    out_filename = 'stix_out.db'
    sel_spid = 0
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--in", required=True, help="input file")
    ap.add_argument("-o", "--out", required=False, help="output file")
    ap.add_argument(
        "-s", "--sel", required=False, help="only select packets of the given SPID")

    args = vars(ap.parse_args())
    if args['out'] is not None:
        out_filename = args['out']
    if args['sel'] is not None:
        sel_spid = int(args['sel'])
    in_filename = args['in']
    LOGGER.info('Input file', in_filename)
    LOGGER.info('Output file', out_filename)
    parse_stix_raw_file(in_filename, out_filename, sel_spid)


if __name__ == '__main__':
    main()
