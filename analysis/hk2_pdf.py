#plot calibration spectra, whose counts are still compressed

import os

import sys
sys.path.append('..')
sys.path.append('.')
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

from utils import stix_packet_analyzer as sta
from utils import stix_desc
analyzer = sta.analyzer()

SPID = 54102


class Plugin:
    def __init__(self, packets=[], current_row=0):
        self.packets = packets
        self.current_row = current_row
        self.ical=0
        self.h2counter=[]
    def run(self,filename ):
        print('Number of packets : {}'.format(len(self.packets)))
        for packet in self.packets:
            try:
                if int(packet['header']['SPID']) != SPID:
                    continue
            except ValueError:
                continue
            analyzer.merge(packet)
        results=analyzer.get_merged_parameters()
        with PdfPages(filename) as pdf:
            figsize=(12,8)
            fig=None
            fig=plt.figure(figsize=figsize)
            plt.axis('off')
            try:
                title=' Housekeeping data SPID: {} ,start: {} stop: {}'.format(SPID,
                        results['UTC'][0],results['UTC'][-1])
            except KeyError:
                title=' Housekeeping data SPID: {} ,start: {} stop: {}'.format(SPID,
                        results['time'][0],results['time'][-1])
            plt.text(0.5,0.5, title,ha='center',va='center')
            pdf.savefig()
            plt.close()
            fig.clf()
            fig=plt.figure(figsize=figsize)
            fig.tight_layout()
            ifig=1
            for key, value in results.items():
                ax=fig.add_subplot(2,2,ifig)
                fig.tight_layout()
                if len(results['time'])==len(value):
                    ax.step(results['time'], value, where='mid')
                else:
                    ax.plot( value )

                ax.set_xlabel('Time')
                ax.set_ylabel('{} raw value'.format(key))
                desc=stix_desc.get_parameter_desc(key)
                ax.set_title(desc)
                print('plotting:{}'.format(key))
                ifig+=1
                if ifig==5:
                    pdf.savefig()
                    plt.close()
                    fig.clf()
                    fig=plt.figure(figsize=figsize)
                    fig.tight_layout()
                    ifig=1


            if ifig>1:
                pdf.savefig()
                plt.close()

            print("Output: {}".format(filename))





