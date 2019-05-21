#!/usr/bin/python
RASPBERRY = True
import sys, json
if RASPBERRY == True:
    import RPi.GPIO as GPIO
from time import sleep
import basic_service
import logging
import threading

FREQUENCY = 100
MIN_SPEED = 0
MAX_SPEED = 70
MAX_FORWARD_SPEED = 70
MAX_BACKWARD_SPEED = 100
SLEEP_TIME = 2

current_color =""

def main():
    if "-l" in sys.argv[1:]:
        # If test mode is activated, log will appear in terminal
        logging.basicConfig(level=logging.DEBUG)
    else:
        # If not, log will not appear in terminal
         logging.basicConfig(level=logging.WARNING)
    logging.debug("Program initialization done")

    basic_service.start_beacon("output_test_estacionar.txt")

    listen = basic_service.Listen()
    listen.start()

    bs = bs_thread(gpio_data)
    bs.start()



def read_gpio_conf(field):
    print('read_gpio_conf')
    with open('gpio_pins.txt') as json_data:
        data = json.load(json_data)
        print('gpio_pins  data: ', data)
        json_data.close()
    return data[field]

def gpio_init(gpio_data, pwm_motor):
    print ('gpio_init')
    gpio_data = read_gpio_conf('gpio_pins')
    if RASPBERRY == True:
       GPIO.setmode(GPIO.BOARD)
    print('GPIO.setmode(GPIO.BOARD)')
    reset_gpio(gpio_data)
    reset_pwm_motor(gpio_data, pwm_motor)
    return (gpio_data, pwm_motor)

def reset_gpio(gpio_data):
    for key, val in list(gpio_data.items()):
        if key != 'stop':
            if RASPBERRY == True:
                GPIO.setup(val,GPIO.OUT)
                GPIO.output(val,GPIO.LOW)
            print ('GPIO.setup(',val,',GPIO.OUT)')
            print ('GPIO.output(',val,',GPIO.LOW)')


def reset_pwm_motor(gpio_data, pwm_motor):
    for key, val in list(gpio_data.items()):
        if key in ('enable_dir'):
            if RASPBERRY == True:
                pwm_motor[key] = GPIO.PWM(val, FREQUENCY)
                pwm_motor[key].start(MIN_SPEED)
            print ('pwm_motor[',key,'] = GPIO.PWM(',val,',',FREQUENCY,')')
            print ('pwm_motor[',key,'].start(',MIN_SPEED,')')
    return pwm_motor

def test_motor(gpio_data):
    if RASPBERRY == True:
        print ('testing motion_engine - forward direction')
        input('print enter to continue')
        pwm_motor['enable_dir'].ChangeDutyCycle(MAX_FORWARD_SPEED)
        GPIO.output(gpio_data['forward_dir'], GPIO.HIGH)
        GPIO.output(gpio_data['backward_dir'], GPIO.LOW)
        GPIO.output(gpio_data['enable_dir'], GPIO.HIGH)
        sleep (SLEEP_TIME)
        print ('testing motion_engine - backward direction')
        input('print enter to continue')
        pwm_motor['enable_dir'].ChangeDutyCycle(MAX_BACKWARD_SPEED)
        GPIO.output(gpio_data['backward_dir'], GPIO.HIGH)
        GPIO.output(gpio_data['forward_dir'], GPIO.LOW)
        GPIO.output(gpio_data['enable_dir'], GPIO.HIGH)
        sleep (SLEEP_TIME)
        print ('testing motion_engine - forward direction')
        input('print enter to continue')
        sleep (SLEEP_TIME)
        print ('test concluded')
        input('press enter to terminate the test')

def sem_motor_control(color, gpio_data):
    if color == 'green':
        print("Entered green, Semaphore: " + color)
        pwm_motor['enable_dir'].ChangeDutyCycle(MAX_FORWARD_SPEED)
        GPIO.output(gpio_data['forward_dir'], GPIO.HIGH)
        GPIO.output(gpio_data['backward_dir'], GPIO.LOW)
        GPIO.output(gpio_data['enable_dir'], GPIO.HIGH)
    else:
        print("Semaphore: " + color)
        stop_control(gpio_data)


def stop_control(gpio_data):
    for key, val in list(gpio_data.items()):
        if key in ('forward_dir', 'backward_dir', 'enable_dir', 'turn_left', 'turn_right', 'enable_turn'):
            if RASPBERRY == True:
                GPIO.output(val, GPIO.LOW)
            print('GPIO.output(',val, ', GPIO.LOW)')

class bs_thread(threading.Thread):

    def __init__(self, gpio_data):
        threading.Thread.__init__(self)
        self.kill_received = False
        self.gpio_data = gpio_data

    def run(self):
        while True:
            self.rcv_light(gpio_data)

    def rcv_light(self, gpio_data):
        global current_color
        #print(basic_service.color)
        bs_color = basic_service.color
        if bs_color in ['green','yellow','red']:
            if current_color != bs_color:
                current_color = bs_color
                sem_motor_control(current_color,self.gpio_data)

if __name__ == '__main__':
    gpio_data = {}
    gpio_data = read_gpio_conf('gpio_pins')
    pwm_motor = {}
    gpio_init(gpio_data, pwm_motor)
    main()
