#!/usr/bin/python
import RPi.GPIO as GPIO
from time import sleep
import basic_service
import threading
import logging
import sys

RED_PIN = [11,15]
GREEN_PIN = [12,22]
YELLOW_PIN = [13,18]

GREEN_TIME = 3
YELLOW_TIME = 2
RED_TIME = 5

UNIQUE_ID = None

NUM_CARS = 0

def main():
	global UNIQUE_ID
	global NUM_CARS
	if "-l" in sys.argv[1:]:
		# If test mode is activated, log will appear in terminal
		logging.basicConfig(level=logging.DEBUG)
	
	if "-i" in sys.argv[1:]:
		pos = sys.argv.index("-i")+1
		UNIQUE_ID = int(sys.argv[pos])

	if "-c" in sys.argv[1:]:
		pos = sys.argv.index("-c")+1
		NUM_CARS = int(sys.argv[pos])

	else:
		# If not, log will not appear in terminal
		 logging.basicConfig(level=logging.WARNING)
	logging.debug("Program initialization done")

	global bs
	bs = bs_thread()
	bs.start()
	sem = semaphore_mgmt()
	sem.start()

	while sem.isAlive():
		try:
			# synchronization timeout of threads kill
			sem.join(1)
		except KeyboardInterrupt:
			# Ctrl-C handling and send kill to threads
			logging.debug("Sending kill to thread listen")
			sem.kill_received = True


class semaphore_mgmt(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.kill_received = False
		GPIO.setmode(GPIO.BOARD) # used board numbers
		GPIO.setup(RED_PIN[0],GPIO.OUT) # Out pin
		GPIO.setup(GREEN_PIN[0],GPIO.OUT) # Out pin
		GPIO.setup(YELLOW_PIN[0],GPIO.OUT) # Out pin

		GPIO.setup(RED_PIN[1],GPIO.OUT) # Out pin
		GPIO.setup(GREEN_PIN[1],GPIO.OUT) # Out pin
		GPIO.setup(YELLOW_PIN[1],GPIO.OUT) # Out pin

	def turn_on_green(self,num_sem):
		GPIO.output(YELLOW_PIN[num_sem-1],GPIO.LOW)
		GPIO.output(RED_PIN[num_sem-1],GPIO.LOW)
		GPIO.output(GREEN_PIN[num_sem-1],GPIO.HIGH) # Led on

	def turn_on_yellow(self,num_sem):
		GPIO.output(GREEN_PIN[num_sem-1],GPIO.LOW)
		GPIO.output(RED_PIN[num_sem-1],GPIO.LOW)
		GPIO.output(YELLOW_PIN[num_sem-1],GPIO.HIGH) # Led on

	def turn_on_red(self,num_sem):
		GPIO.output(YELLOW_PIN[num_sem-1],GPIO.LOW)
		GPIO.output(GREEN_PIN[num_sem-1],GPIO.LOW)
		GPIO.output(RED_PIN[num_sem-1],GPIO.HIGH) # Led on

	def turn_off_all(self,num_sem):
		GPIO.output(YELLOW_PIN[num_sem-1],GPIO.LOW)
		GPIO.output(GREEN_PIN[num_sem-1],GPIO.LOW)
		GPIO.output(RED_PIN[num_sem-1],GPIO.LOW)

	def turn_on_all(self,num_sem):
		GPIO.output(YELLOW_PIN[num_sem-1],GPIO.HIGH)
		GPIO.output(GREEN_PIN[num_sem-1],GPIO.HIGH)
		GPIO.output(RED_PIN[num_sem-1],GPIO.HIGH)

	def run(self):
		global bs
		while self.kill_received == False:

			logging.debug("New semaphore_mgmt thread created")
			self.turn_on_red(2)
			sleep(1)
			self.turn_on_green(1)
			bs.send_light("green")

			sleep(GREEN_TIME) # Wait

			self.turn_on_yellow(1)
			bs.send_light("yellow")
			sleep(YELLOW_TIME) # Wait

			self.turn_on_red(1)
			bs.send_light("red")

			sleep(1)
			self.turn_on_green(2)
			sleep(RED_TIME-YELLOW_TIME) # Wait
			self.turn_on_yellow(2)
			sleep(YELLOW_TIME)

		self.turn_off_all(1)
		self.turn_off_all(2)
		GPIO.cleanup()

class bs_thread(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.kill_received = False

	def run(self):
		global UNIQUE_ID
		global NUM_CARS
		basic_service.DEVICE_TYPE = UNIQUE_ID
		basic_service.num_cars = NUM_CARS

		basic_service.start_beacon("output_sem_location.txt")

		# Start timer thread, that will remove deprecated records
		timer = basic_service.Timer()
		timer.start()

		listen = basic_service.Listen()
		listen.start()
		

	def send_light(self, light_color):
		#print("entrei no send_light do traffic light - cor " + light_color)
		bs_send_light = basic_service.sendLight(light_color)
		bs_send_light.start()

	def get_num_cars():
		return basic_service.num_cars

if __name__ == '__main__':
	main()