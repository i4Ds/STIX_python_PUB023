#!/usr/bin/python3 
from stix_parser.core import stix_parser
parser = stix_parser.StixTCTMParser()
data='0d e5 c3 ce 00 1a 10 03 19 0e 80 00 87 46 6e 97 04 80 00 87 46 00 00 00 00 00 00 00 00 00 00 00 00'
packets=parser.parse_hex(data)
