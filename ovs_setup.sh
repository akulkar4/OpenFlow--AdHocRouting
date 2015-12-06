#!/bin/bash

sleep 2m

/sbin/ifup wlan0
ovs-vsctl del-br bridge
ovs-vsctl add-br bridge
/sbin/ifconfig bridge up
ovs-vsctl add-port bridge wlan0
/sbin/ifconfig wlan0 0
/sbin/ifconfig bridge 192.168.10.2 netmask 255.255.255.0
/sbin/iw dev wlan0 interface add fish0 type monitor flags none
/sbin/ifconfig fish0 up
ovs-vsctl set-controller bridge tcp:192.168.10.3:6655

exit
