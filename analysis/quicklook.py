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
from analysis import calibration 
from analysis import housekeeping as hk2
from analysis import ql_lightcurve as qllc

from utils import mongo_db
STIX_LOGGER = stix_logger.stix_logger()


def process(run_id, output, process='hk'):
    mdb = mongo_db.MongoDB()
    print("request packet from mongodb")
    packets = mdb.select_packets_by_run(run_id)
    print('number of packets:{}'.format(len(packets)))
    plugin=None
    if process=='hk':
        plugin = hk2.Plugin(packets)
    elif process=='cal':
        plugin = calibration.Plugin(packets)
    elif process=='qllc':
        plugin=qllc.Plugin(packets)
    if plugin:
        plugin.run(output)


def main():

    ap = argparse.ArgumentParser()
    required = ap.add_argument_group('Required arguments')
    optional = ap.add_argument_group('Optional arguments')


    required.add_argument(
        "-i", dest='run', required=True, nargs='?', help="run ID.")
    optional.add_argument(
        "-o",
        dest='output',
        default=None,
        required=False,
        help="Output filename. ")
    
    required.add_argument(
        "-p", dest='process', required=True,  
        choices=('hk','cal','qllc'),help="what processing ?")

    args = vars(ap.parse_args())
    process(args['run'], args['output'], args['process'])


if __name__ == '__main__':
    main()
