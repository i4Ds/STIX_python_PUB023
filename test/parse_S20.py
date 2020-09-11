from stix_parser.core import stix_parser
import binascii
import struct
from matplotlib import pyplot as plt
def to_SCET(hex_str):
    raw = binascii.unhexlify(hex_str)
    scet=struct.unpack('>IH',raw)
    return scet[0]+scet[1]/65536.


parser = stix_parser.StixTCTMParser()
parser.set_verbose(1)
packets=[]

fr=open('S20.log','r')
fo=open('timestamps.csv','w')
#fo.write('Timestamp 1, Timestamp 2, STIX heart beat')

scet_1=[]
scet_2=[]
stix_scet=[]
t_diff=[]

for line in fr:
    cols=line.split()
    UTC=cols[0]
    scet1_hex=cols[1].replace(':','')
    scet2_hex=cols[2].replace(':','')
    scet1=to_SCET(scet1_hex)
    scet2=to_SCET(scet2_hex)
    hex_data=cols[-1]
    packet=parser.parse_hex(hex_data)[0]
    parameters = packet['parameters']
    heartbeat=parameters[9][3][1][1][0]  #NIX00059, 
    fo.write('{} {} {} {} \n'.format(scet1,scet2,heartbeat, scet2-heartbeat))
    scet_1.append(scet1)
    scet_2.append(scet2)
    stix_scet.append(heartbeat)
    t_diff.append(heartbeat-scet2)
plt.plot(scet_1)
plt.plot(scet_2)
plt.plot(stix_scet)
plt.plot(t_diff)
plt.show()

    

