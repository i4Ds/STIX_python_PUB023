import sys
sys.path.append('.')
import os
import threading
from pipeline import parser_daemon as pd
from pipeline import goes_downloader as gd

PARSER_SLEEP_TIME=60
GOES_TIME_LOOP=24*3600
def parser_loop():
    print('Starting parser main loop...')
    pd.main()
    threading.Timer(PARSER_SLEEP_TIME, parser_loop).start()

def goes_loop():
    print('Starting GOES main loop...')
    gd.main()
    threading.Timer(GOES_TIME_LOOP, goes_loop).start()



if __name__=='__main__':
    parser_loop()
    goes_loop()
