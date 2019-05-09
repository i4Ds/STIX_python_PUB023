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
from core import stix_telemetry_parser
from core import stix_logger
LOGGER = stix_logger.LOGGER
def main():
    in_filename = 'test/stix.dat'
    out_filename = ''
    sel_spid = 0
    logger_level=10
    #pkl or db
    ap = argparse.ArgumentParser()
    output_param_type='tree'
    ap.add_argument("-i", "--in", required=True, help="input file")
    ap.add_argument("-o", "--out", required=False, help="output file")
    ap.add_argument(
        "-s", "--sel", required=False, help="only select packets of the given SPID")
    ap.add_argument(
        "-p", "--ptype", required=False, help="output parameter type. Can be tree or array")

    ap.add_argument(
        "-f", "--ftype", required=False, help="output file type. Can be db (sqlite database) or pkl (compressed python pickle file) ")

    ap.add_argument(
        "-l", "--level", required=False, help="Logger verbose level")

    args = vars(ap.parse_args())

    if args['sel'] is not None:
        sel_spid = int(args['sel'])

    if args['level'] is not None:
        logger_level= int(args['level'])

    if args['ptype'] is not None:
        output_param_type= args['ptype']


    if args['out'] is not None:
        out_filename = args['out']



    in_filename = args['in']

    LOGGER.set_level(logger_level)
    LOGGER.info('Input', in_filename)
    LOGGER.info('Output', out_filename)

    stix_telemetry_parser.parse_stix_raw_file(in_filename,LOGGER, 
            out_filename, sel_spid, output_param_type=output_param_type)


if __name__ == '__main__':
    main()
