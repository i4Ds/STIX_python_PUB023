import sys
sys.path.append('/home/xiaohl/FHNW/STIX/gsw/STIX_parser/stix_parser/ui')
sys.path.append('/home/xiaohl/FHNW/STIX/gsw/STIX_parser/')
import client_packet_request as req

from detector import *

packets=req.request(query_str=':', host='localhost',port=9096, verbose_level=1)
#a query_string can be 
#  -  a python slice notation, for example, ':' '0:-1', 3:-1
#  -  'len',  to get the total number of packets,
#  -   index ,  to get a packet of the given index#set verbose_level to 0, to suppress print output  
adc_packets=[x for x in packets if x['header']['SPID']==54132]
pixel_packets=adc_packets[0:12]
#for p in pixel_packets:
#    print(p['parameters'][0][3][1][1])
detector_scanned=adc_packets[12:]
for p in detector_scanned:
    print(p['parameters'][0][3][0][1])

for d in QUARTER_DETECTORS[1]:

