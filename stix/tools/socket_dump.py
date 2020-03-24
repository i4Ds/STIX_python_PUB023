#!/usr/bin/env python3
# @file         : socket_dump.py
# @description  : A tool to receive packets via socket and dump the packets to a file
# @author       : Hualin Xiao
# @date         : Oct. 11, 2019
# usage:
#     python3 socket_dump.py <OUTPUT>

import sys
import socket
import binascii

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORTS = [9000, 9001]  # Port to listen on (non-privileged ports are > 1023)


def connect_socket(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return s
    except:
        return None


def run(filename):
    for port in PORTS:
        s = connect_socket(HOST, port)
        if s:
            break
    if not s:
        print('Failed to connect to the socket...')
        return

    print('socket connection established.')
    print('use Ctrl + c to exit ')
    print('waiting for packets ...')
    with open(filename, 'wb') as f:
        num = 0
        try:
            buf = b''
            while True:
                while True:
                    data = s.recv(1)
                    buf += data
                    if data == b'>':
                        if buf.endswith(b'<-->'):
                            break
                data2 = buf.split()
                if buf[0:9] == 'TM_PACKET'.encode():
                    data_hex = data2[-1][0:-4]
                    data_binary = binascii.unhexlify(data_hex)
                    f.write(data_binary)
                    num += 1
                    print('Received: TM ({}, {})(SPID {})  at {} '.format(
                        data2[3].decode(), data2[4].decode(),
                        data2[1].decode(), data2[2].decode()))

                buf = b''
        except KeyboardInterrupt:
            f.close()
            print('{} packets written to {}'.format(num, filename))

        finally:
            s.close()


if __name__ == '__main__':
    filename = ''
    if len(sys.argv) < 2:
        from tkinter import filedialog
        from tkinter import *
        root = Tk()
        root.filename = filedialog.asksaveasfilename(
            initialdir=".",
            title="Set output filename",
            filetypes=(("raw data files", "*.dat"), ("all files", "*.*")))
        filename = root.filename
        root.withdraw()
    else:
        filename = sys.argv[1]
    run(filename)
