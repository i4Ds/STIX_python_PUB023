#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_xml_to_bin.py
# @description  : read hex string from clipboard and write it to a binary file
# @date         : March. 28, 2019
import sys
import Tkinter as tk
from cStringIO import StringIO
import numpy as np
from matplotlib import pyplot as plt

root = tk.Tk()
root.withdraw()
raw_data=root.clipboard_get()
buf=StringIO(raw_data)
#print buf.readlines()
x=[]
y=[]
for line in buf.readlines():
    row=line.split()
    x.append(float(row[0]))
    y.append(float(row[1]))
#print
print x,y
xx=np.array(x)
yy=np.array(x)
plt.plot(x,y)
    
plt.show()
    
