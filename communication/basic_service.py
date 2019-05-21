#!/usr/bin/env python
#
# Send/receive UDP multicast packets.
# Requires that your OS kernel supports IP multicast.
#
# Usage:
#   mcast -s (sender, IPv4)
#   mcast -s -6 (sender, IPv6)
#   mcast    (receivers, IPv4)
#   mcast  -6  (receivers, IPv6)


import time
import serial
import struct
import socket
import sys
import string
import sockets # a Python code
import threading
import logging


#Startup
client_thread = []
table_neighbor={} 
lock = threading.Semaphore()
lock_msg = threading.Semaphore()
rcvSocket = sockets.receiverInit()
sndSocket = sockets.senderInit()

msgID = 1

color = ""


# def main(file_name=""):
# 	if "-l" in sys.argv[1:]:
# 		# If test mode is activated, log will appear in terminal
# 		logging.basicConfig(level=logging.DEBUG)
# 	else:
# 		# If not, log will not appear in terminal
# 		 logging.basicConfig(level=logging.WARNING)
# 	logging.debug("Program initialization done")
# 	start_beacon(file_name)
# 	# Start timer thread, that will remove deprecated records
# 	timer = Timer()
# 	timer.start()
# 	listen = Listen()
# 	listen.start()
	
# 	while listen.isAlive():
# 		try:
# 			# synchronization timeout of threads kill
# 			listen.join(1)
# 		except KeyboardInterrupt:
# 			# Ctrl-C handling and send kill to threads
# 			logging.debug("Sending kill to thread listen")
# 			listen.kill_received = True

def start_beacon(file_name):
	if file_name != "":
		send_data = openFile(file_name)
		beacon = sendInfo(send_data)
		beacon.start()

class Listen(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.kill_received = False

	def run(self):
		while self.kill_received == False:
			logging.debug("New Listen thread created")
			(ClientMsg, (ClientIP)) = sockets.rcvMessage(rcvSocket)
			logging.debug("Received message, opening message handler...")
			handler = Handler(ClientMsg, ClientIP)
			# Add a new thread to the thread list of clients
			client_thread.append(handler)
			handler.start()

class Handler(threading.Thread):

	def __init__(self, msg, clientIP):
		threading.Thread.__init__(self)
		self.msg = msg
		self.clientIP = clientIP
		self.daemon = True

	def run(self):
		logging.debug("New Handler thread created")
		msg_str = self.msg.decode('utf-8')
		logging.debug("Decoded message")

		msg = msg_str.split("|")

		if not msg:
			logging.warning("Empty message")
			exit(-1, "Empty message!")

		else:
			nodeID = self.clientIP[0]
			logging.debug("Node ID: " + nodeID)
			#print("Message received: " + msg_str)
			tableUpdate(msg, nodeID)

def tableUpdate(msg, nodeID):
	#print(msg)
	msgType = msg[0]
	if msgType == "beacon":

		#identificador unico da mensagem gerada pelo no
		msgIDrcv = msg[1]

		#tempo que foi registado no sistema GPS
		time_gps = msg[2]

		#Coordenadas do GPS para o respetivo nodeID
		latitude = msg[3]
		longitude = msg[4]

		speed = msg[5]
		true_course = msg[6]
		date = msg[7]
		timestamp = time.time()

		if nodeID in table_neighbor:  # means that the table already has that node
			logging.debug("Node ID already in table")
			if int(table_neighbor[nodeID][0]) < int(msgIDrcv): 
				# valid message id
				lock.acquire()
				logging.debug("Acquired lock in neighbor table")
				table_neighbor[nodeID] = [msgIDrcv, timestamp, time_gps, latitude, longitude, speed, true_course, date]
				logging.debug("Updated node ID record")
				lock.release()
				logging.debug("Released lock in neighbor table")
				#print("Updated list: " + str(table_neighbor))

			#else:
				#print("Invalid message ID")
		else:
			logging.debug("Node ID not in table")
			# else we need to add it to the table
			lock.acquire()
			logging.debug("Acquired lock in neighbor table")
			flag = 1
			table_neighbor[nodeID] = [msgIDrcv, timestamp, time_gps, latitude, longitude, speed, true_course, date]
			logging.debug("Added node ID record")
			lock.release()
			logging.debug("Released lock in neighbor table")
			#print("Updated list: " + str(table_neighbor))
	else:
		print("Message received: " + str(msg))
		global color
		color = msg[1]



class Timer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True

	def run(self):
		while True:
			time.sleep(2)
			logging.debug("Verifying timeout")
			for key in table_neighbor.keys():
				logging.debug("Key timeout analysis: " + str(table_neighbor[key][1]))
				if table_neighbor[key][1] < time.time()-5.0:
					#print("Node ID timeout detected! Data that will be deleted:")
					#print(str(table_neighbor[key]))
					lock.acquire()
					del table_neighbor[key]
					lock.release()
					#print("Neighbor table after delete:")
					#print(table_neighbor)


class sendInfo(threading.Thread):
	def __init__(self, gps_file):
		threading.Thread.__init__(self)
		self.gps_file = gps_file
		self.daemon = True

	def run(self):
		global msgID
		count = 0
		while True:
			if count < 10:
				#send beacon
				logging.debug("Sending beacon")

				for i in self.gps_file:
					finalMsg = str("beacon")+"|"+str(msgID)+"|"+str(i)

					lock_msg.acquire()
					sockets.sendMessage(finalMsg, sndSocket)
					lock_msg.release()

					count = count + 1
					msgID = msgID + 1
					logging.debug("Message with GPS data sent")
					
					#print("Message sent: " + finalMsg)
					logging.debug("Awaiting next GPS data")
					time.sleep(1)
			else:
				#send table
				logging.debug("Sending table")
				table_msg = "cam|"
				lock_msg.acquire()
				for i in table_neighbor:
					table_msg += str(table_neighbor[i]) + "|"
				sockets.sendMessage(table_msg, sndSocket)
				lock_msg.release()
				count = 0

class sendLight(threading.Thread):
	def __init__(self, light_color):
		threading.Thread.__init__(self)
		self.daemon = True
		self.light_color = light_color

	def run(self):
		global msgID
		finalMsg = str("den")+"|"+str(self.light_color)
		#print("\nMensagem a ser enviada: " + finalMsg + "\n")
		lock_msg.acquire()
		sockets.sendMessage(finalMsg, sndSocket)
		lock_msg.release()

		msgID = msgID + 1


def openFile(file_name):
	gps_data=[]
	file = open(file_name,"r")
	logging.debug("GPS data ready to send")
	for line in file:
		if line != "('data[0:6]', u'$GPRMC')\n":
			line_split = line.split(",")
			line_filter = ""
			for i in line_split:
				line_filter = line_filter + i.split(" : ")[1] + "|"
			
			gps_data.append(line_filter[:-2])
	logging.debug("GPS data ready to send")
	return gps_data
