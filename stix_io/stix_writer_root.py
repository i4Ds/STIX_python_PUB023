#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_writer_root.py
# @description  : Write decoded parameters to a root file
#                 Information of the ROOT file format can be found http://root.cern.ch 
#                 Installation of PyROOT is needed
# @author       : Hualin Xiao
# @date         : Feb. 27, 2019
import pprint
from ROOT import TFile, TTree
from array import array


class stix_writer:
    def __init__(self, filename):
        self.filename = filename
        self.packet_counter = 0
        self.fout=None
        if filename:
            #self.out=open(filename,'w')
            self.fout=TFile(filename,'recreate')
            self.tree=TTree('header','header')
            self.seg_flag=array('B',[0])
            self.seq_count=array('I',[0])
            self.service_subtype=array('B',[0])
            self.service_type=array('B',[0])
            self.SPID=array('I',[0])
            self.length=array('I',[0])
            self.des=array('B',[0])
            self.desc=array('c','\0'*64)
            self.timestamp=array('f',[0])
            self.tree.Branch('seg_flag',self.seg_flag,'seg_flag/B')
            self.tree.Branch('seq_count',self.seq_count,'seq_count/I')
            self.tree.Branch('service_type',self.service_type,'service_type/B')
            self.tree.Branch('service_subtype',self.service_subtype,'service_subtype/B')
            self.tree.Branch('SPID',self.SPID,'SPID/I')
            self.tree.Branch('length',self.length,'length/I')
            self.tree.Branch('desc',self.desc,'desc[64]/C')
            self.tree.Branch('timestamp',self.timestamp,'timestamp/f')
            self.tree.Branch('des',self.des,'des/B')

    def done(self):
        self.tree.Write()
        self.fout.Close()

    def write_header(self, header):
        """
        it is called for every telemetry data header
        """
        if self.fout:
            self.seg_flag[0]=header['seg_flag']
            self.seq_count[0]=header['seq_count']
            self.service_subtype[0]=header['service_subtype']
            self.service_type[0]=header['service_type']
            self.SPID[0]=header['SPID']
            self.length[0]=header['data_length']
            self.timestamp[0]=header['time']
            for i,c in enumerate(header['DESCR'][0:64]):
                self.desc[i]=str(c)
            self.tree.Fill()
        #msg = [
        #    self.packet_counter, header['service_type'],
        #    header['service_subtype'], header['SPID'],header['SSID'], header['DESCR'],
        #    header['time'], header['coarse_time'], header['fine_time'],header['segmentation'],header['data_length']
        #]
        #line=(','.join(map(str, msg)))
        #self.packet_counter += 1
        #if self.out:
        #    pp = pprint.PrettyPrinter(indent=4, stream=self.out)
        #    pp.pprint(line)

    def write_parameters(self, parameters):
        pprint.pprint(parameters)
        #if self.out:
            #pp = pprint.PrettyPrinter(indent=4, stream=self.out)
            #pp.pprint(parameters)
