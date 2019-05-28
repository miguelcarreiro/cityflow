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
import csv


#Startup
client_thread = []
table_neighbor={}
lock = threading.Semaphore()
lock_msg = threading.Semaphore()
rcvSocket = sockets.receiverInit()
sndSocket = sockets.senderInit()
DEVICE_TYPE = None #1-10 traffic light  >20 car

num_cars = 0


msgID = 1

color = ""

def start_beacon(file_name):
	if file_name != "":
		send_data = openGpsFile(file_name)
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
			nodeID = self.clientIP[0][:-6]
			logging.debug("Node ID: " + nodeID)
			#print("Message received: " + msg_str)
			tableUpdate(msg, nodeID)

def tableUpdate(msg, nodeID):
	
	msgType = msg[0]

	if msgType == "beacon" and msg[8] != 'None':

		#print(str(msg[8]))

		unique_id = int(msg[8])
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
				table_neighbor[nodeID] = [msgIDrcv, timestamp, time_gps, latitude, longitude, speed, true_course, date, unique_id]
				logging.debug("Updated node ID record")
				lock.release()
				logging.debug("Released lock in neighbor table")
				#print("Updated list: " + str(table_neighbor))

		else:
			logging.debug("Node ID not in table")
			# else we need to add it to the table

			lock.acquire()
			logging.debug("Acquired lock in neighbor table")
			flag = 1
			table_neighbor[nodeID] = [msgIDrcv, timestamp, time_gps, latitude, longitude, speed, true_course, date, unique_id]
			logging.debug("Added node ID record")
			lock.release()
			logging.debug("Released lock in neighbor table")
			#print("Updated list: " + str(table_neighbor))

	elif msgType == "den" and msg[-1] != 'None' and nodeID in table_neighbor.keys():
		#print("Message received: " + str(msg))
		unique_id = int(msg[-1])
		if DEVICE_TYPE != unique_id:
			if DEVICE_TYPE > 20: # sou um carro
				if unique_id < 11: # recebi de um semaforo
					#verificar se e o semaforo mais perto de mim 
					light_id = getNearestTrafficLight(DEVICE_TYPE)
					print("Unique id: " + str(unique_id) + " | Light id: " + str(light_id))
					if unique_id==light_id:
						global color
						color = msg[1]
						#TO DO: carro deve ser controlado por esse semáforo

			elif DEVICE_TYPE < 11: #sou um semáforo
				if unique_id > 20: # recebi de um carro
					#TO DO:contar número de carros
					print("Contar carros")
				elif unique_id < 11: #recebi de um semaforo

					num_cars = int(msg[2])
					#TO DO:transmitir entre semaforos o numero de carros

				else:
					print("outro tipo de dispositivo")

			else:
				print("outro tipo de dispositivo")

class Timer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True

	def run(self):
		while True:
			time.sleep(2)
			logging.debug("Verifying timeout")
			print("Table neighbor:\n" + str(table_neighbor))
			for key in table_neighbor.keys():
				logging.debug("Key timeout analysis: " + str(table_neighbor[key][1]))
				if table_neighbor[key][1] < time.time()-5.0:

					lock.acquire()
					del table_neighbor[key]
					lock.release()


class sendInfo(threading.Thread):
	def __init__(self, gps_file):
		threading.Thread.__init__(self)
		self.gps_file = gps_file
		self.daemon = True

	def run(self):
		global msgID
		global DEVICE_TYPE
		count = 0
		while True:
			if count < 10:
				#send beacon
				logging.debug("Sending beacon")

				for i in self.gps_file:
					finalMsg = str("beacon")+"|"+str(msgID)+"|"+str(i)+"|"+str(DEVICE_TYPE)

					lock_msg.acquire()
					sockets.sendMessage(finalMsg, sndSocket)
					lock_msg.release()

					count = count + 1
					msgID = msgID + 1
					logging.debug("Message with GPS data sent")
					
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
		global num_cars
		finalMsg = str("den") + "|" + str(self.light_color) + "|" + str(num_cars) + "|" + str(DEVICE_TYPE)

		lock_msg.acquire()
		sockets.sendMessage(finalMsg, sndSocket)
		lock_msg.release()

		msgID = msgID + 1


def openGpsFile(file_name):
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

def openConfigFile(file_name):
	device_list = []
	file = open(file_name, "r")
	logging.debug("Config data ready to import")
	csv_reader = csv.reader(file, delimiter='|')

	for row in csv_reader:
		device_list.append([row])

	return device_list

def getNearestTrafficLight(car_id):  #semaforo mais perto consoante direcao
	
	car_coordinate = []

	for key_device in table_neighbor:
		device = table_neighbor[key_device]
		if int(device[-1]) == car_id:   #[-2]?? id?
			car_coordinate = [int(device[3]),int(device[4])]

			break

	min_distance_id = 0
	min_distance = 100000000 #max int
	new_distance = 0
	for key_device in table_neighbor:
		device = table_neighbor[key_device]
		print("Device ID: " + str(device[-1]))
		if int(device[-1]) < 11:

			new_distance = (int(device[4])) - car_coordinate[1]
			print("New distance: " + str(new_distance))

			if new_distance < min_distance and new_distance >= 0:
				min_distance = new_distance

				min_distance_id = device[-1]

	return min_distance_id
