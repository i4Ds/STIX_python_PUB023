
#!/usr/bin/python3
#plugin template
import pprint
class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        # your code goes here
        print('current row: {}'.format(self.current_row))
        print('Number of packets {}:'.format(len(self.packets)))
        print(len(self.packets))
        for packet in self.packets:
            if packet['header']['SPID']!=54118:
                continue
            pprint.pprint(packet)

            break
