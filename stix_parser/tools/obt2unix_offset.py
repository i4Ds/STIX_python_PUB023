# a script used to generate a list of offsets between OBT and UNIX epoch
# the list is used by web data browsers and Starlet
from stix_parser.core import stix_datetime
import pprint

start = 1582150894
span = 15 * 365 * 84000

offset = 0
last_offset = 0
i = start
while i < span + start:
    obt = stix_datetime.unix2scet(i)
    offset = i - obt
    if abs(last_offset - offset) > 0.1:
        print(i, stix_datetime.unix2utc(i), offset)
        last_offset = offset
    i += 3600
