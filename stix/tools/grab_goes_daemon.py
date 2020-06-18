#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" goes x-ray flux grabber
    workflow:
    1) grab GOES x-ray flux data 
    2) extract start time and stop time information
    3) write the indexing information to mongo db and write the data to disk

    Author: Hualin Xiao
    Date: 2020-06-18
"""
import sys
import os
import json
import time
import requests
import pymongo
from dateutil import parser as dtparser

GEOS_DATA_DIRECTORY='/opt/stix/geos'

def utc2unix(utc):
    if isinstance(utc, str):
        if not utc.endswith('Z'):
            utc += 'Z'
        try:
            return dtparser.parse(utc).timestamp()
        except:
            return 0
    elif isinstance(utc, int) or isinstance(utc, float):
        return utc
    else:
        return 0
def save_geos(data):
    utc_now= datetime.utcnow()
    filename=utc_now.strftime('%Y%m%d%H%M.json')
    start_unix=utc2unix(data[0]['time_tag'])
    end_unix=utc2unix(data[-1]['time_tag'])
    print(start_unix,end_unix,filename)
    connect = pymongo.MongoClient()
    db = connect["stix"]
    collection_goes= db['goes']
    base_name= os.path.basename(filename)
    abspath = os.path.abspath(filename)
    path = os.path.dirname(abspath)
    doc={'creation_time':utc_now,
        'filename':basename,
        'path':path,
        'start_unix':start_unix,
        'stop_unix':end_unix
        }
    collection_goes.save(doc)
    connect.close()


def download_7_day_data():
    url='http://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json'
    print('downloading data...')
    r = requests.get(url)
    print('to json...')
    data=r.json()
    save_geos(data)

def import_data(filename):
    with open(filename) as f:
        data=json.loads(f.read())
        save_geos(data)

def loop():
    while True:
        download_7_day_data()
        time.sleep(24*3600)


if __name__=='__main__':
    if len(sys.argv)==1:
        loop()
    else:
        import_data(sys.argv[1])



