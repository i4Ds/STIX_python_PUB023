import sys
import pprint
from stix_parser.core.ui import client_packet_request as req 
num_packets=req.request(query_str='len', host='localhost',port=9096, verbose_level=1)
#a query_string can be 
#  -  a python slice notation, for example, ':' '0:-1', 3:-1
#  -  'len',  to get the total number of packets,
#  -   index ,  to get a packet of the given index#set verbose_level to 0, to suppress print output  
print('\nNumber of packets:')
print(num_packets)

print('\nQuery packet using indexing:')
packet=req.request(query_str='0', host='localhost',port=9096, verbose_level=1)
pprint.pprint(packet)

print('\nQuery packet using slicing:')
packets=req.request(query_str='0:10', host='localhost',port=9096, verbose_level=1)
pprint.pprint(len(packets))
