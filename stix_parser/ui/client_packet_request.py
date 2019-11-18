#!/usr/bin/python3
# request packets from parser Qt GUI via socket
# @author: Hualin Xiao
# @date:  Oct. 28, 2019

import socket
import sys
import pickle
import struct


def update_console_progress(progress):
    num = int(progress / 2.)
    bar = '#' * num + ' ' * (50 - num)
    print('\r[{0}] {1}%'.format(bar, progress), end="", flush=True)


def request(query_str=':', host='localhost', port=9096, verbose_level=1):
    """
       query_string can be 
         -  a python slice notation, for example, ':' '0:-1', 3:-1
         -  "len",  to get the total number of packets,
         -   index ,  to get a packet of the given index
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)
    sock.connect(server_address)
    data = b''
    try:
        sock.sendall(bytearray(query_str.encode()))
        print('Fetching data from server..')
        length = -1
        while True:
            buf = sock.recv(4096)
            if buf:
                if length == -1:
                    length = struct.unpack('>I', buf[0:4])[0]
                data += buf
                update_console_progress(round(len(data) * 100. / length))
                if buf.endswith(b'EOF'):
                    break
            else:
                break
    except Exception as e:
        print(str(e))
        sock.close()
        return []
    finally:
        sock.close()
    result = pickle.loads(data[4:-3])
    if query_str != 'len':
        print('\n{} packets ({} bytes) received.'.format(
            len(result),
            len(data) - 3))
    return result


if __name__ == '__main__':
    import pprint
    pprint.pprint(request())
