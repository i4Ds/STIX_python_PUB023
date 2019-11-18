# plugin to draw current 
import os

import sys
sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('./'))
sys.path.append(os.path.abspath('../../'))
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
from stix_parser.core import stix_datatypes as sdt


SPID = 54119


class Plugin:
    def __init__(self, packets=[], current_row=0):
        self.packets = packets
        self.current_row = current_row
        self.iql = 0

    def run(self, pdf):
        for pkt in self.packets:
            packet=sdt.Packet(pkt)
            if not packet.isa(SPID):
                continue

            figsize = (12, 8)


            #fig.clf()




            isub = 0
            spectra_container = []
            T0 = 0
            pkt=self.packets[self.current_row]
            packet=sdt.Packet(pkt)
            if not packet.isa(SPID):
                return 
            seg_flag = packet['seg_flag']
            fig = None
              
            scet_coarse=packet[1].raw
            scet_fine=packet[2].raw
            int_duration=packet[3].raw+1


            compression_s = packet[5].raw
            compression_k = packet[6].raw
            compression_m = packet[7].raw
            UTC= packet[7].raw


            fig = plt.figure(figsize=figsize)
            plt.axis('off')
            title = ' QL background: # {} \n Packets received at: {} \n T0: {} \
            \n SCET: {} \n Comp_S: {} \n Comp_K: {} \n Comp_M:{}'.format(
                self.iql, UTC, int_duration * 0.1,
                scet_coarse + scet_fine / 65536., compression_s,
                compression_k, compression_m)
            plt.text(0.5, 0.5, title, ha='center', va='center')
            pdf.savefig()
            plt.close()


            light_curve = packet.get('NIX00270/NIX00277/*.eng')[0]
            triggers = packet.get('NIX00273/*.eng')



            fig = plt.figure(figsize=figsize)

            plt.subplot(211)
            for ilc, lc in enumerate(light_curve):
                print("Length of light curve :")
                print(len(lc))
                plt.plot(lc, label='LC {}'.format(ilc))

            plt.title('QL background')
            plt.xlabel('Time / {} (s)'.format(int_duration * 0.1))
            plt.ylabel('Counts in {} s '.format(int_duration * 0.1))

            plt.subplot(212)
            for lt in triggers:
                plt.plot(lt, label='triggers')
            plt.title('Triggers')
            plt.xlabel('Time / {} (s)'.format(int_duration * 0.1))
            plt.ylabel('Counts in {} s '.format(int_duration * 0.1))
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            self.iql += 1
