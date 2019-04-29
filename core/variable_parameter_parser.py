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
class variable_parameter_parser:
    """
    Variable parameter parser
    """
    def __init__(self, data, spid,output_type='tree',logger=None):
        """
        Args:
            data         :  binary data stream to be decoded
            vp_structures: variable data structure descriptions
        """
        self.root = None
        self.source_data = data
        self.spid = spid
        self.logger=logger

        self.nodes = []
        self.results_tree = []
        self.num_nodes = 0
        self.nodes.append(
            self.create_node('top', 0, 0, 0, stix_global.MAX_PARAMETERS, None,
                             1))
        self.current_offset = 0
        self.last_offset = 0
        self.current_offset_bit = 0
        self.length_min = 0
        self.output_type =output_type
        self.results_dict={}
        self.parameter_desc={}
    def reset(self):
        self.nodes[0]['child']=[]
        self.results_tree[:]=[]
        self.results_dict.clear()
        self.parameter_desc.clear()
        self.current_offset = 0
        self.last_offset = 0
        self.current_offset_bit = 0
        self.length_min = 0
        

    def get_parameters(self):
        self.build_tree()
        packet_length = len(self.source_data)
        if self.length_min > packet_length:
            self.logger.error(
                'The packet length ({}) is less than the required minimal length {}'
                .format(packet_length, self.length_min))
            self.logger.error('Data Field not parsed!')
            return 0, None
        if self.output_type=='tree':
            self.walk_to_tree(self.nodes[0], self.results_tree)
            return self.current_offset, self.results_tree
        else:
            self.walk_to_array(self.nodes[0])
            return self.current_offset, self.results_dict


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
    def get_parameter_description(self):
        return self.parameter_desc
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
    def build_tree(self):
        """
        To build a parameter tree 
        """
        self.reset()
        self.structures = STIX_IDB.get_variable_packet_structure(self.spid)

        mother = self.nodes[0]
        repeater = [{'node': mother, 'counter': stix_global.MAX_PARAMETERS}]
        #counter:  number of repeated times

        for par in self.structures:
            self.parameter_desc[par['PCF_NAME']]=par['PCF_DESCR']
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




    def pprint_par(self,st):
        if debug:
            print(('%s %s  %s %s %s %s %s %s\n')%(str(st['VPD_POS']), st['VPD_NAME'], st['VPD_GRPSIZE'], 
                st['VPD_OFFSET'],  str(st['PCF_WIDTH']),str(st['offset']),str(st['offset_bit']), st['PCF_DESCR']))

    def pprint_structure(self,structures):
        if debug:
            pprint(structures)
            for st in structures:
                print(('%s %s  %s %s %s %s\n')%(str(st['VPD_POS']), st['VPD_NAME'], st['VPD_GRPSIZE'], 
                    st['VPD_OFFSET'],  str(st['PCF_WIDTH']), st['PCF_DESCR']))

    def walk_to_array(self, mother):
        """
        Parameter tree traversal
        """
        if not mother:
            return
        result_node = None
        counter = mother['counter']
        parameter_values={}
        for i in range(0, counter):
            for node in mother['child']:
                if not node or self.current_offset > len(self.source_data):
                    return None
                result = self.parse_parameter(node)
                value=result['raw'][0]
                name=node['name']
                #append parameter to the output list
                if name in self.results_dict:
                    self.results_dict[name].append(value)
                else:
                    self.results_dict[name]=[value]

                if node['child']:
                    node['counter'] = value
                    #number of repeated times
                    self.walk_to_array(node)

    def walk_to_tree(self, mother, para):
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
                    #'eng_value_type': result['eng_value_type'],
                    'descr': result['descr'],
                    'child': []
                }
                if node['child']:
                    node['counter'] = result['raw'][0]
                    self.walk_to_tree(node, result_node['child'])
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
                self.current_offset_bit += self.last_num_bits + vpd_offset
            self.last_num_bits = width
        elif width % 8 == 0:
            self.current_offset_bit = 0
            self.last_offset = self.current_offset
            self.current_offset += width / 8
            self.last_num_bits = 0
            self.last_data_width = width

        par['offset'] = self.last_offset
        par['offset_bit'] = self.current_offset_bit

        #print('###{},{}, {},{}'.format(par['PCF_NAME'],self.last_offset,self.current_offset_bit,width))

        parameter_interpret=False
        if self.output_type == 'tree':
            parameter_interpret=True
            #not to interpret a raw value to physical value

        return stix_parser.interpret_telemetry_parameter(
            self.source_data, par, parameter_interpret)
def test():
    t = variable_parameter_parser('', 54121)
    t.build_tree()
    pprint(t.nodes)
    #t.walk(t.nodes[0])
if __name__ == '__main__':
    test()
