#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A program to search for flares
1. cmake 
3. make install

"""

import os
import sys
import time
import requests
from scipy import signal
import numpy as np
from matplotlib import pyplot as plt
from stix.core import stix_datatypes as sdt
from stix.core import mongo_db as db
from stix.core import stix_datetime

mdb=db.MongoDB()
#default_folder = '/data/flare_search/'
SPID = 54118

def search(file_id, peak_min_width=15, peak_min_distance=75): # 1min, seperated by 75*4=300 seconds):
    packets = mdb.select_packets_by_run(file_id, SPID)
    if not packets:
        print(f'No QL LC packets found for run {file_id}')
        return
    #else:
    #    print('Number of  LC packets found for run {}: {}'.format(file_id,packets.count()))

    #fname_out = os.path.abspath(
    #    os.path.join(output_dir, 'solar_flares_{}.pdf'.format(file_id)))
    #figsize = (12, 8)
    #fig = plt.figure(figsize=figsize)
    lightcurves = {}
    unix_time = []
    for pkt in packets:
        packet = sdt.Packet(pkt)
        if not packet.isa(SPID):
            continue
        #fig = None

        scet_coarse = packet[1].raw
        scet_fine = packet[2].raw
        start_scet = scet_coarse + scet_fine / 65536.

        int_duration = (packet[3].raw + 1) * 0.1

        detector_mask = packet[4].raw
        pixel_mask = packet[6].raw

        num_lc = packet[17].raw

        compression_s = packet[8].raw
        compression_k = packet[9].raw
        compression_m = packet[10].raw

        num_lc_points = packet.get('NIX00270/NIX00271')[0]
        lc = packet.get('NIX00270/NIX00271/*.eng')[0]
        rcr = packet.get('NIX00275/*.raw')
        UTC = packet['header']['UTC']
        for i in range(len(lc)):
            if i not in lightcurves:
                lightcurves[i] = []
            lightcurves[i].extend(lc[i])
        unix_time.extend([
            stix_datetime.scet2unix(start_scet + x * int_duration)
            for x in range(num_lc_points[0])
        ])

    if not lightcurves:
        return None

    unix_time=np.array(unix_time)
    lightcurve=np.array(lightcurves[0]) #only search for peaks in the first energy bin 
    xpeak, properties = signal.find_peaks(lightcurve,
                                                width=peak_min_width,
                                                distance=peak_min_distance)
    result={}
    peak_values=lightcurve[xpeak]
    if xpeak.size>0:
        peak_unix_times = unix_time[xpeak]
        peaks_utc=[stix_datetime.unix2utc(x) for x in peak_unix_times]
        result={'num_peaks':xpeak.size,
                'peak_unix_time':peak_unix_times.tolist(),
                'peak_counts':peak_values.tolist(),
                'peak_utc':peaks_utc,
                'peak_idx':xpeak.tolist(),
                #'properties':properties,
                'run_id':file_id
                }
        mdb.write_flares(result)
    return result


if __name__ == '__main__':
    search(268)
