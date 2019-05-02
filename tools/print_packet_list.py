#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : packet_stat.py
# @description  : packet statistics 
# @author       : Hualin Xiao
# @date         : Feb. 11, 2019
#

from __future__ import (absolute_import, unicode_literals)
import argparse
import pprint
from core import idb
from core import stix_global
from core import variable_parameter_parser as vp
from core import stix_writer
from core import stix_logger
from core import stix_parser
from core import stix_plotter


LOGGER = stix_logger.LOGGER
STIX_IDB = idb.STIX_IDB





def analyze_stix_raw_file(in_filename,out_filename=None):
    """
    Parse stix raw packets 
    Args:
     in_filename: input filename
     out_filename: output filename
     selected_spid: filter data packets by  SPID. 0  means to select all packets
    Returns:
    """
    spid_list = []
    pid=0
    fout=None
    if out_filename:
        fout=open(out_filename,'w')
    title=(' time, SPID, service, service_subtype, description\n')
    print(title)
    if fout:
        fout.write(title)
    with open(in_filename, 'rb') as in_file:
        num_packets = 0
        num_bytes_read = 0
        timestamps=[]
        while True:
            status, header, header_raw, application_data_raw, bytes_read = stix_parser.read_one_packet(
                in_file, LOGGER)
            num_bytes_read += bytes_read
            if status == stix_global.NEXT_PACKET:
                continue
            if status == stix_global.EOF:
                break

            packet_info=' {} , {}, {}, {},{}\n'.format(header['time'], 
                    header['SPID'],  header['service_type'],header['service_subtype'], header['DESCR'] ) 
            print(packet_info)
            if fout:
                fout.write(packet_info)




def main():
    in_filename = 'test/stix.dat'
    out_filename= None
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--in", required=True, help="input file")
    ap.add_argument("-o", "--out", required=False, help="output file")
    args = vars(ap.parse_args())
    if args['out'] is not None:
        out_filename= args['out']
    in_filename = args['in']
    analyze_stix_raw_file(in_filename,out_filename)


if __name__ == '__main__':
    main()
