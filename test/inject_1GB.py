from core import stix_logger
from core import stix_parser

stix_logger._stix_logger.set_logger(filename=None, verbose=2)

parser = stix_parser.StixTCTMParser()
for i in range(0,500):
    print('loop: {}'.format( i))
    parser.parse_file('data/ql2.dat', 'mongo', 0,'tree')

