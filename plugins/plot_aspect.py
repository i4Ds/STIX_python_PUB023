#plugin example
import sys
sys.path.append('..')
sys.path.append('.')
from core import stix_packet_analyzer as sta
from matplotlib import pyplot as plt

analyzer = sta.analyzer()


class Plugin:
    def __init__(self, packets=[], current_row=0):
        self.packets = packets
        self.current_row = current_row

    def run(self):
        # your code goes here
        plt.ion()
        timestamp = []
        A0_V = []
        A1_V = []
        B0_V = []
        B1_V = []
        for packet in self.packets:
            if int(packet['header']['SPID']) != 54102:
                continue
            header = packet['header']
            timestamp.append(float(header['unix_time']))
            parameters = packet['parameters']
            analyzer.load_packet(packet)
            names = ['NIX00078', 'NIX00079', 'NIX00080', 'NIX00081']
            results = analyzer.get_raw(names)
            A0_V.append(results['NIX00078'])
            A1_V.append(results['NIX00079'])
            B0_V.append(results['NIX00080'])
            B1_V.append(results['NIX00081'])

        plt.plot(timestamp, A0_V, label='A0_V')
        plt.plot(timestamp, A1_V, label='A1_V')
        plt.plot(timestamp, B0_V, label='B0_V')
        plt.plot(timestamp, B1_V, label='B1_V')
        plt.xlabel('Time (s)')
        plt.ylabel('Raw voltage ')
        plt.legend()
        plt.show()
        plt.savefig('aspect.png')
