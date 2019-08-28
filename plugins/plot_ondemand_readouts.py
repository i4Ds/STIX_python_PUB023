#plot baseline 

import os
from PyQt5 import QtWidgets, QtCore, QtGui
from data_utils  import *
from matplotlib import pyplot as plt


SPID=54132

class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        # your code goes here
        timestamp=[]
        spectra=[]
        packet=self.packets[self.current_row]
        if int(packet['header']['SPID']) != SPID:
            print('wrong packet type')
            return
        header=packet['header']
        param=packet['parameters']
        nodes=get_nodes(param, 'NIX00104')
        if not nodes:
            print('can not find baseline data in the packet')
            return []
        num_struct=int(nodes[0]['raw'][0])
        params=nodes[0]['children']
        detectors=get_raw(params, 'NIX00100')
        pixels=get_raw(params, 'NIX00105')
        means=get_raw(params, 'NIX00106')
        stds=get_raw(params, 'NIX00107')
        x=[]
        y1=[]
        y2=[]
        for i in range(num_struct):
            x.append(int(pixels[i])+int(detectors[i])*12)
            y1.append(int(means[i]))
            y2.append(int(stds[i]))

        plt.step(x,y1,where='mid',label='On demand readout mean ADC values')
        plt.step(x,y1,where='mid',label='On demand readout mean ADC values')
        plt.step(x,y2,where='mid',label='On demand readout ADC std dev.')
        plt.xlabel('Detector ID')
        plt.ylabel('ADC')
        plt.legend(loc='best')
        plt.show()







        







            
