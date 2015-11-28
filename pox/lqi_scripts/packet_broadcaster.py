#!/usr/bin/python

from socket import *
import time

UDP_IP = "192.168.10.255"
UDP_PORT = 40000
MESSAGE = "LQI Hello"


sock = socket(AF_INET,SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
sock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)

while True:
    sock.sendto(MESSAGE,(UDP_IP,UDP_PORT))
    time.sleep(10)


