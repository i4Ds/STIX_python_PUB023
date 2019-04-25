#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_writer.py
# @description  : Write decoded parameters to a python pickle file
#                 see https://docs.python.org/2/library/pickle.html for descriptions of python pickle
#                 It can be further analyzed.
# @author       : Hualin Xiao
# @date         : Feb. 27, 2019
#import json
import pprint
#import pymongo
import pickle
import gzip
import datetime


class stix_writer:
    def __init__(self, filename):
        self.filename = filename
        self.packet_counter = 0
        self.fout=None
        self.packets=[]

        self.fout=gzip.open(filename,'wb')

    def register_run(self,in_filename):
        #not used
        run_info={'Run':
                    {'Input':in_filename,
                     'Output':,self.filename,
                     'date': datetime.datetime.now().isoformat()}
                }
        
        pickle.dump(run_info,self.fout)

    def write_header(self, header):

        """
        it is called for every telemetry data header
        """
        msg = [
            self.packet_counter, header['service_type'],
            header['service_subtype'], header['SPID'],header['SSID'], header['DESCR'],
            header['time'], header['coarse_time'], header['fine_time'],header['segmentation'],header['data_length']
        ]
        line=(','.join(map(str, msg)))
        self.packet_counter += 1
        #if self.fout:
        #    pp = pprint.PrettyPrinter(indent=4, stream=self.fout)
        #    pp.pprint(line)
    def write(self,header, parameters, parameter_desc=dict()):
        packet={'header':header, 'parameter':parameters, 
                'parameter_desc':parameter_desc}
        self.packets.append(packet)
    def done(self):
        pickle.dump(self.packets,self.fout)
        self.fout.close()


    def write_parameters(self, parameters,spid=0):
        pprint.pprint(parameters)
