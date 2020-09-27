#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : MongoDB.py
# @description  : Mongodb reader
# @author       : Hualin Xiao
# @date         : May. 12, 2019
#import json
import os
import pprint
import datetime
import uuid
import bson
import pymongo

NUM_MAX_PACKETS = 20000
MAX_REQUEST_LC_TIME_SPAN_DAYS = 3
QL_SPIDS = {
    'lc': 54118,
    'bkg': 54119,
    'qlspec': 54120,
    'var': 54121,
    'flare': 54122
}


class MongoDB(object):
    def __init__(self, server='localhost', port=27017, user='', pwd=''):
        self.filename = None
        self.packets = []
        self.db = None
        self.collection_packets = None
        self.collection_raw_files = None
        self.collection_calibration = None
        self.collection_ql = None
        try:
            if server == 'localhost' and user == '' and pwd == '':
                self.connect = pymongo.MongoClient(server, port)
            else:
                self.connect = pymongo.MongoClient(server,
                                                   port,
                                                   username=user,
                                                   password=pwd,
                                                   authSource='stix')
            self.db = self.connect["stix"]
            self.collection_packets = self.db['packets']
            self.collection_raw_files = self.db['raw_files']
            self.collection_calibration = self.db['calibration_runs']
            self.collection_ql = self.db['quick_look']
            self.collection_data_requests = self.db['bsd']
            self.collection_fits = self.db['fits']
            self.collection_events = self.db['events']
            self.collection_auto_flares = self.db['auto_flares']

        except Exception as e:
            print('Error occurred while initializing mongodb: {}'.format(
                str(e)))

    def get_db(self):
        return self.db

    def get_collection_calibration(self):
        return self.collection_calibration

    def get_collection_processing(self):
        return self.collection_raw_files

    def get_collection_packets(self):
        return self.collection_packets

    def is_connected(self):
        if self.db:
            return True
        else:
            return False

    def get_filename_of_run(self, run_id):
        if self.collection_raw_files:
            cursor = self.collection_raw_files.find({'_id': int(run_id)})
            for x in cursor:
                return x['filename']
        return ''

    def get_file_id(self, filename):

        if not self.collection_raw_files:
            return -1
        basename = os.path.basename(filename)
        abspath = os.path.abspath(filename)
        path = os.path.dirname(abspath)
        cursor = self.collection_raw_files.find({'filename': basename})
        #,'path':path})
        for x in cursor:
            return x['_id']

        return -2

    def select_packets_by_id(self, pid):
        if self.collection_packets:
            cursor = self.collection_packets.find({'_id': int(pid)})
            return cursor
        return []

    def delete_one_run(self, run_id):
        if self.collection_packets:
            cursor = self.collection_packets.delete_many(
                {'run_id': int(run_id)})

        if self.collection_raw_files:
            cursor = self.collection_raw_files.delete_many(
                {'_id': int(run_id)})

        if self.collection_calibration:
            cursor = self.collection_calibration.delete_many(
                {'run_id': int(run_id)})
        if self.collection_ql:
            cursor = self.collection_ql.delete_many({'run_id': int(run_id)})
        if self.collection_data_requests:
            cursor = self.collection_data_requests.delete_many(
                {'run_id': int(run_id)})
        if self.collection_auto_flares:
            cursor = self.collection_auto_flares.delete_many(
                {'run_id': int(run_id)})
        if self.collection_fits:
            cursor = self.collection_fits.delete_many({'file_id': int(run_id)})

    def delete_runs(self, runs):
        for run in runs:
            self.delete_one_run(run)

    '''
    def select_packets_by_run(self, run_id):
        if self.collection_packets:
            cursor = self.collection_packets.find({
                'run_id': int(run_id)
            }).sort('_id', 1)
            return list(cursor)
        return []
        '''

    def select_packets_by_run(self,
                              run_id,
                              SPIDs=[],
                              sort_field='_id',
                              order=1):
        if not isinstance(SPIDs, list):
            SPIDs = [SPIDs]
        pkts = []
        if self.collection_packets:
            query_string = {'run_id': int(run_id)}
            if SPIDs:
                query_string = {
                    '$and': [{
                        'run_id': int(run_id)
                    }, {
                        'header.SPID': {
                            '$in': SPIDs
                        }
                    }]
                }
            pkts = self.collection_packets.find(query_string).sort(
                sort_field, order)
        return pkts

    def close(self):
        if self.connect:
            self.connect.close()

    def select_all_runs(self, order=-1):
        if self.collection_raw_files:
            runs = self.collection_raw_files.find().sort('_id', order)
            return runs
        return None

    def set_run_ql_pdf(self, _id, pdf_filename):
        if self.collection_raw_files:
            run = self.collection_raw_files.find_one({'_id': _id})
            run['quicklook_pdf'] = pdf_filename
            self.collection_raw_files.save(run)

    def get_run_ql_pdf(self, _id):
        if self.collection_raw_files:
            run = self.collection_raw_files.find_one({'_id': _id})
            if 'quicklook_pdf' in run:
                return run['quicklook_pdf']
        return None

    def get_calibration_run_data(self, calibration_id):
        _id = int(calibration_id)
        rows = []
        if self.collection_calibration:
            rows = self.collection_calibration.find({'_id': _id})
        return rows

    def update_calibration_analysis_report(self, calibration_id, data):
        #save calibration data analysis results to mongodb
        _id = int(calibration_id)
        if self.collection_calibration:
            doc = self.collection_calibration.find_one({'_id': _id})
            doc['analysis_report'] = data
            self.collection_calibration.save(doc)

    def get_calibration_runs_for_processing(self):
        #search for calibration runs which have  not been yet processed
        docs = []
        try:
            docs = list(self.collection_calibration.find())
        except Exception as e:
            pass
        if docs:
            return [
                doc['_id'] for doc in docs if ('spectra' in doc) and (
                    'sbspec_formats' in doc) and 'analysis_report' not in doc
            ]
        return []

    def write_fits_index_info(self, doc):
        if self.collection_fits:
            self.collection_fits.save(doc)

    def get_next_fits_id(self):
        try:
            return self.collection_fits.find().sort('_id',
                                                    -1).limit(1)[0]['_id'] + 1
        except IndexError:
            return 0

    def get_next_auto_flare_id(self):
        try:
            return self.collection_auto_flares.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            return 0

    def write_flares(self, result):
        """
            write flare info into database
        """
        if 'run_id' not in result:
            return
        if result['num_peaks'] == 0:
            return

        try:
            cursor = self.collection_auto_flares.delete_many(
                {'run_id': int(result['run_id'])})
            #delete
        except Exception as e:
            pass

        if self.collection_auto_flares:
            first_id = self.get_next_auto_flare_id()

        for i in range(result['num_peaks']):
            doc = {
                '_id': first_id + i,
                'run_id': result['run_id'],
                'peak_counts': result['peak_counts'][i],
                'peak_utc': result['peak_utc'][i],
                'peak_unix_time': result['peak_unix_time'][i],
            }
            self.collection_auto_flares.save(doc)

    def get_quicklook_packets(self,
                              packet_type,
                              start_unix_time,
                              span,
                              sort_field='_id'):
        span = float(span)
        start_unix_time = float(start_unix_time)
        if span > 3600 * 24 * MAX_REQUEST_LC_TIME_SPAN_DAYS:  #max 3 days
            return []
        stop_unix_time = start_unix_time + span
        SPID = QL_SPIDS[packet_type]
        collection = self.collection_ql
        if not collection:
            return []
        query_string = {
            "$and": [{
                'stop_unix_time': {
                    '$gt': start_unix_time
                }
            }, {
                'start_unix_time': {
                    '$lt': stop_unix_time
                }
            }, {
                'SPID': SPID
            }]
        }
        ret = collection.find(query_string, {'packet_id': 1}).sort('_id', 1)
        packet_ids = [x['packet_id'] for x in ret]

        if packet_ids:
            query_string = {'_id': {'$in': packet_ids}}
            cursor = self.collection_packets.find(query_string).sort(
                sort_field, 1)
            return cursor
        return []

    def get_quicklook_packets_of_run(self, packet_type, run):
        collection = None
        SPID = QL_SPIDS[packet_type]
        query_string = {'run_id': run, 'header.SPID': SPID}
        cursor = self.collection_packets.find(query_string).sort('_id', 1)
        return cursor
        return []


#if __name__ == '__main__':
#    mdb = MongoDB()
#    #print(mdb.get_packet_for_header(318))
#    mdb.set_quicklook_pdf(0, '/data/a.pdf')
