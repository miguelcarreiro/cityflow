#!/usr/bin/python
import RPi.GPIO as GPIO
from time import sleep
import basic_service
import threading
import logging
import sys

RED_PIN_SEM1 = 11 # Pin 21 is GPIO 9
GREEN_PIN_SEM1 = 12
YELLOW_PIN_SEM1 = 13

RED_PIN_SEM2 = 15
GREEN_PIN_SEM2 = 22
YELLOW_PIN_SEM2 = 18

RED_PIN = [11,15]
GREEN_PIN = [12,22]
YELLOW_PIN = [13,18]

GREEN_TIME = 2.4
YELLOW_TIME = 2
RED_TIME = 5


def main():
	if "-l" in sys.argv[1:]:
		# If test mode is activated, log will appear in terminal
		logging.basicConfig(level=logging.DEBUG)
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
		GPIO.setup(RED_PIN_SEM1,GPIO.OUT) # Out pin
		GPIO.setup(GREEN_PIN_SEM1,GPIO.OUT) # Out pin
		GPIO.setup(YELLOW_PIN_SEM1,GPIO.OUT) # Out pin

		GPIO.setup(RED_PIN_SEM2,GPIO.OUT) # Out pin
		GPIO.setup(GREEN_PIN_SEM2,GPIO.OUT) # Out pin
		GPIO.setup(YELLOW_PIN_SEM2,GPIO.OUT) # Out pin

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
		basic_service.start_beacon("output_test_estacionar.txt")
		# Start timer thread, that will remove deprecated records
		timer = basic_service.Timer()
		timer.start()
		listen = basic_service.Listen()
		listen.start()

	def send_light(self, light_color):
		#print("entrei no send_light do traffic light - cor " + light_color)
		bs_send_light = basic_service.sendLight(light_color)
		bs_send_light.start()
		


if __name__ == '__main__':
	main()