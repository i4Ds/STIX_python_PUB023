#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : stix_parameter.py
# @date         : Feb. 11, 2019
# @description:
#               definitions of structures of decoded parameters

#from core import idb

#PARAMETER_NODE_TYPE = 'dict'
#PARAMETER_NODE_TYPE = 'tuple'
"""
Output parameters store in tuples or dictionaries
storing in tuples could save system memory
"""
_stix_idb = idb._stix_idb
class StixParameterNode:
    """ define decoded parameter structure """

    def __init__(self,
                 name='',
                 raw='',
                 eng='',
                 children=None,
                 node_type=PARAMETER_NODE_TYPE):
        self._name = name
        self._raw = raw
        self._eng = eng
        self._children = []
        if children:
            self._children = children
        self._node_type = node_type

    def set_node_type(self, node_type):
        """can be dictionary or tuple"""
        self._node_type = node_type

    def get_node_type(self):
        return self._node_type

    def get(self, item=None):
        if item == 'name':
            return self._name
        elif item == 'raw':
            return self._raw
        elif item == 'eng':
            return self._eng
        elif item == 'children':
            return self._children
        elif item == 'desc':
            return _stix_idb.get_PCF_description(param_name)
        else:
            return self.get_node(self._node_type)

    def get_node(self, node_type):
        if node_type == 'tuple':
            return (self._name, self._raw, self._eng, self._children)
        else:
            return {
                'name': self._name,
                'raw': self._raw,
                'eng': self._eng,
                'children': self._children
            }

    def isa(self, name):
        if self._name == name:
            return True
        else:
            return False

    def from_node(self, node):
        if type(node) is dict:
            self._name = node['name']
            self._raw = node['raw']
            self._eng = node['eng']
            self._children = node['children']
        elif type(node) is tuple:
            self._name = node[0]
            self._raw = node[1]
            self._eng = node[2]
            self._children = node[3]

    def to_dict(self, node=None):
        self.from_node(node)
        return get_node('dict')

    def to_tuple(self, node=None):
        self.from_node(node)
        return get_node('tuple')

    def set_children(self, children=[]):
        self._children[:] = children

    @property
    def name(self):
        return self._name

    @property
    def raw(self):
        return self._raw

    @property
    def eng(self):
        return self._eng

    @property
    def children(self):
        return self._children

    @property
    def desc(self):
        if self._name:
            return _stix_idb.get_PCF_description(self._name)
        else:
            return ''

    @property
    def node(self):
        return self.get_node(self._node_type)


class StixParameterTree:
    """not used at the moment"""
    def __init__(self, parameters=None):
        self._parameters = []
        if parameters:
            self._parameters = parameters

    def insert(self, parameter):
        if type(parameter) is list:
            self._parameters.extend(parameter)
        else:
            self._parameters.append(parameter)

    def get_parameters(self):
        return self._parameters

    @property
    def parameters(self):
        return self._parameters

    def find(self, name, parameters=0):
        results = []
        if parameters == 0:
            parameters = self._parameters
        for param in parameters:
            param_node = StixParameterNode()
            param_node.from_node(param)
            if param_node.name == name:
                results.append(param_node.node)
            if param_node.children:
                children = self.find(name, param_node.children)
                if children:
                    results.extend(children)
        return results

    def get_raw(self, name, parameters=0):
        results = []
        if parameters == 0:
            parameters = self._parameters
        for param in parameters:
            param_node = StixParameterNode()
            param_node.from_node(param)
            if param_node.name == name:
                results.extend(param_node.get('raw')[0])
            if param_node.children:
                children = self.get_raw(name, param_node.chidren)
                if children:
                    results.extend(children)
        return results

    def get_eng(self, name, parameters=0):
        results = []
        if parameters == 0:
            parameters = self._parameters
        for param in parameters:
            param_node = StixParameterNode()
            param_node.from_node(param)
            if param_node.name == name:
                results.extend(param_node.eng)
            if param_node.children:
                children = self.get_raw(name, param_node.chidren)
                if children:
                    results.extend(children)
        return results

    def get_children(self, name, parameters=0):
        results = []
        if parameters == 0:
            parameters = self._parameters
        for param in parameters:
            param_node = StixParameterNode()
            param_node.from_node(param)
            if param_node.name == name:
                results.append(param_node.chidren)
            if param_node.children:
                children = self.get_children(name, param_node.chidren)
                if children:
                    results.append(children)
        return results
