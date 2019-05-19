#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_plotter.py
# @description  : most used plotting APIs
# @author       : Hualin Xiao
# @date         : March 13, 2019
#
from __future__ import (absolute_import, unicode_literals)
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def discrete_cmap(N, base_cmap=None):
    """Create an N-bin discrete colormap from the specified input map
    base_cmap could be hsv, flag, prism, gist_rainbow, jet, cubehelix, 
    brg,gitst_ncar, PuRd,etc.
    """
    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:
    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, N))
    return color_list


def plot_xy(x, y, xlabel='x', ylabel='y', opt='b-'):
    fig = plt.figure()
    plt.plot(x, y, opt)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    return fig


def plot_text_timeline(timestamps, y, title, ylabel, reset_t0=True):
    plt.title(title)
    x = np.array([])
    xtitle = 'Time (s)'
    if reset_t0:
        x = np.array([t - timestamps[0] for t in timestamps])
        xlabel = 'Time-T0 (s) [T0:{}] '.format(timestamps[0])
    else:
        x = timestamps
    yset = set(y)
    yset_len = len(yset)
    ymap = dict()
    plt.ylim([-0.5, yset_len + 1])
    ytext = []
    colors = discrete_cmap(yset_len, 'hsv')
    for i, value in enumerate(yset):
        ymap[value] = i
        ytext.append(value)
    new_y = [ymap[i] for i in y]

    for xx, yy in zip(x, new_y):
        plt.plot((xx, xx), (yy - 0.5, yy + 0.5), linewidth=1, color=colors[yy])
    plt.xlabel(xlabel)
    # plt.ylabel(ylabel)
    plt.yticks(np.arange(0, yset_len), ytext, rotation=20)
    plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)


def plot_parameter_timeline(timestamps,
                            values,
                            ylabel='y',
                            opt='',
                            reset_t0=True,
                            title=''):
    plt.title(title)
    x = []
    xlabel = 'Time (s)'
    if not reset_t0:
        x = timestamps
    else:
        x = np.array([t - timestamps[0] for t in timestamps])
        duration = timestamps[-1] - timestamps[0]
        plt.xlim([0, duration])
        xlabel = 'Time-T0 (s) [T0:{}] '.format(timestamps[0])
    plt.plot(x, values, opt)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
    plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)


def plot_packet_header_timeline(timestamps, spids, pdf=None):
    fig = plt.figure(figsize=(12, 8))
    #plt.subplot(211)
    plt.title('header')
    duration = timestamps[-1] - timestamps[0]
    plt.xlim([0, duration])
    ymax = len(set(spids))
    plt.ylim([-0.5, ymax + 1])
    spid_y = dict()
    y = 0
    ytick_text = []
    colors = discrete_cmap(ymax, 'hsv')
    for pid in set(spids):
        spid_y[pid] = y
        y += 1
        ytick_text.append(pid)
    for spid, t in zip(spids, timestamps):
        y = spid_y[spid]
        x = t - timestamps[0]
        plt.plot((x, x), (y - 0.5, y + 0.5), linewidth=1, color=colors[y])
    plt.xlabel('Time -T0 (s)')
    plt.yticks(np.arange(0, ymax), ytick_text, rotation=20)
    plt.ylabel('SPID')
    if not pdf:
        plt.show()
    else:
        print('writing to pdf')
        pdf.savefig()
        plt.close()
    fig = plt.figure(figsize=(12, 8))
    #plt.subplot(212)
    plt.plot(timestamps)
    plt.xlabel('Packet #')
    plt.ylabel('Time (s)')
    if not pdf:
        plt.show()
    else:
        print('writing to pdf')
        pdf.savefig()
        plt.close()


def plot_operation_mode_timeline(timestamps, raw_modes, pdf=None):
    mode_text = [
        'LIKELY_BOOT', 'BOOT', 'SAFE', 'MAINTENANCE', 'CONFIGURATION',
        'NOMINAL', 'Unknown'
    ]
    fig = plt.figure(figsize=(12, 8))
    duration = timestamps[-1] - timestamps[0]
    plt.xlim([0, duration])
    ymax = 7
    plt.ylim([-0.5, ymax + 1])
    spid_y = dict()
    y = 0
    ytick_text = []
    colors = discrete_cmap(ymax, 'hsv')
    x = timestamps
    y = raw_modes
    for y, x in zip(raw_modes, timestamps):
        plt.plot((x, x), (y - 0.5, y + 0.5), color=colors[y])
    plt.xlabel('Time -T0 (s)')
    plt.yticks(np.arange(0, ymax), mode_text, rotation=40)
    plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.1)
    plt.title('operation mode')
    if not pdf:
        plt.show()
    else:
        pdf.savefig()
        plt.close()
