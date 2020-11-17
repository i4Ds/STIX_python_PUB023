#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : parser_daemon.py
# @description  : STIX packet parser daemon. It detects new files in the specified folder, 
#                 parses the packets and stores the decoded packets in the MongoDB
# @author       : Hualin Xiao
# @date         : Feb. 11, 2020
#

import os
import sys
import glob
import time
sys.path.append('.')
from datetime import datetime
from stix.core import config
from stix.core import mongo_db 
from stix.core import stix_logger, stix_idb, stix_parser
from stix.fits import fits_creator
from  stix.analysis import calibration
from  stix.analysis import flare_detection
logger = stix_logger.get_logger()

S20_EXCLUDED=True
DO_CALIBRATIONS=True
ENABLE_FITS_CREATION=True
DO_FLARE_SEARCH=True

DAEMON_CONFIG=config.get_config()['pipeline']['daemon']
MONGODB_CONFIG=config.get_config()['pipeline']['mongodb']

def get_now():
    return datetime.now().isoformat()


def write_alerts(raw_filename, alert_headers):
    #print(alert_headers)
    if not alert_headers:
        logger.info('No instrument warning or error message.')
        return
    with open(DAEMON_CONFIG['alert_log'],'a+') as log:
        log.write('File: {}\n'.format(raw_filename))
        for header in alert_headers:
            msg='\tAt {}, TM({},{}) {}\n'.format(header['UTC'], header['service_type'],
                header['service_subtype'],header['descr'] )
            log.write(msg)
        #if other_message:
        #    log.write(other_message)
        #log.close()

def create_flare_notification(raw_filename, flare_info):
    if not flare_info:
        return

    with open(DAEMON_CONFIG['alert_log'],'a+') as log:
        log.write('File: {}\n'.format(raw_filename))
        msg='''\nSTIX detected {} solar flares\n UTC:\n'''.format(flare_info['num_peaks'])
        msg+='\t'.join(flare_info['peak_utc'])
        msg+='\nPeak counts:\n'
        msg+=str(flare_info['peak_counts'])
        msg+='\n'
        msg+='https://www.cs.technik.fhnw.ch/stix/view/plot/lightcurves?run={}'.format(flare_info['run_id'])
        log.write(msg)
        log.close()


def remove_ngnix_cache_files():
    '''
        remove ngnix cache if ngnix cache folder is defined in the configuration file
    '''
    try:
        files=glob.glob(DAEMON_CONFIG['ngnix_cache'])
    except Exception:
        return
    for fname in files:
        os.remove(fname)



def process(instrument, filename):
    base= os.path.basename(filename)
    name=os.path.splitext(base)[0]
    log_path=DAEMON_CONFIG['log_path']
    log_filename=os.path.join(log_path,name+'.log')
    logger.set_logger(log_filename, level=3)
    parser = stix_parser.StixTCTMParser()
    parser.set_MongoDB_writer(MONGODB_CONFIG['host'],MONGODB_CONFIG['port'],
            MONGODB_CONFIG['user'], MONGODB_CONFIG['password'],'',filename, instrument)
    logger.info('{}, processing {} ...'.format(get_now(), filename))
    print('{}, processing {} ...'.format(get_now(), filename))
    if S20_EXCLUDED:
        parser.exclude_S20()
    parser.set_store_binary_enabled(False)
    parser.set_packet_buffer_enabled(False)
    try:
        parser.parse_file(filename) 
        alert_headers=parser.get_stix_alerts()
        write_alerts(base,alert_headers)
    except Exception as e:
        logger.error(str(e))
        return
    summary=parser.done()
    remove_ngnix_cache_files()
    if summary:
        if DO_CALIBRATIONS:
            logger.info('Starting calibration spectrum analysis...')
            try:
                calibration_run_ids=summary['calibration_run_ids']
                report_path=DAEMON_CONFIG['report_path']
                for run_id in calibration_run_ids:
                    calibration.analyze(run_id, report_path)
            except Exception as e:
                logger.error(str(e))
        if ENABLE_FITS_CREATION:
            file_id=summary['_id']
            fits_creator.create_fits(file_id, DAEMON_CONFIG['fits_path'])
        if DO_FLARE_SEARCH:
            print('Searching for flares')
            results=flare_detection.search(file_id)
            if results:
                create_flare_notification(file_id,results)

def main_loop():
    while True:

        print('Start checking ...')
        print(get_now())
        mdb=mongo_db.MongoDB(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'], 
                MONGODB_CONFIG['user'], MONGODB_CONFIG['password'])

        filelist={}
        
        for instrument, selectors in DAEMON_CONFIG['data_source'].items():
            for pattern in selectors:
                filenames=glob.glob(pattern)
                for filename in filenames:
                    file_id=mdb.get_file_id(filename)
                    if file_id == -2 :
                        if instrument not in filelist:
                            filelist[instrument]=[]
                        filelist[instrument].append(filename)

        mdb.close()
        for instrument, files in filelist.items():
            for filename in files:
                process(instrument, filename)

        time.sleep(60)

if __name__ == '__main__':
    if len(sys.argv)==1:
        main_loop()
    else:
        #for test
        process('GU', sys.argv[1])

