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


def create_one_detector_svg(detector_id=0, data=None,  svg_template=''):
    if not svg_template:
        svg_template = """
        <svg width="110" height="110">
        <g>
          {}
         </g>
        </svg>
        """
    pixel_template = '''
      <path id="{}" style="fill:{};stroke-width:1;stroke:rgb(200,200,200)"
      d="{}" />'''

    offset=np.array([5,5])
    fill_color='rgb(230,230,230)'

    pitch_x = 22
    pitch_y = 46


    big_p0_top = offset+ np.array([6, 4])
    big_p0_bottom= offset+np.array([6, 4+92])

    big_pixel_top= 'h 22 v 46 h -11 v -4.5 h -11 Z'
    big_pixel_bottom= 'h 22 v -46 h -11 v 4.5 h -11 Z'

    small_p0 =offset+ np.array([6, 50-4.5])
    small_pixel_path = 'h 11 v 9 h -11  Z'

    container= []
    #create big pixels

    guardring='<rect x="{}" y="{}" width="100" height="100"  style="fill:rgb(255,255,255);stroke-width:2;stroke:rgb(0,0,0)" />'.format(
            offset[0],offset[1])
    container.append(guardring)
    #text='<text x="{}" y="{}" filled="red"> Detector #{} </text>'.format(offset[0]+20,offset[1]+110,  detector_id)
    #container.append(text)



    colors=colour.get_colors(data)
    print(colors)


    for i in range(0, 4):
        start = big_p0_top + np.array([i * pitch_x, 0])
        path = 'M {} {} {}'.format(start[0], start[1], big_pixel_top)
        pid = 'id-{}-{}'.format(detector_id, i )
        if colors:
            fill_color=colors[i]
        container.append(pixel_template.format(pid, fill_color,path))


    for i in range(0, 4):
        start = big_p0_bottom + np.array([i * pitch_x, 0])
        path = 'M {} {} {}'.format(start[0], start[1], big_pixel_bottom)
        pid = 'id-{}-{}'.format(detector_id, i + 4 )
        if colors:
            fill_color=colors[i+4]
        container.append(pixel_template.format(pid, fill_color, path))

    for i in range(0, 4):
        start = small_p0 + np.array([i * pitch_x, 0])
        path = 'M {} {} {}'.format(start[0], start[1], small_pixel_path)
        pid = 'id-{}-{}'.format(detector_id, i + 8)
        if colors:
            fill_color=colors[i+8]

        container.append(pixel_template.format(pid, fill_color, path))
    return svg_template.format('\n'.join(container) )

if __name__=='__main__':
    with open('detector.svg','w') as f:
        f.write(create_one_detector_svg(data=[23,5,43,543,53,33,43,33,34,54,55,44]))
