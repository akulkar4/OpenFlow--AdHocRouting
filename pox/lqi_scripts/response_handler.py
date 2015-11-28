#!/usr/bin/python

import socket
import subprocess as sub
import thread
import time
import fcntl
import struct


ip_list = ['192.168.10.1','00:00:00:00:00:00','0','192.168.10.2','00:00:00:00:00:00','0','192.168.10.3','00:00:00:00:00:00','0',\
           '192.168.10.4','00:00:00:00:00:00','0']

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s',ifname[:15]))[20:24])

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])
            
                      
def tcp_dump():
    tstamp_1 = 0
    tstamp_2 = 0
    tstamp_3 = 0
    tstamp_4 = 0

    ip = get_ip_address('bridge')

    mac = getHwAddr('bridge')
                      
    p = sub.Popen(('sudo','tcpdump','-l','-i','fish0','not','broadcast','and','-n','udp','and','dst','port','40002','and','dst','host','192.168.10.3'),stdout=sub.PIPE)
    for row in iter(p.stdout.readline,b''):
        sig_val = row.rstrip()
        if sig_val.find("192.168.10.1.40000") != -1:
            tstamp_1 = time.time()
            sig_id_1 = sig_val.find("dB") 
            ip_list[2] = sig_val[sig_id_1-2:sig_id_1]
        else:
            if ip != "192.168.10.1":
                if time.time() - tstamp_1 > 30:
                    ip_list[2] = '0'
            else:
                ip_list[2] = '1000'
                ip_list[1] = mac
                
        if sig_val.find("192.168.10.2.40000") != -1:
            tstamp_2 = time.time()
            sig_id_2 = sig_val.find("dB")
            ip_list[5] = sig_val[sig_id_2-2:sig_id_2]
        else:
            if ip != "192.168.10.2":
                if time.time() - tstamp_2 > 30:
                    ip_list[5] = '0'
            else:
                ip_list[5] = '1000'
                ip_list[4] = mac

                
        if sig_val.find("192.168.10.3.40000") != -1:
            tstamp_3 = time.time()
            sig_id_3 = sig_val.find("dB")
            ip_list[8] = sig_val[sig_id_3-2:sig_id_3]
        else:
            if ip != "192.168.10.3":
                if time.time() - tstamp_3 > 30:
                    ip_list[8] = '0'
            else:
                ip_list[8] = '1000'
                ip_list[7] = mac

                
        if sig_val.find("192.168.10.4.40000") != -1:
            tstamp_4 = time.time()
            sig_id_4 = sig_val.find("dB")
            ip_list[11] = sig_val[sig_id_4-2:sig_id_4]
        else:
            if ip != "192.168.10.4":
                if time.time() - tstamp_4 > 30:
                    ip_list[11] = '0'
            else:
                ip_list[11] ='1000'
                ip_list[10] = mac

        
        

def response_handler():
    UDP_IP = "0.0.0.0"
    UDP_PORT = 40002
    
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    flag = 0
    
    while True:
        flag = 0
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

        if addr[0] == "192.168.10.1":
            ip_list[0] = addr[0]
            ip_list[1] = data

        elif addr[0] == "192.168.10.2":
            ip_list[3] = addr[0]
            ip_list[4] = data

        elif addr[0] == "192.168.10.3":
            ip_list[6] = addr[0]
            ip_list[7] = data
            
        elif addr[0] == "192.168.10.4":
            ip_list[9] = addr[0]
            ip_list[10] = data

        #print ip_list

def send_to_control():
    
    CONTROLLER_IP = '192.168.10.2'
    CONTROLLER_PORT = 50000

    while True:
        time.sleep(10)
        data = ''
        count = 1
        for x in ip_list:
            data = data + x
            if count != 12:
                if count%3 == 0:
                    data = data + ';'
                else:
                    data = data + ','
            count = count + 1
        print data
        sock =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.sendto(data,(CONTROLLER_IP,CONTROLLER_PORT))
        

try:
    thread.start_new_thread(tcp_dump,())
    thread.start_new_thread(response_handler,())
    thread.start_new_thread(send_to_control,())
    
except:
    print "Error: Unable to start threads."

while 1:
    pass
