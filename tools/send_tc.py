import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 9001))
cmd = b'SEND_TC 3242 ZIX39017 {PIX00248 4294967295} {PIX00062 4095} <--> '
n = s.send(cmd)
print('%d sent' % n)
