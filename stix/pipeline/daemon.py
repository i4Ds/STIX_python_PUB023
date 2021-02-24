import sys
sys.path.append('.')
import os
import threading
from stix.pipeline import parser_pipeline as pd
from stix.pipeline import goes_downloader as gd

PARSER_SLEEP_TIME=10
GOES_TIME_LOOP=14
def parser_loop():
    pd.main()
    threading.Timer(PARSER_SLEEP_TIME,
            parser_loop).start()

def goes_loop():
    gd.main()
    threading.Timer(GOES_TIME_LOOP,
            goes_loop).start()




if __name__=='__main__':
    parser_loop()
    goes_loop()
