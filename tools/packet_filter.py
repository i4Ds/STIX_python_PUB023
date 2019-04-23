#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : packet_filter.py
# @description  : a script to filter stix TM packets by SPID
# @author       : Hualin Xiao
# @date         : March 12, 2019
#

from __future__ import (absolute_import, unicode_literals)
import argparse
import pprint
from core import idb
from core import stix_global
from core import variable_parameter_parser as vp
from stix_io import stix_writer
from stix_io import stix_logger
from core import stix_parser

LOGGER = stix_logger.LOGGER


def packet_filter(in_filename, out_filename, selected_spid):
    """
    Parse stix raw packets 
    Args:
     in_filename: input filename
     out_filename: output filename
     selected_spid: filter data packets by  SPID. 0  means to select all packets
    Returns:
    """
    with open(in_filename, 'rb') as fin, \
            open(out_filename, 'wb') as fout:
        num_selected_packets = 0
        num_total_packets = 0
        while True:
            status, header, header_raw, application_data_raw, num_bytes_read = stix_parser.read_one(
                fin, LOGGER)
            if status == stix_global.NEXT_PACKET:
                continue
            if status == stix_global.EOF:
                break
            spid = header['SPID']
            num_total_packets += 1
            if spid == selected_spid:
                num_selected_packets += 1
                fout.write(header_raw)
                fout.write(application_data_raw)

        LOGGER.info('Done')
        LOGGER.info('{}/{} packets have been written to {}'.format(
            num_selected_packets, num_total_packets, out_filename))


def main():
    in_filename = 'test/stix.dat'
    out_filename = 'stix_export.dat'
    selected_spid = 0
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--in", required=True, help="input file")
    ap.add_argument("-o", "--out", required=True, help="output file")
    ap.add_argument("-s", "--sel", required=True, help="select packets by SPID")

    args = vars(ap.parse_args())
    if args['out'] is not None:
        out_filename = args['out']
    if args['sel'] is not None:
        selected_spid = int(args['sel'])
    in_filename = args['in']
    LOGGER.info('Input file', in_filename)
    LOGGER.info('Output file', out_filename)
    packet_filter(in_filename, out_filename, selected_spid)


if __name__ == '__main__':
    main()
