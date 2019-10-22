#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @author       : Hualin Xiao
# @date         : Feb. 11, 2019
#
# To process all unprocessed file run ./analysis/quick_processing  --wdb  --all

#from __future__ import (absolute_import, unicode_literals)
import sys
import os
sys.path.append(os.path.abspath(__file__ + "/../../"))

import argparse
from matplotlib.backends.backend_pdf import PdfPages

from core import stix_logger
from core import stix_parser
from core import stix_idb
from analysis import calibration
from analysis import housekeeping as hk
from analysis import ql_lightcurve as qllc

from core import mongo_db
STIX_LOGGER = stix_logger.stix_logger()

OUTPUT_PDF_DIRECTORY='pdf'

STIX_MDB= mongo_db.MongoDB()

def get_pdf_filename(run_id):
    filename='{}/Quicklook_File_{}.pdf'.format(OUTPUT_PDF_DIRECTORY,run_id)
    return os.path.abspath(filename)



def process(run_id, pdf_filename=None, process='all', write_db=False):
    print("Request packet from mongodb...")
    packets = STIX_MDB.select_packets_by_run(run_id)
    print('number of packets:{}'.format(len(packets)))
    with PdfPages(pdf_filename) as pdf:
        plugin = None
        if write_db:
            print('Storing the pdf filename to MongoDB ...')
            STIX_MDB.set_run_ql_pdf(run_id,os.path.abspath(pdf_filename))
        if process in ['hk','all'] :
            plugin_hk = hk.Plugin(packets)
            plugin_hk.run(pdf)
        if process in ['cal','all']:
            plugin_cal = calibration.Plugin(packets)
            plugin_cal.run(pdf)
        if process in ['qllc','all']:
            plugin_qllc = qllc.Plugin(packets)
            plugin_qllc.run(pdf)




def main():

    ap = argparse.ArgumentParser()
    required = ap.add_argument_group('Required arguments')
    optional = ap.add_argument_group('Optional arguments')

    optional.add_argument(
        "-i", dest='run',  default=None,  required=False, nargs='?', help="run ID.")

    optional.add_argument(
        "--all", dest='all_runs',  default=None, 
        action='store_true',
        required=False, help="Get a list of unprocessed runs from MongoDB and process all of them.")


    optional.add_argument(
        "-o",
        dest='output',
        default='',
        required=False,
        help="Output filename. PDF files are stored in folder {} if not specified.".format(OUTPUT_PDF_DIRECTORY))

    required.add_argument(
        "-p",
        dest='process_type',
        required=False,
        default='all',
        choices=('hk', 'cal', 'qllc', 'all'),
        help="select the type of processing")

    required.add_argument(
        "--wdb",
        dest='write_db',
        required=False,
        default=False,
        action='store_true',
        help="whether write processing run to the local MongoDB")
    runs=[]
    outputs=[]

    args = vars(ap.parse_args())
    process_type=args['process_type']
    write_db=args['write_db']
    
    if args['run']:
        runs=[int(args['run'])]
    if args['all_runs']:
        runs=STIX_MDB.get_unprocessed()
        print(runs)

    if args['output']:
        outputs=[args['output']]


    if not args['output'] and runs:
        outputs=[ get_pdf_filename(x) for x in runs]


    print(runs)
    print(outputs)

    for run, out  in zip(runs,outputs):
        print('Processing run # {}'.format(run))
        print('PDF filename:  {}'.format(out))
        process(run,out, process_type, write_db)


if __name__ == '__main__':
    main()
