#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : stix_xml_to_bin.py
# @description  : read hex string from clipboard and write it to a binary file
# @date         : March. 28, 2019
import sys
import binascii
import Tkinter as tk
import re
from tools import parser
from cStringIO import StringIO
from stix_io import stix_logger
LOGGER = stix_logger.LOGGER
def parser_clipboard_data():
    root = tk.Tk()
    root.withdraw()
    raw_hex=root.clipboard_get()
    data_hex= re.sub(r"\s+", "", raw_hex)
    print(data_hex)
    try:
        data_binary = binascii.unhexlify(data_hex)
        in_file=StringIO(data_binary)
        status, header, parameters, param_type, num_bytes_read = parser.parse_one_packet(
            in_file, LOGGER)
        if header and parameters:
            LOGGER.pprint(header,parameters)
        else:
            print('header:%s'%str(header))
            print('parameters:%s'%str(parameters))
    except TypeError:
        print('Non hexadecimal digit found in the clipboard')
if __name__ == '__main__':
    parser_clipboard_data()
