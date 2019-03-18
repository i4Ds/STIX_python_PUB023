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


    def debug(self, msg):
        pprint(msg)

LOGGER = stix_logger()
