#!/usr/bin/python3
# request to json
#@Author: Hualin Xiao
#@Date:   Feb. 11, 2020

import sys
from pprint import pprint
from stix.core import stix_datetime
from datetime import datetime
import json

Request={'occurrences':[]}

def get_uid(start_unix, level):
    start_datetime=stix_datetime.unix2datetime(start_unix)
    year=start_datetime.year
    month=start_datetime.month
    day=start_datetime.day
    hour=start_datetime.hour
    minute=start_datetime.minute
    request_id = (year & 0xF) << 28
    request_id |= (month & 0xF) << 24
    request_id |= (day & 0x1F) << 19
    request_id |= (hour & 0x1F) << 14
    request_id |= (minute & 0x3F) << 8
    request_id |= (level & 0xF) << 4
    return request_id

def form_request(start_unix, level, detector_mask,
        tmin, tmax, tunit, emin, emax, euit):
    uid=get_uid(start_unix, level)
    start_obt=int(stix_datetime.unix2scet(start_unix))
    parameters=[['PIX00076',uid],
            ['PIX00070',level],
            ['PIX00072', start_obt],
            ['PIX00073',0], #subseconds
            ['PIX00248', detector_mask],
            ['PIX00071', 1], #number of structure
            ['PIX00077', tmin],
            ['PIX00078', tmax],
            ['PIXX0079', tunit],
            ['PIX00200', emin],
            ['PIX00201', emax],
            ['PIX00202', euit]]
    return {'name': 'ZIXX3801',
            'actionTime': '00:00:10',
            'parameters':parameters}

def main():
    start_utc='2020-05-23T09:38:00Z'
    unix_t0=stix_datetime.utc2unix(start_utc)
    json_file=open('crab.json','w')
    detector_mask= 0xffffffff-0x300
    pixel_mask=0xff #big pixels
    requests={'occurrences':[
        {
            "name": "AIXF414A",
            "parameters": [
                [
                    "XF414A01",
                    "424",
                ],
                [
                    "XF414A02",
                    "0",
                ],
                [
                    "XF414A03",
                    "{}".format(detector_mask),
                ]
            ]
        },
        {
            "name": "AIXF414A",
            "parameters": [
                [
                    "XF414A01",
                    "425",
                ],
                [
                    "XF414A02",
                    "0",
                ],
                [
                    "XF414A03",
                    "{}".format(pixel_mask),
                ]
            ]
        },
    ]}

    for i in range(0,15):
        dt=5760
        unix=unix_t0+i*dt
        print(stix_datetime.unix2utc(unix))
        TC=form_request(unix, 1, detector_mask, 0, dt*10, 20,  3, 17, 0)
        requests['occurrences'].append(TC)
    json_file.write(json.dumps(requests, indent=4))
    print('Operation requests have been written to crab.json!')

main()








