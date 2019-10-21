#!/usr/bin/python3
#stix packet analyzer

from . import stix_parameter as stp


class StixPacketAnalyzer(object):
    def __init__(self):
        self._parameters = []
        self._parameter_vector = {}
        self._header = None

    def merge_packets(self, packets, SPIDs, default_value_type='eng'):
        num = 0
        for packet in packets:
            try:
                if int(packet['header']['SPID']) not in SPIDs:
                    continue
            except ValueError:
                continue
            self.merge(packet, default_value_type)
            num += 1
        return num

    def merge(self, packet, default_value_type='eng'):
        parameters = packet['parameters']
        header = packet['header']
        if 'UTC' in header:
            if 'UTC' not in self._parameter_vector:
                self._parameter_vector['UTC'] = [header['UTC']]
            else:
                self._parameter_vector['UTC'].append(header['UTC'])
        if 'unix_time' not in self._parameter_vector:
            self._parameter_vector['unix_time'] = [header['unix_time']]
        else:
            self._parameter_vector['unix_time'].append(header['unix_time'])

        for e in parameters:
            param = stp.StixParameter()
            param.clone(e)
            value = 0
            name = param.name
            if 'NIXG' in name:
                continue
            value = param.get_raw_int()
            if default_value_type == 'eng':
                if isinstance(param.eng, (float, int)):
                    value = param.eng

            if name in self._parameter_vector:
                self._parameter_vector[name].append(value)
            else:
                self._parameter_vector[name] = [value]
            if param.children:
                self.merge(param.children, default_value_type)

    def get_merged_parameters(self):
        return self._parameter_vector

    def load(self, packet):
        try:
            self._parameters = packet['parameters']
            self._header = packet['header']
        except KeyError:
            print('Unrecognized packet')


    def to_dict(self, parameter_names=None, parameters=None,  dtype='raw', traverse_children=False):
        if not parameters:
            parameters = self._parameters
        param_dict={}
        for e in parameters:
            param = stp.StixParameter()
            param.clone(e)
            if 'NIXG' in param.name:
                continue
            value=param.get_raw_int()

            if parameter_names:
                if param.name not in parameter_names:
                    continue

            if dtype=='eng':
                value=param.eng

            if param.name in param_dict:
                param_dict[param.name].append(value)
            else:
                param_dict[param.name]=[value]

            if param.children and traverse_children:
                children_results=self.to_dict(parameter_names, param.children,dtype,traverse_children)
                for k, v in children_results:
                    if v:
                        param_dict[k].extend(v)
                
        return param_dict
                



        



    def find(self, name_list, parameters=None, traverse_children=True):
        if not isinstance(name_list, list):
            name_list = [name_list]

        if not parameters:
            parameters = self._parameters
        results = {name: [] for name in name_list}
        #results=dict()
        for e in parameters:
            param = stp.StixParameter()
            param.clone(e)
            if param.name in name_list:
                results[param.name].append(param.raw)
            if param.children and traverse_children:
                children_results = self.find(name_list, param.children)
                for k, v in children_results:
                    if v:
                        results[k].extend(v)
        return results
    """
    def to_array(self, pattern, parameters=None, dtype='raw'):
      #  
      #  pattern examples:
      #      pattern='NIX00159/NIX00146'
      #          return the values of all NIX00146 under NIX00159
      #      pattern='NIX00159/NIX00146/*'
      #          return the children's value of all NIX00146 
     #
      #  
        pnames = pattern.split('/')
        results = []
        if not pnames:
            return []
        if not parameters:
            parameters= self._parameters
        try:
            pname = pnames.pop(0)
        except IndexError:
            return []
        for e in parameters:
            param = stp.StixParameter()
            param.clone(e)
            if param.name == pname or pname == '*':
                if pnames :
                    ret = self.to_array('/'.join(pnames), param.children,
                                        dtype)
                    if ret:
                        results.append(ret)
                else:
                    if dtype == 'eng':
                        if param.eng:
                            results.append(param.eng)
                        else:
                            results.append(param.get_raw_int())
                    elif dtype == 'raw':
                        results.append(param.get_raw_int())

        return results
    """


    def to_array(self, pattern, parameters=None, eng_param='', traverse_children=True, once=False):
        """
          pattern examples:
              pattern='NIX00159/NIX00146'
                  return the values of all NIX00146 under NIX00159
              pattern='NIX00159/NIX00146/*'
                  return the children's value of all NIX00146 
        eng_param:
           The name of the parameter which needs engineering value/decompressed value
        """
        pnames = pattern.split('/')
        results = []
        if not pnames:
            return []
        if not parameters:
            parameters= self._parameters
        try:
            pname = pnames.pop(0)
        except IndexError:
            return []
        for e in parameters:
            param = stp.StixParameter()
            param.clone(e)
            if param.name == pname or pname == '*':
                if pnames and traverse_children:
                    ret = self.to_array('/'.join(pnames), param.children,
                                        eng_param,traverse_children,once)
                    if ret:
                        results.append(ret)
                else:
                    if eng_param==pname:
                        if param.eng:
                            results.append(param.eng)
                        else:
                            results.append(param.get_raw_int())
                    else:
                        results.append(param.get_raw_int())
                    if once:
                        #only capture once
                        break

        return results


def analyzer():
    return StixPacketAnalyzer()
