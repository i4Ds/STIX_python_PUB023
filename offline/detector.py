import numpy as np
DETECTOR_IDs = """
Detector 01 1 0 0x00000001 -
Detector 02 2 1 0x00000002 -
Detector 03 3 2 0x00000004 -
Detector 04 4 3 0x00000008 -
Detector 05 5 4 0x00000010 -
Detector 06 6 5 0x00000020 -
Detector 07 7 6 0x00000040 -
Detector 8  8 7 0x00000080 -
Detector 9 9 8 0x00000100 CFL
Detector 10 10 9 0x00000200 background
Detector 11 11 10 0x00000400 -
Detector 12  12 11 0x00000800 -
Detector 13 13 12 0x00001000 -
Detector 14 14 13 0x00002000 -
Detector 15 15 14 0x00004000 -
Detector 16 16 15 0x00008000 -
Detector 17 17 16 0x00010000 -
Detector 18 18 17 0x00020000 -
Detector 19 19 18 0x00040000 -
Detector 20 20 19 0x00080000 -
Detector 21 21 20 0x00100000 -
Detector 22 22 21 0x00200000 -
Detector 23 23 22 0x00400000 -
Detector 24 24 23 0x00800000 -
Detector 25 25 24 0x01000000 -
Detector 26 26 25 0x02000000 -
Detector 27 27 26 0x04000000 -
Detector 28 28 27 0x08000000 -
Detector 29 29 28 0x10000000 -
Detector 30 30 29 0x20000000 -
Detector 31 31 30 0x40000000 -
Detector 32 32 31 0x80000000 -
"""
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


def create_one_detector_svg(detector_id=0):
    svg_template = """
    <svg width="120" height="120">
      <rect width="100" height="100" 
      style="fill:rgb(255,255,255);stroke-width:2;stroke:rgb(0,0,0)" />
      {}
    </svg>
    """
    path_template = '''
      <path id="{}" style="fill:rgb(230,230,230);stroke-width:1;stroke:rgb(0,0,0)"
      d="{}" />'''

    pitch_x = 22
    pitch_y = 46
    big_p0 = np.array([6, 4])
    big_pixel_path = 'h 22 v 46 h -11 v -9 h -11 Z'
    small_p0 = np.array([6, 50 - 4.5])
    small_pixel_path = 'h 11 v 9 h -11  Z'

    svg_pixels = []
    #create big pixels
    for i in range(0, 4):
        for j in range(0, 2):
            start = big_p0 + np.array([i * pitch_x, j * pitch_y])
            path = 'M {} {} {}'.format(start[0], start[1], big_pixel_path)
            pid = 'id-{}-{}'.format(detector_id, i + 4 * j)
            svg_pixels.append(path_template.format(pid, path))
    for i in range(0, 4):
        start = small_p0 + np.array([i * pitch_x, 0])
        path = 'M {} {} {}'.format(start[0], start[1], small_pixel_path)
        pid = 'id-{}-{}'.format(detector_id, i + 8)
        svg_pixels.append(path_template.format(pid, path))

    return svg_template.format('\n'.join(svg_pixels))

if __name__=='__main__':
    print(create_one_detector_svg())
