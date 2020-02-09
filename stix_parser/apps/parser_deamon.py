#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : parser.py
# @description  : STIX TCTM packet parser
# @author       : Hualin Xiao
# @date         : Feb. 11, 2020
#

import os
import sys
import glob
import time
sys.path.append('.')
from stix_parser.core import config
from stix_parser.core import mongo_db 
from stix_parser.core import stix_logger, stix_idb, stix_parser
logger = stix_logger.get_logger()

S20_EXCLUDED=True


def process(filename, log_path):
    
    base= os.path.basename(filename)
    name=os.path.splitext(base)[0]
    log_filename=os.path.join(log_path,name+'.log')
    logger.set_logger(log_filename, level=3)
    parser = stix_parser.StixTCTMParser()
    parser.set_MongoDB_writer(config.mongodb['host'],config.mongodb['port'],
            config.mongodb['user'], config.mongodb['password'],'',filename)
    logger.info('Processing {} ...'.format(filename))
    if S20_EXCLUDED:
        parser.exclude_S20()
    parser.set_store_binary_enabled(False)
    parser.set_packet_buffer_enabled(False)
    parser.parse_file(filename) 
    parser.done()

def main_loop():
    while True:
        print('Start checking ...')
        unprocessed_files=[]
        mdb=mongo_db.MongoDB(config.mongodb['host'], config.mongodb['port'], 
                config.mongodb['user'], config.mongodb['password'])
        
        for pattern in config.deamon['raw_patterns']:
            filenames=glob.glob(pattern)
            for filename in filenames:
                file_id=mdb.get_file_id(filename)
                if file_id == -2 :
                    unprocessed_files.append(filename)
        mdb.close()
        for filename in unprocessed_files:
            process(filename, config.deamon['log_path'])
            #break

        time.sleep(60)

if __name__ == '__main__':
    main_loop()

