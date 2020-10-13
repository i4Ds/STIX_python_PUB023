import os

import sys
sys.path.append('../') 
sys.path.append('../../')
sys.path.append('.')

from stix.core import stix_parser 
parser = stix_parser.StixTCTMParser()

packets = parser.parse_moc_ascii('/home/xiaohl/Downloads/Flare_Simulation_20200323.ascii')
print(len(packets))
