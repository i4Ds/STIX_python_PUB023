# a script used to generate a list of offsets between OBT and UNIX epoch
# the list is used by web data browsers and Starlet
from stix_parser.core import stix_datetime
import pprint

start=1582150894
span=15*365*84000

offset=0
last_offset=0
for i in range(start, span+start):
    obt=int(stix_datetime.unix2scet(i))
    offset=i-obt
    if last_offset!=offset:
        print(i, stix_datetime.unix2utc(i), offset)
        last_offset=offset
        
    




