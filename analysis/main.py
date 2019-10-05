#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @description  : STIX TM packet parser
# @author       : Hualin Xiao
# @date         : Feb. 11, 2019
#

#from __future__ import (absolute_import, unicode_literals)
import sys
import argparse
sys.path.append('..')
sys.path.append('.')
from core import stix_logger
from core import stix_parser
from core import stix_idb
from analysis import calibration_plugin_pdf  as calibration
from analysis import hk2_pdf as hk2 

from utils import mongo_db
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

    
    args = vars(ap.parse_args())
    if args['idb']:
        idb_instance = stix_idb.stix_idb(args['idb'])
    parser = stix_parser.StixTCTMParser()
    parser.set_parameter_format('tuple')

    packets=parser.parse_file(args['input'])
    output=args['output']
    
    print('number of packets:{}'.format(len(packets)))
    #plugin=cal.Plugin(packets)
    plugin=hk2.Plugin(packets)
    plugin.run(output)


if __name__ == '__main__':
    main()
