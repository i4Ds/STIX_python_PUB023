#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @description  : STIX TM packet parser
# @author       : Hualin Xiao
# @date         : Feb. 11, 2019
#

#from __future__ import (absolute_import, unicode_literals)
import argparse
import pprint
import sys
sys.path.append('..')
sys.path.append('.')
from core import stix_logger
from core import stix_parser


def main():
    in_filename = ''
    out_filename = ''
    sel_spid = 0
    verbose = 10
    logfile = None
    file_type='binary'
    comment=''
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--in",  required=True, nargs='?', help="input filename")
    ap.add_argument("-o", "--out", required=False, nargs='?',help="output filename")
    ap.add_argument("-m", "--comment", required=False, help="comment")
    ap.add_argument("-t", "--ftype", required=False, choices=('binary', 'ascii', 'xml'),
            help="Input file type: binary, ascii or xml ")
    """
    ascii file structure:
    UTC HEX
    """
    ap.add_argument(
        "-s",
        "--sel",
        required=False,
        help="only select packets of the given SPID")
    ap.add_argument(
        "-v", "--verbose", required=False, help="Logger verbose level")

    ap.add_argument("-l", "--log", required=False, help="Log filename")

    args = vars(ap.parse_args())

    if args['sel'] is not None:
        sel_spid = int(args['sel'])

    if args['verbose'] is not None:
        verbose = int(args['verbose'])

    if args['log'] is not None:
        logfile = args['log']


    if args['out'] is not None:
        out_filename = args['out']
    if args['ftype'] is not None:
        file_type= args['ftype']

    if args['comment'] is not None:
        comment= args['comment']


    in_filename = args['in']

    stix_logger._stix_logger.set_logger(logfile, verbose)
    parser = stix_parser.StixTCTMParser()
    selected_spids=[sel_spid,]
    parser.parse_file(in_filename, out_filename, selected_spids=selected_spids, 
            file_type=file_type, comment=comment)


if __name__ == '__main__':
    main()
