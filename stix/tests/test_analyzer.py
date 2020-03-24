import sys
from core import stix_packet_analyzer as sta
import json
s=open('tests/pkg.json').read()
packet=json.loads(s)[0]
packet['header']
st= sta.analyzer()
st.load(packet)
start_coarse_time=st.to_array('NIX00445', once=True)[0]
print(start_coarse_time)

start_fine_time=st.to_array('NIX00446', traverse_children=False)[0]
integration_time=st.to_array('NIX00405', traverse_children=False)[0]
detector_mask=st.to_array('NIX00407', traverse_children=False)[0]
pixel_mask=st.to_array('NIXD0407', traverse_children=False)[0]
points=st.to_array('NIX00270/NIX00271',traverse_children=True, once=True)[0][0]
print(points)
print(pixel_mask)
print(detector_mask)
print(integration_time)

