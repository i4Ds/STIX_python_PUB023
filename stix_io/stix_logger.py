#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_logger.py
# @description  : logger
# @author       : Hualin Xiao
# @date         : Feb. 27, 2019

from pprint import pprint


class stix_logger:
    def __init__(self, path=None):
        self.path = path


    def error(self,  msg, description=''):
        if description:
            print('[ERROR  ] {0}: {1}'.format(msg, description))
        else:
            print('[ERROR  ] : {}'.format(msg))


    def warning(self, msg, description=''):
        if description:
            print('[WARNING] {0}: {1}'.format(msg, description))
        else:
            print('[WARNING] : {}'.format(msg))

    def info(self,  msg, description=''):
        if description:
            print('[INFO   ] {0}: {1}'.format(msg, description))
        else:
            print('[INFO   ] : {}'.format(msg))
    def pprint_parameters(self,parameters):
        if not parameters:
            return 
        for par in parameters:
            if par:
                value=''
                if par['value']!=par['raw']:
                    value=par['value']
                print('{:<10} {:<30} {:<15} {:15}'.format(par['name'],par['descr'],par['raw'],value))
                if 'child' in par:
                    if par['child']:
                        self.pprint_parameters(par['child'])


    def pprint(self,header, parameters):
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
        pprint(msg)

LOGGER = stix_logger()
