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

from stix.core import stix_parser
from stix.core import stix_idb
from stix.analysis import calibration
from stix.analysis import housekeeping as hk
from stix.analysis import ql_lightcurve as qllc
from stix.analysis import ql_background as qlbkg

from stix.core import mongo_db

OUTPUT_PDF_DIRECTORY='pdf'

STIX_MDB= mongo_db.MongoDB()

def get_pdf_filename(run_id):
    filename='{}/Quicklook_File_{}.pdf'.format(OUTPUT_PDF_DIRECTORY,run_id)
    return os.path.abspath(filename)


def generate_pdf(packets, pdf_filename=None, process='all', write_db=False, run_id=-1):
    if not pdf_filename:
        print("PDF filename can be empty.")
        return
    if write_db and run_id==-1:
        print("run ID invalid.")
        return 

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
        if process in ['qlbkg','all']:
            plugin_qlbkg = qlbkg.Plugin(packets)
            plugin_qlbkg.run(pdf)




def process_packets_in_database():

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
        choices=('hk', 'cal', 'qllc', 'qlbkg', 'all'),
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
        packets = STIX_MDB.select_packets_by_run(run)
        print("Requesting packets from mongodb...")
        print('Number of packets:{}'.format(len(packets)))
        generate_pdf(packets,out, process_type, write_db, run)


if __name__ == '__main__':
    process_packets_in_database()
