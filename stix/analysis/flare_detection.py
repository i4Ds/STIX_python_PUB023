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
import math
import matplotlib
from matplotlib import pyplot as plt
from stix.core import stix_datatypes as sdt
from stix.core import mongo_db as db
from stix.core import stix_datetime
from stix.core import stix_logger
logger = stix_logger.get_logger()
matplotlib.use('Agg')

mdb = db.MongoDB()

SPID = 54118

terminal = False


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


def make_lightcurve_snapshot(data, docs, snapshot_path):
    '''
                '_id': first_id + i,
                'run_id': result['run_id'],
                'hidden': hidden,
                'peak_counts': result['peak_counts'][i],
                'peak_utc': result['peak_utc'][i],
                'peak_unix_time': result['peak_unix_time'][i],
    '''
    #print(flare_list)
    inserted_ids=docs['inserted_ids']

    for i, inserted_id in enumerate(inserted_ids):
        if inserted_id==None:
            continue
        _id=inserted_id
        min_height=docs['conditions']['min_height']

        start_unix = docs['start_unix'][i]
        end_unix = docs['end_unix'][i]
        margin=300
        where = np.where((data['time'] > start_unix-margin)
                         & (data['time'] < end_unix+margin))
        unix_ts = data['time'][where]
        t_since_t0 = unix_ts - docs['peak_unix_time'][i]
        lc = data['lc'][where]
        peak_counts = docs['peak_counts'][i]


        fig = plt.figure(figsize=(6, 2))
        plt.plot(t_since_t0, lc)
        T0 = stix_datetime.unix2utc(docs['peak_unix_time'][i])

        plt.vlines(0, peak_counts-docs['properties']['prominences'][i], peak_counts,color='C1')

        plt.hlines(docs['properties']['width_heights'][i], 
               xmin=docs['start_unix'][i]-docs['peak_unix_time'][i], 
               xmax=docs['end_unix'][i]-docs['peak_unix_time'][i], 
               linewidth=2, 
               color='C2')

        plt.hlines(min_height, t_since_t0[0], t_since_t0[-1], linestyle='dotted', color='red',label="threshold")
        plt.xlabel(f'T - T0 (s),  T0: {T0}')
        plt.ylabel('Counts / 4 s')
        plt.title(f'Flare #{_id}')
        #plt.yscale('log')
        filename = os.path.join(snapshot_path, f'flare_lc_{_id}.png')
        fig.tight_layout()
        plt.savefig(filename, dpi=100)
        mdb.set_tbc_flare_lc_filename(_id, filename)
        plt.close()
        plt.clf()


def major_peaks(lefts, rights):
    #remove small peaks
    num=lefts.size
    major=[True]*num
    for i in range(num):
        a=(lefts[i],rights[i])
        for j in range(num):
            if i==j:
                continue
            b=(lefts[j],rights[j])
            
            if a[0]>=b[0] and a[1]<=b[1]:  #a in b
                major[i]=False
    return major
def search(run_id,
           filter_cutoff_freq=0.03,
           filter_order=4,
           peak_min_width=15,
           default_threshold=300,
           peak_min_distance=150,
           prominence=20,
           rel_height=0.9,
           snapshot_path='.'):
    data = get_lightcurve_data(run_id)
    if not data:
        info(f'No QL LC packets found for file {run_id}')
        return None


    unix_time = data['time']
    lightcurve = data['lc']

    height = default_threshold

    stat=mdb.get_nearest_qllc_statistics(unix_time[0],500)
    #load historical background data
    if stat:
        if stat['std'][0]<2*math.sqrt(stat['median'][0]): #valid background
            height=stat['median'][0]+2*stat['std'][0]
            prominence=2*stat['std'][0]


    #b, a = signal.butter(filter_order, filter_cutoff_freq, 'low', analog=False)
    #lc_smoothed = signal.filtfilt(b, a, lightcurve)
    result={}
    xpeaks, properties = signal.find_peaks(
        lightcurve,
        height=height,
        prominence=prominence,
        #threshold=threshold,
        width=peak_min_width,
        rel_height=rel_height, #T90 calculation
        distance=peak_min_distance)
    if xpeaks.size==0:
        info(f'No peaks found for file {run_id}')
        return 
    info('Number of peaks:{}'.format(xpeaks.size))
    conditions = {
        'filter_cutoff_freq': filter_cutoff_freq,
        'filter_order': filter_order,
        'peak_min_width': peak_min_width,
        'peak_min_distance': peak_min_distance,
        'rel_height':rel_height,
        'prominence': prominence,
        'bkg_statistics': stat,
        'min_height': height,

    }
    doc = {}
    peak_values = properties['peak_heights']
    peak_unix_times = unix_time[xpeaks]
    peaks_utc = [stix_datetime.unix2utc(x) for x in peak_unix_times]
    majors=major_peaks(properties['left_ips'],properties['right_ips'])
    range_indexs=[(properties['left_ips'][i].astype(int), properties['right_ips'][i].astype(int)) 
            for  i in range(xpeaks.size)]
    total_counts=[int(np.sum(lightcurve[int(r[0]):int(r[1])])) for r in range_indexs]
    doc = {
            'num_peaks': xpeaks.size,
            'peak_unix_time': peak_unix_times.tolist(),
            'peak_counts': peak_values.tolist(),
            'peak_utc': peaks_utc,
            'total_counts':total_counts,
            #'peak_idx': xpeaks.tolist(),
            'conditions':conditions,
            'peak_width_bins': properties['widths'].tolist(),
            'peak_prominence': properties['prominences'].tolist(),
            'start_unix': unix_time[properties['left_ips'].astype(int)].tolist(),
            'end_unix':unix_time[properties['right_ips'].astype(int)].tolist(),
            'is_major': majors,
            'run_id': run_id
        }

    mdb.save_flare_candidate_info(doc)
    doc['properties']=properties
    make_lightcurve_snapshot(data, doc,  snapshot_path)
    return doc


if __name__ == '__main__':
    import sys
    terminal = True
    if len(sys.argv) != 2:
        print('flare_detection file_number')
    else:
        search(int(sys.argv[1]), snapshot_path='/data/flare_lc')
