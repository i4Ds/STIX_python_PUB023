import pprint
from stix_parser.core import stix_parser
from stix_parser.core import stix_idb
idb=stix_idb.stix_idb()

parser = stix_parser.StixTCTMParser()
parser.set_store_binary_enabled(True)
stat=dict()

fr=open('../../data/STIX_SW_VAL.ascii','r')
headers=[]
for line in fr:
    cols=line.split()
    UTC=cols[0]
    packet_hex=cols[-1]
    packet=parser.parse_hex(packet_hex)[0]
    header=packet['header']
    headers.append(headers)
    if header['TMTC'] == 'TM':
        SPID=header['SPID']
        length=len(packet['bin'])
        if SPID not in stat:
            stat[SPID]=[]
        stat[SPID].append(length)
for key, value in stat.items():
    stat[key]=set(value)

for key, value in stat.items():
    desc=idb.get_telemetry_description(key)
    if desc:
        desc=' '.join(list(desc[0]))
        print('{}; {}; {}\n'.format(key,str(list(value)),desc))
