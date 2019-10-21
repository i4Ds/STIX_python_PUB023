
import os

import sys

import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from datetime import datetime

sys.path.append(os.path.abspath(__file__ + "/../../"))

from core import stix_packet_analyzer as sta
import pprint

analyzer = sta.analyzer()

SPID = 54118


class Plugin:
    def __init__(self, packets=[], current_row=0):
        self.packets = packets
        self.current_row = current_row
        self.iql = 0
        self.h2counter = []

    def run(self, pdf):
        print('Number of packets : {}'.format(len(self.packets)))
        #with PdfPages(filename) as pdf:
        figsize = (12, 8)
        isub = 0
        spectra_container = []
        T0 = 0
        for packet in self.packets:
            try:
                if int(packet['header']['SPID']) != SPID:
                    continue
            except ValueError:
                continue
            header = packet['header']
            seg_flag = header['seg_flag']
            if seg_flag in (1, 3):
                #first packet
                self.h2counter.clear()

            fig = None
            analyzer.load(packet)

              
            parameters=packet['parameters']
            scet_coarse=parameters[1][1][0]
            scet_fine=parameters[2][1][0]
            int_duration=parameters[3][1][0]+1

            detector_mask=parameters[4][1][0]
            pixel_mask=parameters[5][1][0]

            num_lc = parameters[14][1][0]


            compression_s = parameters[6][1][0]
            compression_k = parameters[7][1][0]
            compression_m = parameters[8][1][0]

            num_lc_points = analyzer.to_array('NIX00270/NIX00271')[0]


            light_curve = analyzer.to_array(
                'NIX00270/NIX00271/*', eng_param='*')[0]
            triggers = analyzer.to_array('NIX00273/*', eng_param='*')
            rcr = analyzer.to_array('NIX00275/*')




            UTC = header['UTC']

            fig = plt.figure(figsize=figsize)
            plt.axis('off')
            title = ' QL sum LC: # {} \n Packets received at: {} \n T0: {} \
            \n SCET: {} \n Comp_S: {} \n Comp_K: {} \n Comp_M:{}'.format(
                self.iql, UTC, int_duration * 0.1,
                scet_coarse + scet_fine / 65536., compression_s,
                compression_k, compression_m)
            plt.text(0.5, 0.5, title, ha='center', va='center')
            pdf.savefig()
            plt.close()
            #fig.clf()

            fig = plt.figure(figsize=figsize)
            ax = plt.subplot(111)
            for ilc, lc in enumerate(light_curve):
                print("Length of light curve :")
                print(len(lc))
                ax.plot(lc, label='LC {}'.format(ilc))

            ax.legend()
            ax.set_title('QL lightcurves')
            ax.set_xlabel('Time / {} (s)'.format(int_duration * 0.1))
            ax.set_ylabel('Counts in {} s '.format(int_duration * 0.1))
            pdf.savefig()
            plt.close()
            fig = plt.figure(figsize=figsize)
            ax = plt.subplot(111)
            for lt in triggers:
                print("Length of trigger counter accumulator:")
                print(len(lt))
                ax.plot(lt, label='triggers')
                ax.set_title('Triggers')
                ax.set_xlabel('Time / {} (s)'.format(int_duration * 0.1))
                ax.set_ylabel('Counts in {} s '.format(int_duration * 0.1))
            pdf.savefig()
            plt.close()

            fig = plt.figure(figsize=figsize)
            ax = plt.subplot(111)
            for lt in rcr:
                print("Length of RCR:")
                print(len(lt))
                ax.plot(lt, label='RCR')
                ax.set_title('RCR')
                ax.set_xlabel('Time / {} (s)'.format(int_duration * 0.1))
                ax.set_ylabel('RCR ')
            pdf.savefig()
            plt.close()
            self.iql += 1
