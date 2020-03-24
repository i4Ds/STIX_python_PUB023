#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : stix_parameter.py
# @date         : Feb. 11, 2019
# @description:
#               definitions of structures of decoded parameters
from . import stix_idb
STIX_IDB = stix_idb.stix_idb()


class StixParameter(object):
    """ define decoded parameter structure """

    __parameter_foramt = 'tuple'
    __decompressor = None

    def __init__(self, name='', raw='', eng='', children=None):
        #param_format can be tuple or dict
        self._name = name
        self._raw = raw
        self._eng = eng
        self._children = []
        self._parameter=None

        if children:
            self._children = children

    @classmethod
    def set_format(cls, fmt):
        """can be dictionary or tuple"""
        if fmt in ('tuple', 'dict'):
            cls.__parameter_foramt = fmt
        else:
            raise Exception(
                'Invalid parameter format {}, can be only tuple or dict'.
                format(fmt))

    @classmethod
    def set_decompressor(cls, instance):
        cls.__decompressor = instance

    def get_raw_int(self):
        try:
            return int(self._raw[0])
        except (TypeError, IndexError, ValueError):
            return None

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
            return STIX_IDB.get_parameter_description(self._name)
        return self.get_parameter()

    def get_parameter(self, param_format=None):
        if not param_format:
            param_format = StixParameter.__parameter_foramt

        if not self._eng and StixParameter.__decompressor:
            if StixParameter.__decompressor.is_compressed():
                raw_int = self.get_raw_int()
                if raw_int is not None:
                    ret = StixParameter.__decompressor.get_decompressed_value(
                        self._name, raw_int)
                    if ret is not None:
                        self._eng = ret

        if param_format == 'tuple':
            return (self._name, self._raw, self._eng, self._children)
        return {
            'name': self._name,
            'raw': self._raw,
            'eng': self._eng,
            'desc': self.desc,
            'children': self._children
        }

    def isa(self, name):
        return self._name == name

    def clone(self, parameter):
        self._parameter=parameter
        #useful for setting children
        if isinstance(parameter, dict):
            self._name = parameter['name']
            self._raw = parameter['raw']
            self._eng = parameter['eng']
            self._children = parameter['children']
        elif isinstance(parameter, (tuple, list)):
            self._name = parameter[0]
            self._raw = parameter[1]
            self._eng = parameter[2]
            self._children = parameter[3]

    def to_dict(self, parameter=None):
        self.clone(parameter)
        return self.get_parameter('dict')

    def to_tuple(self, parameter=None):
        self.clone(parameter)
        return self.get_parameter('tuple')

    def set_children(self, children=None):
        if children and self._parameter:
            self._children.extend(children)

    @property
    def name(self):
        return self._name

    @property
    def raw(self):
        return self._raw

    @property
    def eng(self):
        try:
            return float(self._eng)
        except:
            return self._eng

    @property
    def children(self):
        return self._children

    @property
    def desc(self):
        if self._name:
            return STIX_IDB.get_parameter_description(self._name)
            #return stix_desc.get_parameter_desc(self._name)
        return ''

    @property
    def parameter(self):
        return self.get_parameter()
