#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : stix_parameter.py
# @date         : Feb. 11, 2019
# @description:
#               definitions of structures of decoded parameters

from core import idb
PARAMETER_NODE_TYPE='dict'
_stix_idb = idb._stix_idb
class StixParameterNode:
    """ define decoded parameter structure """
    def __init__(self, name='', raw='', eng='', children=None, node_type=PARAMETER_NODE_TYPE):
        self._name=name
        self._raw=raw
        self._eng=eng
        self._children=[]
        if children:
            self.children=children
        self._node_type=node_type
        
    def set_node_type(self,node_type):
        """can be dictionary or tuple"""
        self._node_type=node_type
    
    def get_node_type(self):
        return self._node_type

    def get(self,item=None):
        if item =='name':
            return self._name
        elif item =='raw':
            return self._raw
        elif item =='eng':
            return self._eng
        elif item=='children':
            return self._children
        elif item=='desc':
            return _stix_idb.get_PCF_description(param_name)
        else:
            return self.get_node(self._node_type)

    def get_node(self, node_type):
        if node_type=='tuple':
            return (self._name, self._raw,self._eng, self._children)
        else:
            return {'name':self._name, 'raw':self._raw,'eng':self._eng, 
                    'children':self._children}

    def set(self,node):
        if type(node) is dict:
            self._name=node['name']
            self._raw=node['raw']
            self._eng=node['eng']
            self._children=node['children']
        elif type(node) is tuple:
            self._name=node[0]
            self._raw=node[1]
            self._eng=node[2]
            self._children=node[3]
    def to_dict(self,node=None):
        self.set(node)
        return get_node('dict')

    def to_tuple(self,node=None):
        self.set(node)
        return get_node('tuple')
    def set_children(self,children=[]):
        self._children[:]=children
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
    def __init__(self):
        pass
    def append(self,parameter):
        pass


