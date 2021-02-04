#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Flare detection algorithm
    Procedure:
    1) smoothing the lowest energy bin lightcurve using a butterworth low-pass filter
    2) searching for local maxima in the smoothed lightcurve

"""

import os
import sys
sys.path.append('.')
from scipy import signal
import numpy as np
from stix.core import stix_datatypes as sdt
from stix.core import mongo_db as db
from stix.core import stix_datetime
from stix.core import stix_logger
logger = stix_logger.get_logger()

mdb=db.MongoDB()

SPID = 54118

terminal=False
def info(msg):
    if terminal:
        print(msg)
        return
    logger.info(msg)


def get_lightcurve_data(file_id):
    packets = mdb.select_packets_by_run(file_id, SPID)
    if not packets:
        info(f'No QL LC packets found for run {file_id}')
        return None
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
    return {'time': np.array(unix_time), 'lc': np.array(lightcurves[0])}

def find_peaks(data, filter_cutoff_freq=0.03, filter_order=4, 
        peak_min_width=15, peak_min_distance=75,  sigma=20 ): # 1min, seperated by 75*4=300 seconds):
    unix_time=data['time']
    lightcurve=data['lc']
    median=np.median(lightcurve)
    height=median+3*np.sqrt(median)
    b,a=signal.butter(filter_order, filter_cutoff_freq, 'low', analog=False) 
    lc_smoothed = signal.filtfilt(b, a, lightcurve)
    xpeaks, properties = signal.find_peaks(lc_smoothed,
                                                height=height,
                                                #threshold=threshold,
                                                width=peak_min_width,
                                                distance=peak_min_distance)
    data['xpeaks']=xpeaks
    data['properties']=properties
    return data

def save_database(data):
    unix_time=data['time']
    lightcurve=data['lc']
    xpeaks=data['xpeaks']
    result={}
    if xpeaks.size>0:
        peak_values=lightcurve[xpeaks]
        peak_unix_times = unix_time[xpeaks]
        peaks_utc=[stix_datetime.unix2utc(x) for x in peak_unix_times]
        result={'num_peaks':xpeaks.size,
                'peak_unix_time':peak_unix_times.tolist(),
                'peak_counts':peak_values.tolist(),
                'peak_utc':peaks_utc,
                'peak_idx':xpeaks.tolist(),
                #'properties':properties,
                'run_id':data['run_id']
                }
        mdb.save_flare_candidate_info(result)
    return result

def search(run_id, filter_cutoff_freq=0.03, filter_order=4,
        peak_min_width=15, peak_min_distance=75, sigma=20):
    data=get_lightcurve_data(run_id)
    if not data:
        info(f'No QL LC packets found for file {run_id}')
        return None
    result=find_peaks(data, filter_cutoff_freq, filter_order,
            peak_min_width, peak_min_distance, sigma)
    if not result:
        info(f'No peaks found for file {run_id}')
        return None
    info('Number of peaks:{}'.format(len(result['xpeaks'])))
    data['run_id']=run_id
    data['conditions']={'filter_cutoff_freq':filter_cutoff_freq,
            'filter_order':filter_order, 
            'peak_min_width':peak_min_width, 
            'peak_min_distance':peak_min_distance,
            'sigma':sigma
            }
    summary=save_database(result)
    return summary




if __name__ == '__main__':
    import sys
    terminal=True
    if len(sys.argv)!=2:
        print('flare_detection file_number')
    else:
        search(int(sys.argv[1]))
