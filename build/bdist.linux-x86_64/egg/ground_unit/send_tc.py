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


class SIRIUS(object):
    def __init__(self):
        self.cmd_id=0
        self.sock=None
        self.tcl_id=0
        self.num_rec=0
        for port in PORTS:
            self.sock = connect_socket(HOST, port)
            if self.sock:
                break
        if not s:
            print('Failed to connect to the socket...')
            return
        print('socket connection established.')
        print('use Ctrl + c to exit ')
        print('waiting for packets ...')
    def get_one(self):
        buf = b''
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
            self.num_rec+= 1
            return data_binary

    def send_tc(self, cmd):
        if not self.sock:
            print("Failed to send telecommand. Socket not established.")
            return 
        cmd = b'SEND_TC {} {} <--> '.format(self.cmd_id,cmd)
        self.cmd_id+=1
        try:
            print('sending command:'+cmd )
            n = self.sock.send(cmd)
            print('%d sent' % n)
        except Exception as e:
            print(str(e))

    def send_tcl(self,tcl):
        if not self.sock:
            print("Failed to send TCL script. Socket not established.")
            return 
        cmd = b'TCL {} {} <--> '.format(self.tcl_id,cmd)
        self.tcl_id+=1
        try:
            print('sending command:'+cmd )
            n = self.sock.send(cmd)
            print('%d sent' % n)
        except Exception as e:
            print(str(e))
        
