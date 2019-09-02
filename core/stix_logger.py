#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_logger.py
# @description  : logger

import pprint
import sys


class StixLogger:
    def __init__(self, filename=None, verbose=10):
        self.logfile = None
        self.signal_info = None
        self.signal_warn = None
        self.signal_error = None
        self.signal_enabled = False
        self.filename = filename
        self.set_logger(filename, verbose)

    def set_signal(self, sig_info, sig_warn, sig_error):
        self.signal_info = sig_info
        self.signal_warn = sig_warn
        self.signal_error = sig_error
        self.signal_enabled = True

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
        elif self.logfile:
            self.logfile.write(msg + '\n')
        else:
            print(msg)

    def error(self, msg):
        self.printf(('[ERROR  ] : {}'.format(msg)), 'error')

    def warn(self, msg):
        if self.verbose < 1:
            return
        self.printf(('[WARN   ] : {}'.format(msg)), 'warn')

    def info(self, msg):
        if self.verbose < 2:
            return
        if not self.signal_enabled:
            self.printf(('[INFO   ] : {}'.format(msg)), 'info')
        else:
            self.printf(msg, 'info')

    def pprint_parameters(self, parameters):
        if self.verbose < 3 or not parameters:
            return
        if type(parameters) is list:
            for par in parameters:
                if par:
                    try:
                        # for tree-like structure
                        eng= ''
                        if par['eng'] != par['raw']:
                            eng= par['eng']
                        self.printf(('{:<10} {:<30} {:<15} {:15}'.format(
                            par['name'], par['descr'], par['raw'], eng)))
                        if 'children' in par:
                            if par['children']:
                                self.pprint_parameters(par['children'])
                    except BaseException:
                        self.printf(par)
        elif type(parameters) is dict:
            self.printf(parameters)

    def debug(self, msg):
        if self.verbose < 4:
            return
        self.printf(msg)
    def parser_summary(self,summary):
         self.info(
                    'Total number of packets: {} ('
                    'TM: {}, TC:{}), bad bytes: {}, bad headers: {} .'.format(
                        summary['TM'] +
                        summary['TC'],
                        summary['TM'],
                        summary['TC'], summary['bad_bytes'], 
                        summary['bad_headers']))
_stix_logger = StixLogger()
