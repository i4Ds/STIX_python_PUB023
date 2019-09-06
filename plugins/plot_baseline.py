#plot baseline 

import os
from PyQt5 import QtWidgets, QtCore, QtGui
from data_utils  import *
from matplotlib import pyplot as plt


SPID=54133

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
        baselines=[]

        last_det=-1
        x=[]
        y=[]
        xcoll=[]
        ycoll=[]
        for i in range(num_struct):
            if int(detectors[i])!=last_det and last_det !=-1:
                xcoll.append(x)
                ycoll.append(y)
                x=[]
                y=[]
                plt.step(xcoll[-1],ycoll[-1], where='mid', label='Detector {}'.format(detectors[i]))
            x.append(int(pixels[i]))
            y.append(int(means[i]))
            last_det=int(detectors[i])
            print(x)

        plt.legend(loc='best')
        plt.show()







        







            
