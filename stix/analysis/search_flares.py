#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A program to search for flares
1. cmake 
3. make install

"""

import os
import sys
sys.path.append('../../')
sys.path.append('./')
import time
import requests
import scipy
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
from stix.core import stix_datatypes as sdt
from stix.core import mongo_db as db
from stix.core import stix_datetime

mdb=db.MongoDB()
default_folder = '/data/flare_search/'
SPID = 54118


def main(file_id, output_dir=default_folder):
    packets = mdb.select_packets_by_run(file_id, SPID)
    if not packets:
        print(f'No QL LC packets found for run {file_id}')
        return
    else:
        print('Number of  LC packets found for run {}: {}'.format(file_id,packets.count()))

    fname_out = os.path.abspath(
        os.path.join(output_dir, 'solar_flares_{}'.format(file_id)))
    figsize = (12, 8)
    fig = plt.figure(figsize=figsize)
    lightcurves = {}
    unix_time = []
    for pkt in packets:
        packet = sdt.Packet(pkt)
        if not packet.isa(SPID):
            continue
        fig = None

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
        print('Number of points')
        print(num_lc)
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
        find_peaks(unix_time,lightcurves[0])


def find_peaks(unix_time, lightcurve, width=20, distance=200):
    ydata = np.array(lightcurve)
    xpeak, properties = scipy.signal.find_peaks(ydata,
                                                width=width,
                                                distance=distance)
    print('Peaks:')
    print(xpeak)
    if xpeak:
        peak_unix_times = unix_time[xpeak]
        print('Peak unix time:')
        print(peak_unix_times)
        print('Properties:')
        print(properties)


if __name__ == '__main__':
    main(268)
