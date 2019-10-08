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
from core import stix_idb
analyzer = sta.analyzer()
STIX_IDB = stix_idb.stix_idb()

SPIDs = [54102, 54101]


class Plugin(object):
    def __init__(self, packets=[]):
        self.packets = packets

    def run(self, filename):
        print('Number of packets : {}'.format(len(self.packets)))
        num = analyzer.merge_packets(self.packets, SPIDs)
        print("Nb. of merged packets:{}".format(num))
        results = analyzer.get_merged_parameters()

        with PdfPages(filename) as pdf:
            figsize = (12, 8)
            fig = None
            fig = plt.figure(figsize=figsize)
            plt.axis('off')
            try:
                title = ' Housekeeping data SPID: {} ,start: {} stop: {}'.format(
                    SPID, results['UTC'][0], results['UTC'][-1])
            except KeyError:
                title = ' Housekeeping data SPID: {} ,start: {} stop: {}'.format(
                    SPID, results['time'][0], results['time'][-1])
            plt.text(0.5, 0.5, title, ha='center', va='center')
            pdf.savefig()
            plt.close()
            fig.clf()
            fig = plt.figure(figsize=figsize)
            fig.tight_layout()
            ifig = 1

            for key, value in results.items():
                if 'NIXG' in key:
                    continue
                ax = fig.add_subplot(2, 2, ifig)
                fig.tight_layout()

                text_cal = STIX_IDB.get_textual_mapping(key)

                if len(results['time']) == len(value):
                    ax.step(results['time'], value, where='mid')

                else:
                    ax.plot(value)

                ax.set_xlabel('Time')
                desc = stix_desc.get_parameter_desc(key)
                ax.set_title('{} ({})'.format(desc, key))
                if text_cal:
                    print(text_cal)
                    if len(text_cal) < 10:
                        #ax.set_ylim(text_cal[0])
                        ax.set_yticks(text_cal[0])
                        ax.set_yticklabels(text_cal[1])
                else:
                    ax.set_ylabel('value')

                print('plotting:{}'.format(key))
                ifig += 1
                if ifig == 5:
                    pdf.savefig()
                    plt.close()
                    fig.clf()
                    fig = plt.figure(figsize=figsize)
                    fig.tight_layout()
                    ifig = 1
            if ifig > 1:
                pdf.savefig()
                plt.close()

            print("Output: {}".format(filename))
