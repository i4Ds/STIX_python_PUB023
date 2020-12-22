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
from stix.core import stix_datetime
from stix.core import mongo_db 
from stix.core import stix_logger, stix_idb, stix_parser
from stix.fits import fits_creator
from  stix.analysis import calibration
from  stix.analysis import flare_detection
from  stix.analysis import sci_packets_merger
logger = stix_logger.get_logger()

S20_EXCLUDED=True
DO_CALIBRATIONS=True
ENABLE_FITS_CREATION=True
DO_FLARE_SEARCH=True
DO_BULK_SCIENCE_DATA_MERGING=True

daemon_config=config.get_config()['pipeline']['daemon']
noti_config=daemon_config['notification']
mongodb_config=config.get_config()['pipeline']['mongodb']

def get_now():
    return datetime.now().isoformat()



def create_notification(raw_filename, alert_headers, summary, flare_info):
    with open(noti_config['file'],'a+') as log:
        msg='New file: {}\n'.format(raw_filename)
        msg+='Data acq. time: {} - {} \n'.format(stix_datetime.unix2utc(summary['data_start_unix_time']),
                stix_datetime.unix2utc(summary['data_stop_unix_time']),
                )
        file_id=summary['_id']
        msg+='\n'
        msg+='\nHK plots: https://www.cs.technik.fhnw.ch/stix/view/plot/housekeeping/file/{}\n'.format(file_id)
        try:
            if '54118' in summary['summary']['spid']:
                msg+='\nLightcurves: https://www.cs.technik.fhnw.ch/stix/view/plot/lightcurves?run={}\n'.format(file_id)
            msg+='\nFITS files: https://www.cs.technik.fhnw.ch/stix/view/list/fits/file/{}\n'.format(file_id)
            if summary['calibration_run_ids']:
                msg+='\nCalibration: https://www.cs.technik.fhnw.ch/stix/view/plot/calibration/file/{}\n'.format(file_id)
        except Exception as e:
            print(e)
            pass
        msg+='\n'
        if alert_headers:
            msg+='STIX Service 5 message:\n'
            for header in alert_headers:
                msg+='\tAt {}, TM({},{}) {}\n'.format(header['UTC'], header['service_type'],
                    header['service_subtype'],header['descr'] )
        else:
            msg+='No Service 5 report in the file.\n'

        if flare_info:
            msg+='''\nSTIX detected at least {} solar flares\n \n'''.format(flare_info['num_peaks'])
        else:
            msg+='\n No solar flare  detected.\n'


        log.write(msg)


def remove_ngnix_cache_files():
    '''
        remove ngnix cache if ngnix cache folder is defined in the configuration file
    '''
    try:
        files=glob.glob(daemon_config['ngnix_cache'])
    except Exception:
        return
    for fname in files:
        os.remove(fname)



def process(instrument, filename):
    base= os.path.basename(filename)
    name=os.path.splitext(base)[0]
    flare_info=None
    log_path=daemon_config['log_path']
    log_filename=os.path.join(log_path,name+'.log')
    logger.set_logger(log_filename, level=3)
    parser = stix_parser.StixTCTMParser()
    parser.set_MongoDB_writer(mongodb_config['host'],mongodb_config['port'],
            mongodb_config['user'], mongodb_config['password'],'',filename, instrument)
    logger.info('{}, processing {} ...'.format(get_now(), filename))
    print('{}, processing {} ...'.format(get_now(), filename))
    if S20_EXCLUDED:
        parser.exclude_S20()
    parser.set_store_binary_enabled(False)
    parser.set_packet_buffer_enabled(False)
    alert_headers=None
    try:
        parser.parse_file(filename) 
        alert_headers=parser.get_stix_alerts()
    except Exception as e:
        logger.error(str(e))
        return
    summary=parser.done()
    if summary:
        if DO_CALIBRATIONS:
            logger.info('Starting calibration spectrum analysis...')
            try:
                calibration_run_ids=summary['calibration_run_ids']
                report_path=daemon_config['report_path']
                for run_id in calibration_run_ids:
                    calibration.analyze(run_id, report_path)
            except Exception as e:
                logger.error(str(e))
        if ENABLE_FITS_CREATION:
            file_id=summary['_id']
            fits_creator.create_fits(file_id, daemon_config['fits_path'])
        if DO_FLARE_SEARCH:
            print('Searching for flares')
            flare_info=flare_detection.search(file_id)
        if DO_BULK_SCIENCE_DATA_MERGING:
            print('merging bulk science data')
            sci_packets_merger.process(file_id)

    try:
        create_notification(base,alert_headers, summary,flare_info )
    except Exception as e:
        print(str(e))
    remove_ngnix_cache_files()

def main_loop():
    while True:

        print('Start checking ...')
        print(get_now())
        mdb=mongo_db.MongoDB(mongodb_config['host'], mongodb_config['port'], 
                mongodb_config['user'], mongodb_config['password'])

        filelist={}
        
        for instrument, selectors in daemon_config['data_source'].items():
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

