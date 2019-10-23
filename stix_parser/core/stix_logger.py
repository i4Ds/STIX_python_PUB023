#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_logger.py
# @description  : logger

import sys
from datetime import datetime
import pprint


class StixLogger(object):
    __instance = None

    @staticmethod
    def get_instance(filename=None, verbose=4):
        if not StixLogger.__instance:
            StixLogger(filename, verbose)
        return StixLogger.__instance

    #singleton

    def __init__(self, filename=None, verbose=10):

        if StixLogger.__instance:
            raise Exception('Logger already initialized')
        else:
            StixLogger.__instance = self

        self.logfile = None
        self.signal_info = None
        self.signal_warn = None
        self.signal_error = None
        self.signal_enabled = False
        self.filename = filename
        self.set_logger(filename, verbose)

    def set_signal(self, sig_info, sig_important_info, sig_warn, sig_error):
        self.signal_info = sig_info
        self.signal_important_info = sig_important_info
        self.signal_warn = sig_warn
        self.signal_error = sig_error
        self.signal_enabled = True
    def get_now(self):
        now= datetime.now()
        return  now.strftime("%Y-%m-%d %H:%M:%S")

    def emit(self, msg):
        self.info(msg)

    def get_log_filename(self):
        return self.filename

    def set_logger(self, filename=None, verbose=3):
        if self.logfile:
            self.logfile.close()
            self.logfile = None
        self.filename = filename
        self.verbose = verbose
        if filename:
            try:
                self.logfile = open(filename, 'w+')
            except IOError:
                print('Can not open log file {}'.format(filename))

    def set_verbose(self, verbose):
        self.verbose = verbose

    def printf(self, msg, msg_type="info"):
        if self.signal_enabled:
            if msg_type == 'info':
                self.signal_info.emit(msg)
            elif msg_type == 'warn':
                self.signal_warn.emit(msg)
            elif msg_type == 'error':
                self.signal_error.emit(msg)
            elif msg_type == 'important':
                self.signal_important_info.emit(msg)
        elif self.logfile:
            self.logfile.write(msg + '\n')
        else:
            print(msg)

    def important_info(self, msg):
        self.printf(('[INFO {}] : {}'.format(self.get_now(), msg)), 'important')

    def error(self, msg):
        self.printf(('[ERROR {}] : {}'.format(self.get_now(),msg)), 'error')

    def warn(self, msg):
        if self.verbose < 1:
            return
        self.printf(('[WARN {}] : {}'.format(self.get_now(),msg)), 'warn')

    def info(self, msg):
        if self.verbose < 2:
            return
        if not self.signal_enabled:
            self.printf(('[INFO {}] : {}'.format(self.get_now(),msg)), 'info')
        else:
            self.printf(msg, 'info')

    def pprint(self, parameter):
        if self.verbose > 5:
            pprint.pprint(parameter)

    def pprint_parameters(self, parameters):
        if self.verbose < 3 or not parameters:
            return
        if isinstance(parameters, list):
            for par in parameters:
                if par:
                    try:
                        # for tree-like structure
                        eng = ''
                        if par['eng'] != par['raw']:
                            eng = par['eng']
                        self.printf(('{:<10} {:<30} {:<15} {:15}'.format(
                            par['name'], par['descr'], par['raw'], eng)))
                        if 'children' in par:
                            if par['children']:
                                self.pprint_parameters(par['children'])
                    except BaseException:
                        self.printf(par)
        else:
            self.printf(parameters)

    def debug(self, msg):
        if self.verbose < 4:
            return
        self.printf(msg)

    def print_summary(self, summary):
        self.important_info(
            'Size: {} bytes (bad:{});'
            ' Nb. of packets: {} ('
            'TM: {}, TC:{}, Filtered: {}); Parsed {} (TM:{},TC:{}); Bad headers:{} .'
            .format(
                summary['total_length'], summary['num_bad_bytes'],
                summary['num_tm'] + summary['num_tc'] +
                summary['num_filtered'], summary['num_tm'], summary['num_tc'],
                summary['num_filtered'],
                summary['num_tm_parsed'] + summary['num_tc_parsed'],
                summary['num_tm_parsed'], summary['num_tc_parsed'],
                summary['num_bad_headers']))


def stix_logger():
    return StixLogger.get_instance()
