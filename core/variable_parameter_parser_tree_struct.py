#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @title        : node.py
# @description  : variable packet parameters parser
#                 Information provided in IDB PCF and VP is used
# @author       : Hualin Xiao
# @date         : Feb. 28, 2019

from __future__ import (absolute_import, unicode_literals)
from pprint import pprint
import json
from core import stix_parser
from core import stix_global
from core import idb
from stix_io import stix_logger

STIX_IDB = idb.STIX_IDB
LOGGER = stix_logger.LOGGER
class variable_parameter_parser:
    """
    Variable parameter parser
    """
    def __init__(self, data, spid):
        """
        Args:
            data         :  binary data stream to be decoded
            vp_structures: variable data structure descriptions
        """
        self.root = None
        self.source_data = data
        self.spid = spid

        self.nodes = []
        self.results = []
        self.num_nodes = 0
        self.nodes.append(
            self.create_node('top', 0, 0, 0, stix_global.MAX_PARAMETERS, None,
                             1))
        self.current_offset = 0
        self.last_offset = 0
        self.current_offset_bit = 0
        self.length_min = 0
    def reset(self):
        self.nodes[0]['child']=[]
        self.current_offset = 0
        self.last_offset = 0
        self.current_offset_bit = 0
        self.length_min = 0

    def get_parameters(self):
        self.preprocess()
        packet_length = len(self.source_data)

        if self.length_min > packet_length:
            LOGGER.error(
                'The packet length ({}) is less than the required minimal length {}'
                .format(packet_length, self.length_min))
            LOGGER.error('Data Field not parsed!')
            return 0, None
        self.walk(self.nodes[0], self.results)
        return self.current_offset, self.results

    def create_node(self,
                    name,
                    position,
                    width,
                    offset_bit,
                    repeat_size,
                    parameter,
                    counter=0,
                    desc='',
                    child=[]):
        node = {
            'name': name,
            'offset_bit': offset_bit,
            'position': position,
            'repeat_size': repeat_size,
            'counter': counter,
            #'width': width,
            'parameter': parameter,
            'ID': self.num_nodes,
            'child': child,
            #'desc': desc
        }
        self.num_nodes += 1
        return node

    def register_parameter(self,
                           mother,
                           name,
                           position,
                           width,
                           offset_bit,
                           repeat_size,
                           parameter,
                           counter,
                           desc='',
                           child=[]):
        node = self.create_node(name, position, width, offset_bit, repeat_size,
                                parameter, counter, desc, child)
        if width % 8 == 0:
            self.length_min += width / 8
        mother['child'].append(node)
        return node

    def preprocess(self):
        self.reset()
        self.structures = STIX_IDB.get_variable_packet_structure(self.spid)
        mother = self.nodes[0]
        repeater = [{'node': mother, 'counter': stix_global.MAX_PARAMETERS}]
        #counter:  number of repeated times

        for par in self.structures:
            if repeater:
                for e in reversed(repeater):
                    e['counter'] -= 1
                    if e['counter'] < 0:
                        repeater.pop()
            mother = repeater[-1]['node']
            node = self.register_parameter(
                mother, par['PCF_NAME'], par['VPD_POS'], par['PCF_WIDTH'],
                par['VPD_OFFSET'], par['VPD_GRPSIZE'], par, 0,
                par['PCF_DESCR'], [])

            rpsize = par['VPD_GRPSIZE']
            if rpsize > 0:
                mother = node
                repeater.append({'node': node, 'counter': rpsize})

    def walk(self, mother, para):
        if not mother:
            return
        result_node = None
        counter = mother['counter']
        for i in range(0, counter):
            for node in mother['child']:
                if not node or self.current_offset > len(self.source_data):
                    return
                result = self.parse_parameter(node)
                result_node = {
                    'name': node['name'],
                    'raw': result['raw'],
                    'value': result['value'],
                    'eng_value_type': result['eng_value_type'],
                    'descr': result['descr'],
                    'child': []
                }
                if node['child']:
                    node['counter'] = result['raw'][0]
                    self.walk(node, result_node['child'])
                para.append(result_node)

    def parse_parameter(self, node):
        """
        parse a parameter. 
        The offset, offset bit and parameter name are described in 'node'
        """
        par = node['parameter']
        width = par['PCF_WIDTH']
        vpd_offset = par['VPD_OFFSET']
        if width % 8 != 0:
            if vpd_offset < 0:
                self.current_offset_bit = self.last_data_width + vpd_offset
            else:
                self.current_offset_bit += self.last_bit_width + vpd_offset
            self.last_bit_width = width
        elif width % 8 == 0:
            self.current_offset_bit = 0
            self.last_offset = self.current_offset
            self.current_offset += width / 8
            self.last_bit_width = 0
            self.last_data_width = width

        par['offset'] = self.last_offset
        par['offset_bit'] = self.current_offset_bit
        #print('###{},{}, {},{}'.format(par['PCF_NAME'],self.last_offset,self.current_offset_bit,width))
        parameter = stix_parser.interpret_telemetry_parameter(
            self.source_data, par)
        return parameter


def test():
    t = variable_parameter_parser('', 54121)
    t.preprocess()
    pprint(t.nodes)
    #t.walk(t.nodes[0])


if __name__ == '__main__':
    test()
