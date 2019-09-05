#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_writer.py
# @description  : Write decoded data to a python pickle file, sqlite database or mongo database
# @author       : Hualin Xiao
# @date         : Feb. 27, 2019
import pprint
import pickle
import gzip
import pymongo
import datetime
import os
from core import stix_logger
STIX_LOGGER= stix_logger.stix_logger()


class StixPickleWriter(object):
    def __init__(self, filename):
        self.filename = filename
        self.packet_counter = 0
        self.fout = None
        self.packets = []
        if filename.endswith('.pklz'):
            self.fout = gzip.open(filename, 'wb')
        else:
            self.fout = open(filename, 'wb')

    def register_run(self, in_filename, filesize=0, comment=''):
        self.run = {
            'Input': in_filename,
            'Output': self.filename,
            'filsize': filesize,
            'comment': comment,
            'Date': datetime.datetime.now().isoformat()
        }

    def write_one(self, packet):
        pass

    def write_all(self, packets):
        if self.fout:
            data = {'run': self.run, 'packet': packets}
            pickle.dump(data, self.fout)
            self.fout.close()


class StixBinaryWriter(object):
    def __init__(self, filename):
        self.filename = filename
        self.packet_counter = 0
        self.fout = None
        self.packets = []
        self.num_success = 0
        try:
            self.fout = open(self.filename, 'wb')
        except IOError:
            STIX_LOGGER.error(
                'IO error. Can not create file:{}'.format(filename))

    def register_run(self, in_filename, filesize=0, comment=''):
        pass
        #not write them to binary file
    def get_num_sucess(self):
        return self.num_success

    def write_one(self, packet):
        if self.fout:
            try:
                raw = packet['bin']
                self.fout.write(raw)
                self.num_success += 1
            except KeyError:
                STIX_LOGGER.warn('binary data not available')

    def write_all(self, packets):
        if self.fout:
            for packet in packets:
                self.write_one(packet)


class StixMongoWriter(object):
    """write data to   MongoDB"""

    def __init__(self,
                 server='localhost',
                 port=27017,
                 username='',
                 password=''):

        self.packets = []
        self.db = None
        self.collection_packets = None
        self.collection_runs = None
        self.current_run_id = 0
        self.current_header_id = 0
        self.start = -1
        self.end = -1
        try:
            self.connect = pymongo.MongoClient(
                server, port, username=username, password=password)
            self.db = self.connect["stix"]

            self.collection_packets = self.db['packets']
            self.collection_headers = self.db['headers']
            self.collection_runs = self.db['runs']
            self.create_indexes()
        except Exception as e:
            raise e
            print('can not connect to mongodb')

    def create_indexes(self):
        """to speed up queries """
        if self.collection_headers:
            if self.collection_headers.count() == 0:
                self.collection_headers.create_index([('time', -1),
                                                      ('SPID', -1),
                                                      ('service_type', -1),
                                                      ('service_subtype', -1),
                                                      ('run_id', -1)],
                                                     unique=False)

        if self.collection_runs:
            if self.collection_runs.count() == 0:
                self.collection_runs.create_index([('file', -1), ('date', -1)],
                                                  unique=False)

        if self.collection_packets:
            if self.collection_packets.count() == 0:
                self.collection_packets.create_index([('header.time', -1),
                                                      ('header_id', -1),
                                                      ('run_id', -1)],
                                                     unique=False)

    def register_run(self, in_filename, filesize=0, comment=''):
        try:
            self.current_run_id = self.collection_runs.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_run_id = 0
            # first entry
        try:
            self.current_header_id = self.collection_headers.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_header_id = 0

        try:
            self.current_packet_id = self.collection_packets.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_packet_id = 0

        log_filename = STIX_LOGGER.get_log_filename()
        self.run_info = {
            'filename': os.path.basename(in_filename),
            'path': os.path.dirname(in_filename),
            'comment': comment,
            'log': log_filename,
            'date': datetime.datetime.now().isoformat(),
            'filesize': filesize
        }

    def write_all(self, packets):
        if self.db and packets:
            self.run_info['start'] = packets[0]['header']['time']
            self.run_info['end'] = packets[-1]['header']['time']
            self.run_info['_id'] = self.current_run_id
            run_id = self.collection_runs.insert_one(self.run_info).inserted_id
            for packet in packets:
                header = packet['header']
                parameters = packet['parameters']

                header['run_id'] = run_id
                header['_id'] = self.current_header_id
                header_id = self.collection_headers.insert_one(
                    header).inserted_id
                self.current_header_id += 1

                packet['header_id'] = header_id
                packet['run_id'] = self.current_run_id
                packet['_id'] = self.current_packet_id
                result = self.collection_packets.insert_one(packet)
                self.current_packet_id += 1

    def write_one(self, packet):
        pass
