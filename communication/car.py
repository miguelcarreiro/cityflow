import time
import serial
import struct
import socket
import sys
import string
import sockets
import logging


skt_send = sockets.senderInit()

msgID = 1


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


if __name__ == '__main__':
    if "-l" in sys.argv[1:]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    logging.debug("Program initialization done")

    filename = "output_test_estacionar.txt"

    send_data = openFile(filename)
    logging.debug("GPS data from " + filename + " ready to send")

    for i in send_data:
    	finalMsg = str(msgID)+"|"+str(i)
    	sockets.sendMessage(finalMsg, skt_send)
    	logging.debug("Message with GPS data sent")
    	msgID = msgID + 1
    	print("Message sent: " + finalMsg)
    	logging.debug("Awaiting next GPS data")
    	time.sleep(1)