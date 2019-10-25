from stix_parser.core import stix_parser
import binascii
import struct
def to_SCET(hex_str):
    raw = binascii.unhexlify(hex_str)
    scet=struct.unpack('>IH',raw)
    return scet[0]+scet[1]/65536.


parser = stix_parser.StixTCTMParser()
packets=[]
f=open('S20.log','r')
for line in f:
    cols=line.split()
    UTC=cols[0]
    scet1_hex=cols[1].replace(':','')
    scet2_hex=cols[2].replace(':','')
    scet1=to_SCET(scet1_hex)
    scet2=to_SCET(scet2_hex)
    hex_data=cols[-1]
    raw_bin = binascii.unhexlify(hex_data)
    packet=parser.parse_hex(raw_bin)[0]
    parameters = packet['parameters']
    heartbeat_value=parameters[9][3][1][1][0]  #NIX00059, 
    print('{}, {}, {}\n'.format(scet1,scet2,heartbeat_value))

    

