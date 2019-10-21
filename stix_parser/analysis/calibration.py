
import os

import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from datetime import datetime
import sys
sys.path.append(os.path.abspath(__file__ + "/../../"))

from core import stix_packet_analyzer as sta

analyzer = sta.analyzer()

SPID = 54124


class Plugin:
    def __init__(self, packets=[], current_row=0):
        self.packets = packets
        self.current_row = current_row
        self.ical = 0
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
            detector_ids = analyzer.to_array('NIX00159/NIXD0155')[0]
            pixels_ids = analyzer.to_array('NIX00159/NIXD0156')[0]
            spectra = analyzer.to_array('NIX00159/NIX00146/*')[0]

            parameters=packet['parameters']

            live_time = parameters[4][1][0]
            quiet_time = parameters[3][1][0]
            compression_s = parameters[6][1][0]
            compression_k =  parameters[7][1][0]
            compression_m = parameters[8][1][0]

            for i, spec in enumerate(spectra):
                if sum(spec) > 0:
                    det = detector_ids[i]
                    pixel = pixels_ids[i]

                    print('Detector %d Pixel %d, counts: %d ' %
                          (det, pixel, sum(spec)))

                    g = (det, pixel, spec)
                    spectra_container.append(g)
                    self.h2counter.append((det, pixel, sum(spec)))

            if seg_flag == 2:
                #last packet
                try:
                    UTC = packet['header']['UTC']
                except:
                    UTC = packet['header']['unix_time']

                num = len(spectra_container)
                if num > 0:
                    if fig:
                        fig.clf()
                    fig = plt.figure(figsize=figsize)
                    plt.axis('off')
                    title = ' Calibration Run: # {} \n Packets received at: {} \n live time: {} \
                    \n quiet time: {} \n Comp_S: {} \n Comp_K: {} \n Comp_M:{}'.format(
                        self.ical, UTC, live_time, quiet_time,
                        compression_s, compression_k, compression_m)
                    plt.text(0.5, 0.5, title, ha='center', va='center')
                    pdf.savefig()
                    plt.close()
                    #fig.clf()

                    if fig:
                        fig.clf()
                    fig = plt.figure(1, figsize=figsize)
                    ax = plt.subplot(111)
                    x = np.array([e[0] for e in self.h2counter])
                    y = np.array([e[1] for e in self.h2counter])
                    z = np.array([e[2] for e in self.h2counter])
                    nbins = [32, 12]
                    h = plt.hist2d(
                        x,
                        y,
                        nbins,
                        np.array([(0, 32), (0, 12)]),
                        weights=z,
                        cmin=1,
                        cmap=plt.cm.jet)
                    ax.set_xticks(range(0, 32, 2))
                    ax.set_yticks(range(0, 12, 1))
                    title = 'Calibration run #{} at {}'.format(
                        self.ical, UTC)
                    fig.suptitle(title, fontsize=14, fontweight='bold')
                    plt.title('Counts (compressed)')
                    plt.xlabel('Detector')
                    plt.ylabel('Pixel')
                    plt.colorbar(h[3])
                    pdf.savefig()
                    #plt.clf()
                    plt.close()

                last_detector = -1
                ifig = 0
                has_fig = False
                fig = None
                det_counts = dict()
                for element in spectra_container:
                    det, pixel, spec = element
                    num = len(spec)
                    if last_detector != det:
                        if ifig == 4:
                            ifig = 0
                        ifig += 1

                    if ifig == 1 and last_detector != det:
                        print('creating fig')
                        if has_fig and fig:
                            print('saving fig detector :{}'.format(det))
                            print(last_detector, det, pixel)
                            pdf.savefig()
                            plt.close()
                        if fig:
                            fig.clf()
                        fig = plt.figure(figsize=figsize)
                        fig.tight_layout()
                        fig.suptitle(
                            'Calibration run %d' % self.ical,
                            fontsize=12,
                            fontweight='bold')

                    ax = fig.add_subplot(2, 2, ifig)
                    print("plot for detector : {}".format(det))
                    fig.tight_layout()
                    ax.step(
                        np.linspace(0, num, num),
                        spec,
                        where='mid',
                        label='Pixel {}'.format(pixel))
                    ax.legend(loc='lower right')
                    ax.set_xlabel('Energy channel')
                    ax.set_ylabel('Compressed counts')
                    ax.set_title('Detector {} '.format(det + 1))
                    has_fig = True

                    last_detector = det

                if has_fig and fig:
                    print('saving fig detector :{}'.format(det))
                    print(last_detector, det, pixel)
                    pdf.savefig()
                    plt.close()

                spectra_container.clear()
                self.ical += 1
