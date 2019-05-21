#!/bin/bash

sudo ip link set wlo1 down
sudo iwconfig wlo1 mode ad-hoc
sudo iwconfig wlo1 channel 6
sudo iwconfig wlo1 essid 'RV-6'
sudo ip link set wlo1 up
sudo ip addr add 10.1.6.200/24 dev wlo1
