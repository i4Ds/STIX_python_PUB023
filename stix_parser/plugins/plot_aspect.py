#plugin example
import sys
sys.path.append('..')
sys.path.append('.')
from stix_parser.core import stix_datatypes as sdt
from matplotlib import pyplot as plt


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
        for pkt in self.packets:
            packet = sdt.Packet(pkt)
            if not packet.isa(54102):
                continue
            timestamp.append(float(packet['unix_time']))
            names = ['NIX00078', 'NIX00079', 'NIX00080', 'NIX00081']
            results = packet.children_as_dict()
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
