# -*- encoding: utf-8 -*-
""" A  Qt parser GUI plugin used to plot ASIC on-demand readouts, threshold readouts and 
    dark current readouts. 

In order to use it, you need to select a background report in the 
GUI and execute this plugin in the plugin manager
"""

import os
import sys
from ROOT import TTree, TFile 
from array import array

sys.path.append(os.path.abspath('../../'))
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
from stix_parser.core import stix_datatypes as sdt
from tkinter import filedialog
from tkinter import *

SPIDs = [54132, 54133, 54134, 54130]
#On demand readout or baseline

DESCR = {
    54132: 'On-demand readout',
    54133: 'Baseline readouts',
    54134: 'Dark current readouts',
    54130: 'threshold scan'
}
def get_filename():
    root = Tk()
    root.filename = filedialog.asksaveasfilename(
        initialdir=".",
        title="Set output filename",
        filetypes=(("ROOT", "*.root"), ("all files", "*.*")))
    filename = root.filename
    root.withdraw()

class Plugin:
    def __init__(self, packets=[], current_row=0):
        self.packets = packets
        self.current_row = current_row
        self.iql = 0

    def run(self):
        isub = 0
        fig = None
        fname=get_filename()

        f=TFile(fname,'recreate')
        t=TTree('detector','detector test')
        max_num=100000

        spid= array('i', [0])
        detectors =array('i', [0])
        channels = array('i', [0])
        ADC_mean =array('i', [0])
        ADC_stdev = array('i', [0])

        #des= array('c', 32*[''])
        runs= array('i', [0])

        t.Branch('spid', spid,'spid/I')
        t.Branch('detector', detectors,'detector/I')
        t.Branch('channel', channels,'channels/I')
        t.Branch('mean', ADC_mean,'mean/I')
        t.Branch('std', ADC_stdev,'std/I')
        t.Branch('run', runs,'run/I')
        #t.Branch('desc', desc,'desc[32]/c')


        is_thr = False
        num_read = 0
        for pkt in self.packets:
            packet = sdt.Packet(pkt)
            if packet.SPID not in SPIDs and num_read == 0:
                print('Not ADC readout report')
                return
            num_read += 1
            if packet.SPID not in SPIDs:
                print('Not ADC readout report')
                continue
            if packet.SPID == 54130:
                is_thr = True
            description = DESCR[packet.SPID]

            UTC = packet['header']['UTC']
            print('Analyzing packet # {}'.format(self.current_row))
            det = packet.get('NIX00104/NIX00100')[0]
            chan = packet.get('NIX00104/NIX00105')[0]
            adc = []
            std = []
            selector = 'NIX00104/NIX00106'
            if is_thr:
                selector = 'NIX00104/NIX00108'
            else:
                std = packet.get('NIX00104/NIX00107')[0]
            adc = packet.get(selector)[0]
            for k, d in enumerate(det):
                spid[k]=packet.SPID
                detectors[k]=d
                channels[k]=cha[k]
                ADC_mean[k]=adc[k]
                if not is_thr:
                    ADC_stdev[k]=std[k]
                runs[k]=current_run
                t.Fill()


            if packet.seg_flag in [2, 3]:
                current_run+=1
            self.current_row += 1
