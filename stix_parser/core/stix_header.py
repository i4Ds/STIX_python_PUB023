#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  File: header.py
#  structure needed to decode headers

TC_HEADER_FIRST_BYTE=[0x1D,0x1B]
TM_HEADER_FIRST_BYTE=[0x0D]
HEADER_FIRST_BYTE=[0x0D,0x1D,0x1B]

TELEMETRY_RAW_STRUCTURE = [  # each dictionary
    {  #first byte
        'APID': (0, 11),
        'category': (0, 4),
        'APID_pid': (4, 7),
        'packet_id': (0, 16),
        'version': (13, 3),
        'packet_type': (12, 1),
        'header_flag': (11, 1),
        'process_id': (4, 11)
    },
    {  #second byte
        'seg_flag': (14, 2),
        'seq_count': (0, 14)
    },
    {
        'length': (0, 16)  # real length is length+1+6
    },
    {
        'PUS': (0, 8),
    },
    {
        'service_type': (0, 8)
    },
    {
        'service_subtype': (0, 8)
    },
    {
        'destination': (0, 8)
    },
    {
        'coarse_time': (0, 32)
    },
    {
        'fine_time': (0, 16)
    }
]
TELEMETRY_HEADER_CONSTRAINTS = {
    'version': [0],
    'packet_type': [0],
    'seg_flag': range(0, 4),
    'length': range(0, 4106 + 1),
    'PUS': [16],
}
TELECOMMAND_HEADER_CONSTRAINTS = {
    'version': [0],
    #'length': range(0, 223 + 1),
    'seg_flag': [3],
}

PACKET_SEG = [
    'continuation packet', 'first packet', 'last packet', 'stand-alone packet'
]
ACK_MAPPING = {
    0: 'no response',
    9: 'ACC_ACK EXE_ACK',
    1: 'ACC_ACK',
    8: 'EXE_ACK'
}

TELECOMMAND_RAW_STRUCTURE = [  # each dictionary
    {
        'APID': (0, 11),
        'category': (0, 4),
        'APID_pid': (4, 7),
        'packet_id': (0, 16),
        'version': (13, 3),
        'packet_type': (12, 1),
        'header_flag': (11, 1),
        'process_id': (4, 11)
    },
    {
        'seg_flag': (14, 2),
        'seq_count': (0, 14)
    },
    {
        'length': (0, 16)  # real length is length+1+6
    },
    {
        'CCSDC': (0, 1),
        'PUS': (1, 3),
        'ACK': (4, 4),
    },
    {
        'service_type': (0, 8)
    },
    {
        'service_subtype': (0, 8)
    },
    {
        'source_id': (0, 8)
    },
    {
        'subtype': (0, 8)
    }
]
