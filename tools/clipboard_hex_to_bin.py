#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_xml_to_bin.py
# @description  : read hex string from clipboard and write it to a binary file
# @date         : March. 28, 2019
import sys
import binascii
import Tkinter as tk
import re
def clipboard_hex_to_bin(out_filename):
    with open(out_filename,'wb') as fout :
        root = tk.Tk()
        root.withdraw()
        raw_hex=root.clipboard_get()
        data_hex= re.sub(r"\s+", "", raw_hex)
        print('header:%s'%data_hex[:10])
        data_binary = binascii.unhexlify(data_hex)
        fout.write(data_binary)
        print('data length:%d'%len(data_binary))
        print('output:%s'%out_filename)
def main():
    fname='clipboard.dat'
    if len(sys.argv) >= 2:
        fname=sys.argv[1]
    clipboard_hex_to_bin(fname)
if __name__ == '__main__':
    main()
