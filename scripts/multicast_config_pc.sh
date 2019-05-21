#!/bin/bash

sudo ip route add 225.0.0.0/24 dev wlo1
sudo ip -6 route add ff15:7079:7468:6f6e:6465:6d6f:6d63:6173 dev wlo1 table local
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1
