#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_logger.py
# @description  : logger
# @author       : Hualin Xiao
# @date         : Feb. 27, 2019

from pprint import pprint
import xlwt

class stix_logger:
    def __init__(self, path=None, level=10):
        self.path = path
        self.level=level
    def set_level(level):
        self.level=level


    def error(self,  msg, description=''):
        if description:
            print('[ERROR  ] {0}: {1}'.format(msg, description))
        else:
            print('[ERROR  ] : {}'.format(msg))

    def warning(self, msg, description=''):
        if self.level < 1:
            return 
        if description:
            print('[WARNING] {0}: {1}'.format(msg, description))
        else:
            print('[WARNING] : {}'.format(msg))

    def info(self,  msg, description=''):
        if self.level < 2:
            return 

        if description:
            print('[INFO   ] {0}: {1}'.format(msg, description))
        else:
            print('[INFO   ] : {}'.format(msg))
    def pprint_parameters(self,parameters):
        if self.level< 3 or not parameters:
            return
        if type(parameters) is list:
            for par in parameters:
                if par:
                    try:
                        #for tree-like structure 
                        value=''
                        if par['value']!=par['raw']:
                            value=par['value']
                        print('{:<10} {:<30} {:<15} {:15}'.format(par['name'],par['descr'],par['raw'],value))
                        if 'child' in par:
                            if par['child']:
                                self.pprint_parameters(par['child'])
                    except:
                        print(par)
        elif type(parameters) is dict:
            for key, val in parameters.items():
                if len(val) <50:
                    print('%s : %s'%(key, str(val)))
                else:
                    print(key)
                    print(val[0:50])

        else:
            pprint(par)



    def pprint(self,header, parameters):
        if self.level<3:
            return 
        print('*'*80)
        print('packet id      : {}'.format(header['packet_id']))
        print('Description    : {}'.format(header['DESCR']))
        print('Timestamp      : {}'.format(header['time']))
        print('SPID           : {}'.format(header['SPID']))
        print('segmentation   : {}'.format(header['segmentation']))
        print('service type   : {}'.format(header['service_type']))
        print('service subtype: {}'.format(header['service_subtype']))
        print('data length    : {}'.format(header['data_length']))
        print('APID           : {}'.format(header['APID']))
        print('-'*70)
        print('{:<10} {:<30} {:<15} {:15}'.format('name','descr','raw','eng_value'))
        print('-'*70)
        self.pprint_parameters(parameters)
        print('*'*80)



    def debug(self, msg):
        if self.level <4 :
            return 
        pprint(msg)

LOGGER = stix_logger()
