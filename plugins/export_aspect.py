#plugin example
import pprint

def get_raw(parameters, name):
    return [int(item['raw'][0]) for item in parameters if item['name']==name]

class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        # your code goes here
        with open('aspect_V.csv','w') as f:
            num = 0
            for packet in self.packets:
                if int(packet['header']['SPID']) != 54102:
                    continue
                parameters=packet['parameters']
                A0_V=get_raw(parameters,'NIX00078')
                A1_V=get_raw(parameters,'NIX00079')
                B0_V=get_raw(parameters,'NIX00080')
                B1_V=get_raw(parameters,'NIX00081')
                csv_line=('{},{},{},{}'.format(A0_V,A1_V,B0_V,B1_V))
                print(csv_line)
                f.write(csv_line+'\n')
                num += 1
            print('{} packets processed'.format(num))
            







            
