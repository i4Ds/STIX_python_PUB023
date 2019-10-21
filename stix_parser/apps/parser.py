#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @description  : STIX TM packet parser
# @author       : Hualin Xiao
# @date         : Feb. 11, 2019
#

import os
import sys
sys.path.append(os.path.abspath(__file__ + "/../../"))

import argparse
from core import stix_logger
from core import stix_parser
from core import stix_idb

STIX_LOGGER = stix_logger.stix_logger()


def main():

    ap = argparse.ArgumentParser()
    required = ap.add_argument_group('Required arguments')
    optional = ap.add_argument_group('Optional arguments')

    required.add_argument(
        "-i",
        dest='input',
        required=True,
        nargs='?',
        help="Input raw data filename.")
    optional.add_argument(
        "-o",
        dest='output',
        default=None,
        required=False,
        help="Output filename. ")

    optional.add_argument(
        "--idb",
        dest='idb',
        default=None,
        required=False,
        help="IDB sqlite3 filename. ")

    optional.add_argument(
        "--opf",
        dest='param_format',
        default='tuple',
        required=False,
        choices=('tuple', 'dict'),
        help="format to store output parameters. ")

    optional.add_argument(
        "-t",
        dest='input_type',
        default=None,
        choices=('bin', 'ascii', 'xml', 'hex'),
        help=
        "Input file type. Four types (bin, hex, ascii or xml) are supported.")

    optional.add_argument(
        "--wdb",
        dest='wdb',
        default=False,
        action='store_true',
        help='Write decoded packets to local MongoDB.')
    optional.add_argument(
        "--db-host",
        dest='db_host',
        default='localhost',
        help='MongoDB host IP.')
    optional.add_argument(
        "--db-port",
        dest='db_port',
        default=27017,
        type=str,
        help='MongoDB host port.')
    optional.add_argument(
        "--db-user", dest='db_user', default='', help='MongoDB username.')
    optional.add_argument(
        "--db-pwd", dest='db_pwd', default='', help='MongoDB password.')
    optional.add_argument(
        "-m", default='', dest='comment', required=False, help="comment")

    optional.add_argument(
        '--SPID',
        nargs='*',
        dest='SPID',
        action="store",
        default=[],
        type=int,
        help='Only to parse the packets of the given SPIDs.')
    optional.add_argument(
        '--services',
        nargs='*',
        dest='services',
        action="store",
        default=[],
        type=int,
        help='Only to parse the packets of the given service types.')
    optional.add_argument(
        "-v",
        dest="verbose",
        default=5,
        required=False,
        help="Logger verbose level",
        type=int)
    optional.add_argument(
        "-l",
        "--log",
        dest='logfile',
        default=None,
        required=False,
        help="Log filename")

    args = vars(ap.parse_args())
    STIX_LOGGER.set_logger(args['logfile'], args['verbose'])
    if args['idb']:
        idb_instance = stix_idb.stix_idb(args['idb'])

    parser = stix_parser.StixTCTMParser()
    param_format = args['param_format']
    if args['wdb']:
        param_format = 'tuple'
        #must be tuple as they consume  less storage
    parser.set_parameter_format(param_format)

    selected_spids = args['SPID']
    selected_services = args['services']
    parser.set_packet_filter(selected_services, selected_spids)

    if args['output']:
        parser.set_store_packet_enabled(False)
        parser.set_store_binary_enabled(False)
        parser.set_pickle_writer(args['output'], args['comment'])
    if args['wdb']:
        parser.set_store_packet_enabled(False)
        parser.set_store_binary_enabled(False)
        parser.set_store_packet_enabled(False)
        parser.set_MongoDB_writer(args['db_host'], args['db_port'],
                                  args['db_user'], args['db_pwd'],
                                  args['comment'])

    parser.parse_file(args['input'], args['input_type'])
    parser.done()


if __name__ == '__main__':
    main()
