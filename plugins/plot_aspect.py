#plugin example
import pprint
from matplotlib import pyplot as plt
def get_raw(parameters, name):
    return [int(item['raw'][0]) for item in parameters if item['name']==name][0]

class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        # your code goes here
        plt.ion()
        timestamp=[]
        A0_V=[]
        A1_V=[]
        B0_V=[]
        B1_V=[]
        for packet in self.packets:
            if int(packet['header']['SPID']) != 54102:
                continue
            header=packet['header']
            timestamp.append(float(header['time']))
            parameters=packet['parameters']
            A0_V.append(get_raw(parameters,'NIX00078'))
            A1_V.append(get_raw(parameters,'NIX00079'))
            B0_V.append(get_raw(parameters,'NIX00080'))
            B1_V.append(get_raw(parameters,'NIX00081'))

        plt.plot(timestamp,A0_V,label='A0_V')
        plt.plot(timestamp,A1_V,label='A1_V')
        plt.plot(timestamp,B0_V,label='B0_V')
        plt.plot(timestamp,B1_V,label='B1_V')
        plt.xlabel('Time (s)')
        plt.ylabel('Raw voltage ')
        plt.legend()
        plt.show()
        







            
