#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_writer.py
# @description  : Write decoded data to a python pickle file, sqlite database or mongo database
# @author       : Hualin Xiao
# @date         : Feb. 27, 2019
import os
import datetime
import pickle
import gzip
import pymongo
import time
from core import stix_logger
from core import stix_global
from core import stix_packet_analyzer 
from core import stix_datetime
STIX_LOGGER = stix_logger.stix_logger()

analyzer = stix_packet_analyzer.analyzer()

class StixPacketWriter(object):
    def __init__(self):
        pass

    def write_all(self, packets):
        pass

    def write_one(self, packet):
        pass

    def set_filename(self, fname):
        pass

    def set_summary(self, summary):
        pass

    def close(self):
        pass


class StixPickleWriter(StixPacketWriter):
    def __init__(self, filename):
        super(StixPickleWriter, self).__init__()
        self.filename = filename
        self.packet_counter = 0
        self.fout = None
        self.packets = []
        self.run = None
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
    def write_all(self, packets):
        if self.fout:
            data = {'run': self.run, 'packet': packets}
            pickle.dump(data, self.fout)
            self.fout.close()

    def write_one(self, packet):
        self.packets.append(packet)

    def close(self):
        self.write_all(self.packets)


class StixBinaryWriter(StixPacketWriter):
    def __init__(self, filename):
        super(StixBinaryWriter, self).__init__()
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

    def close(self):
        if self.fout:
            self.fout.close()


class StixMongoDBWriter(StixPacketWriter):
    """write data to   MongoDB"""

    def __init__(self,
                 server='localhost',
                 port=27017,
                 username='',
                 password=''):
        super(StixMongoDBWriter, self).__init__()

        self.ipacket = 0
        self.packets = []
        self.start_time = 0
        self.end_time = 0
        self.db = None
        self.filename = ''
        self.path = ''
        self.summary = ''
        self.collection_packets = None
        self.current_packet_id = 0
        self.collection_runs = None
        self.current_run_id = 0
        self.calibration_info=None

        self.current_calibration_run_id = 0

        self.start = -1
        self.end = -1
        self.run_info = None
        try:
            self.connect = pymongo.MongoClient(
                server, port, username=username, password=password)
            self.db = self.connect["stix"]

            self.collection_packets = self.db['packets']
            self.collection_runs = self.db['processing_runs']
            self.collection_calibration = self.db['calibration_runs']
            self.create_indexes()
        except Exception as e:
            STIX_LOGGER.error(str(e))

    def create_indexes(self):
        """to speed up queries """
        if self.collection_runs:
            if self.collection_runs.count() == 0:
                indexes=['file','date']
                for index in indexes:
                    self.collection_runs.create_index(indexes)

        if self.collection_packets:
            if self.collection_packets.count() == 0:
                indexes=['header.unix_time','header.SPID','header.service_type',
                        'header.service_subtype','run_id','TMTC']
                for index in indexes:
                    self.collection_packets.create_index(index)

    def register_run(self, in_filename, filesize=0, comment=''):
        try:
            self.current_run_id = self.collection_runs.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_run_id = 0
            # first entry

        try:
            self.current_packet_id = self.collection_packets.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_packet_id = 0

        try:
            self.current_calibration_run_id = self.collection_calibration.find(
            ).sort('_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_calibration_run_id = 0

        log_filename = STIX_LOGGER.get_log_filename()

        self.filename = os.path.basename(in_filename)
        self.path = os.path.dirname(in_filename)

        self.run_info = {
            'filename': self.filename,
            'path': self.path,
            'comment': comment,
            'log': log_filename,
            'date': datetime.datetime.now(),
            'run_start_unix_time': time.time(),
            'run_stop_unix_time': 0,
            'data_start_unix_time': 0,
            'data_stop_unix_time': 0,
            '_id': self.current_run_id,
            'status': stix_global.UNKNOWN,
            'summary': '',
            'filesize': filesize
        }
        #print(self.run_info)
        self.inserted_run_id = self.collection_runs.insert_one(
            self.run_info).inserted_id

    def set_filename(self, fname):
        self.filename = os.path.basename(fname)
        self.path = os.path.dirname(fname)

    def set_summary(self, summary):
        self.summary = summary

    def write_all(self, packets):
        for packet in packets:
            self.write_one(packets)

    def write_one(self, packet):

        if self.ipacket == 0:
            self.start_time = packet['header']['unix_time']
        self.end_time = packet['header']['unix_time']
        #insert header

        packet['run_id'] = self.current_run_id
        packet['_id'] = self.current_packet_id
        self.capture_calibration(packet)

        try:
            self.collection_packets.insert_one(packet)
        except Exception as e:
            STIX_LOGGER.error(
                'Error occurred when inserting packet to MongoDB')
            STIX_LOGGER.error(str(e))
            STIX_LOGGER.info('Packet:' + str(header))
            raise
            return


        self.current_packet_id += 1
        self.ipacket += 1

    def close(self):
        #it has to be called at the end

        if not self.collection_runs:
            STIX_LOGGER.warn('MongoDB was not initialized ')
            return
        STIX_LOGGER.info('{} packets have been inserted into MongoDB'.format(
            self.ipacket))
        STIX_LOGGER.info('Updating run :'.format(self.inserted_run_id))
        run = self.collection_runs.find_one({'_id': self.inserted_run_id})
        if run:
            run['data_start_unix_time'] = self.start_time
            run['data_stop_unix_time'] = self.end_time
            run['run_stop_unix_time'] = time.time()
            run['filename'] = self.filename
            run['path'] = self.path
            run['status'] = stix_global.OK
            #status ==1 if success  0
            run['summary'] = self.summary
            self.collection_runs.save(run)
            STIX_LOGGER.info(str(run))
            STIX_LOGGER.info('Run info updated successfully.')
        else:
            STIX_LOGGER.error('Run info not updated.')


    def capture_calibration(self, packet):
        if not self.collection_calibration:
            return 
        header=packet['header']
        if header['SPID'] != 54124:
            return
        if header['seg_flag'] in [1,3]:
            self.calibration_info={
                    'run_id':self.current_run_id,
                    'packet_ids':[self.current_packet_id],
                    'header_unix_time':header['unix_time'],
                    '_id':self.current_calibration_run_id 
                    }
        elif header['seg_flag'] == 0 :
            if not self.calibration_info:
                STIX_LOGGER.warn('The first calibration report is missing!')
            else:
                self.calibration_info['packet_ids'].append(self.current_packet_id)

        if header['seg_flag'] in [2,3]:
            #last or single packet
            analyzer.load(packet)
            param_dict=analyzer.to_dict()
            self.calibration_info['duration']=param_dict['NIX00122'][0]
            scet=param_dict['NIX00445'][0]
            self.calibration_info['SCET']=scet
            self.calibration_info['start_unix_time']=stix_datetime.convert_SCET_to_unixtimestamp(scet)
            self.calibration_info['aux']=param_dict
            self.collection_calibration.insert_one(self.calibration_info)
            self.current_calibration_run_id += 1

            self.calibration_info=None
            

            

