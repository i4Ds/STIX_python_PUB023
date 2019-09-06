import sys
sys.path.append('..')
sys.path.append('.')
import stix_packet_analyzer as sta
analyzer=sta.analyzer()

SPID=54124

class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        timestamp=[]
        spectra=[]
        print('searching for calibration packets')
        num=0
        for packet in self.packets:

            spid=0
            try:
                spid=int(packet['header']['SPID'])
            except ValueError:
                #TC 
                continue
            if spid != SPID:
                continue

            analyzer.load_packet(packet)
            detector_ids=analyzer.find_all('NIX00159>NIXD0155')
            pixels_ids=analyzer.find_all('NIX00159>NIXD0156')
            spectra=analyzer.find_all_children('NIX00159>NIX00146')
            for i,spec in enumerate(spectra):
                if sum(spec)>0:
                    num+=1
                    print('Detector %d Pixel %d, counts: %d '%(detector_ids[i], pixels_ids[i], sum(spec)))

        print('Total number of non-empty spectra:%d'%num)




def test():
    from core import stix_parser
    parser = stix_parser.StixTCTMParser()
    parser.parse_file('../GU/raw/asw164_calibration_test1.dat')
    packets=parser.get_decoded_packets()
    p=Plugin(packets)
    p.run()

if __name__=='__main__':
    test()
            







            



        







            
