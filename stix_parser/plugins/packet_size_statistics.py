#!/usr/bin/python3
#plugin template
class Plugin:
    def __init__(self, packets=[], current_row=0):
        self.packets = packets
        self.current_row = current_row

    def run(self):
        # your code goes here
        print('current row: {}'.format(self.current_row))
        print('Number of packets {}:'.format(len(self.packets)))
        print(len(self.packets))

        counter = {}

        total_size = 0
        num_TC = 0
        num_TM = 0
        for packet in self.packets:
            header = packet['header']

            if header['TMTC'] == 'TC':
                if header['name'] != 'ZIX20128':
                    num_TC += 1
                continue
            if header['SPID'] == 54103:
                #hk4 should not count
                continue
            total_size += header['raw_length']
            num_TM += 1
            apid = header['apid']
            if apid not in counter:
                counter[apid] = 0
            counter[apid] += header['raw_length']
        print('TM Total size:', total_size)

        print('APID, length')
        for key, value in counter.items():
            print('{}, {}'.format(key, value))
        print('Number of TM', num_TM)
        print('Number of TC', num_TC)
