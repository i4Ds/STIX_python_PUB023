#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : soc_ascii_paser.py
# @description  : STIX TM packet parser
# 
# @author       : Hualin Xiao
# @date         : April 15, 2019
#

from __future__ import (absolute_import, unicode_literals)
import argparse
import pprint
import binascii
from cStringIO import StringIO
import xmltodict
from core import idb
from core import stix_global
from stix_io import stix_writer_sqlite as stw
from stix_io import stix_logger
from tools import parser
from datetime import datetime

LOGGER = stix_logger.LOGGER


def parse_soc_ascii_file(in_filename, out_filename=None, selected_spid=0):
    """each line like:
       2019-04-10T01:45:34.258Z 0DA7C001000B10050100800000050B400011
    """
    packets=[]
    with open(in_filename) as fd:
        num_packets = 0
        num_fix_packets=0
        num_variable_packets=0
        num_bytes_read = 0
        st_writer = stw.stix_writer(out_filename)
        st_writer.register_run(in_filename)
        total_packets=0
        for line  in fd:
            [utc_timestamp,data_hex]=line.strip().split()
            data_binary= binascii.unhexlify(data_hex)
            in_file=StringIO(data_binary)
            status, header, parameters, param_type, num_bytes_read = parser.parse_one_packet(
                in_file, LOGGER)
            total_packets += 1
            header['time']=utc_timestamp
            LOGGER.pprint(header, parameters)
            if param_type ==1:
                num_fix_packets += 1
            elif param_type == 2: 
                num_variable_packets += 1
            if header and parameters:
                st_writer.write_parameters(parameters)

        LOGGER.info('{} packets found in the file: {}'.format(total_packets,in_filename))
        LOGGER.info('{} ({} fixed and {} variable) packets processed.'.format(num_packets,\
                num_fix_packets,num_variable_packets))
        LOGGER.info('Writing parameters to file {} ...'.format(out_filename))
        st_writer.done()
        LOGGER.info('Done.')


def main():
    in_filename = 'test/stix.ascii'
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
    parse_soc_ascii_file(in_filename, out_filename, sel_spid)


if __name__ == '__main__':
    main()
