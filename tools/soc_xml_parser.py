#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @description  : STIX TM packet parser 
# @author       : Hualin Xiao
# @date         : March. 28, 2019
#

from __future__ import (absolute_import, unicode_literals)
import argparse
import pprint
import binascii
from cStringIO import StringIO
import xmltodict
from core import idb
from core import stix_global
#from core import variable_parameter_parser as vp
from core import variable_parameter_parser_tree_struct as vp
#from stix_io import stix_writer
from stix_io import stix_writer_sqlite as stw
from stix_io import stix_logger
from core import stix_parser

LOGGER = stix_logger.LOGGER


def parse_esa_xml_file(in_filename, out_filename=None, selected_spid=0):
    """
    Parse STIX raw TM packets  
    Args:
     in_filename: input filename
     out_filename: output filename
     selected_spid: filter data packets by  SPID. 0  means to select all packets
    Returns:
    """
    packets=[]
    with open(in_filename) as fd:
        doc = xmltodict.parse(fd.read())
        for e in doc['ns2:ResponsePart']['Response']['PktRawResponse']['PktRawResponseElement']:
            packet={'id':e['@packetID'],
                    'raw':e['Packet'][60:]}
            packets.append(packet)

        num_packets = 0
        num_fix_packets=0
        num_variable_packets=0
        num_bytes_read = 0
        st_writer = stw.stix_writer(out_filename)
        st_writer.register_run(in_filename)

        total_packets=0
        for packet in packets:
            data_hex=packet['raw']
            data_binary= binascii.unhexlify(data_hex)
            in_file=StringIO(data_binary)

            status, header, header_raw, application_data_raw, num_bytes_read = stix_parser.read_one_packet_from_binary_file(
                in_file, LOGGER)
            total_packets += 1
            if status == stix_global.NEXT_PACKET:
                continue
            if status == stix_global.EOF:
                break
            spid = header['SPID']
            tpsd = header['TPSD']
            if selected_spid > 0 and spid != selected_spid:
                continue
            st_writer.write_header(header)

            parameters = None
            application_data_raw_length = len(application_data_raw)
            num_packets += 1
            if tpsd == -1:
                # see SCOS ICD page 28
                parameters = stix_parser.parse_fixed_packet(
                    application_data_raw, spid)
                num_fix_packets += 1

            else:
                vpd_parser = vp.variable_parameter_parser(
                    application_data_raw, spid)
                processed_data_length, parameters = vpd_parser.get_parameters()
                if processed_data_length != application_data_raw_length:
                    LOGGER.info("Packet length invalid, data length: {}, processed: {}".format(application_data_raw_length,
                        processed_data_length))
                num_variable_packets += 1
            
            msg_dict={'packet_id':packet['id'],'header':header,'parameter':parameters}
            pprint.pprint(msg_dict)
            st_writer.write_parameters(parameters)

        LOGGER.info('{} packets found in the file: {}'.format(total_packets,in_filename))
        LOGGER.info('{} ({} fixed and {} variable) packets processed.'.format(num_packets,\
                num_fix_packets,num_variable_packets))
        LOGGER.info('Writing parameters to file {} ...'.format(out_filename))
        st_writer.done()
        LOGGER.info('Done.')


def main():
    in_filename = 'test/stix.xml'
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
