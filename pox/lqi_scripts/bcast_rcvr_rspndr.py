#!/usr/bin/python

import socket
import fcntl, socket, struct

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])
            
    

UDP_IP = "192.168.10.255"
UDP_PORT = 40000

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

sock1 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    sock.sendto(getHwAddr("wlan0"),(addr[0],40002))




    
# sock.sendto(getHwAddr("wlan0"),(addr[0],40002))
