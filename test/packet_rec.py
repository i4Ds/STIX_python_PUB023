#!/usr/bin/env python3

import socket
HOST = 'localhost'  # Standard loopback interface address (localhost)
PORTS = [9000, 9001]  # Port to listen on (non-privileged ports are > 1023)
SPEARATOR = '<-->'


def connect_socket(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return s
    except:
        return None


def run():
    for port in PORTS:
        s = connect_socket(HOST, port)
        if s:
            break
    if not s:
        print('Failed to connect to the socket...')
        return
    try:
        buf = b''
        while True:
            data = s.recv(1024)
            if not data:
                break
            buf += data
            if buf.endswith(b'<-->'):
                data2 = buf.split()
                if buf[0:9] == 'TM_PACKET'.encode():
                    print(data2[0:5])
                    raw = data2[-1][0:-4]
                    #print(raw)
                buf = b''

    finally:
        s.close()


if __name__ == '__main__':
    run()
