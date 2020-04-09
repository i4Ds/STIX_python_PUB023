#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : parser_deamon.py
# @description  : STIX packet parser daemon. It detects new files in the given folder, 
#                 parses them  and stores the decoded packets in the MongoDB
# @author       : Hualin Xiao
# @date         : Feb. 11, 2020
#

import os
import sys
import glob
import time
sys.path.append('.')
from stix.core import config
from stix.core import mongo_db 
from stix.core import stix_logger, stix_idb, stix_parser
logger = stix_logger.get_logger()

S20_EXCLUDED=True


def process(instrument, filename, log_path):
    
    base= os.path.basename(filename)
    name=os.path.splitext(base)[0]
    log_filename=os.path.join(log_path,name+'.log')
    logger.set_logger(log_filename, level=3)
    parser = stix_parser.StixTCTMParser()
    parser.set_MongoDB_writer(config.mongodb['host'],config.mongodb['port'],
            config.mongodb['user'], config.mongodb['password'],'',filename, instrument)
    logger.info('Processing {} ...'.format(filename))
    if S20_EXCLUDED:
        parser.exclude_S20()
    parser.set_store_binary_enabled(False)
    parser.set_packet_buffer_enabled(False)
    try:
        parser.parse_file(filename) 
    except Exception as e:
        logger.error(str(e))
        return
    parser.done()

def main_loop():
    while True:
        print('Start checking ...')
        mdb=mongo_db.MongoDB(config.mongodb['host'], config.mongodb['port'], 
                config.mongodb['user'], config.mongodb['password'])

        filelist={}
        
        for instrument, selectors in config.deamon['data_source'].items():
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
                process(instrument, filename, config.deamon['log_path'])



        time.sleep(60)

if __name__ == '__main__':
    main_loop()

