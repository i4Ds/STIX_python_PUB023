import sys
import os
import colour
import numpy as np
DETECTOR_MASKS=
{
        0	,0x00000001,
        1	,0x00000002,
        2	,0x00000004,
        3	,0x00000008,
        4	,0x00000010,
        5	,0x00000020,
        6	,0x00000040,
        7	,0x00000080,
        8	,0x00000100,
        9	,0x00000200,
        10	,0x00000400,
        11	,0x00000800,
        12	,0x00001000,
        13	,0x00002000,
        14	,0x00004000,
        15	,0x00008000,
        16	,0x00010000,
        17	,0x00020000,
        18	,0x00040000,
        19	,0x00080000,
        20	,0x00100000,
        21	,0x00200000,
        22	,0x00400000,
        23	,0x00800000,
        24	,0x01000000,
        25	,0x02000000,
        26	,0x04000000,
        27	,0x08000000,
        28	,0x10000000,
        29	,0x20000000,
        30	,0x40000000,
        31	,0x80000000
        }


QUARTER_IDs = """
Q1 0b0001 detectors 1, 2, 5, 6, 7, 11, 12, 13
Q2 0b0010 detectors 3, 4, 8, 9, 10, 14, 15, 16
Q3 0b0100 detectors 20, 21, 22, 26, 27, 28, 31, 32
Q4 0b1000 detectors 17, 18, 19, 23, 24, 25, 29, 30
"""
PIXEL_IDs = """
L0 0 0x001 Top pixel row
L1 1 0x002 Top pixel row
L2 2 0x004 Top pixel row
L3 3 0x008 Top pixel row
L4 4 0x010 Bottom pixel row
L5 5 0x020 Bottom pixel row
L6 6 0x040 Bottom pixel row
L7 7 0x080 Bottom pixel row
S8 8 0x100 Small pixel
S9 9 0x200 Small pixel
S10 10 0x400 Small pixel
S11 11 0x800 Small pixel
"""

ASIC_CHANNELS = """
Channel number Identification (bit mask) Comment
0 0x00000001 Pixel number 7
1 0x00000002 Pixel number 3
2 0x00000004 -
3 0x00000008 Pixel number 11
4 0x00000010 -
5 0x00000020 Pixel number 6
6 0x00000040 -
7 0x00000080 -
8 0x00000100 Pixel number 2
9 0x00000200 -
10 0x00000400 -
11 0x00000800 Pixel number 10
12 0x00001000 -
13 0x00002000 -
14 0x00004000 -
15 0x00008000 Pixel number 1
16 0x00010000 -
17 0x00020000 -
18 0x00040000 Pixel number 5
19 0x00080000 -
20 0x00100000 -
21 0x00200000 Pixel number 9
22 0x00400000 -
23 0x00800000 -
24 0x01000000 -
25 0x02000000 -
26 0x04000000 Pixel number 0
27 0x08000000 -
28 0x10000000 -
29 0x20000000 Pixel number 4
30 0x40000000 Pixel number 8
31 0x80000000 Guard ring
"""

