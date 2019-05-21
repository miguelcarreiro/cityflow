# Car_motor_test project

The Car_motor_test project is a very simple example of controlling motors using a Raspberry PI Zero through the GPIO pins.
  

## Getting Started  

The car_motor_test is a Python program that runs on a Raspberry Pi Zero of a special toy car: a **SmartMob car**. 

The SmartMob car has two motors: a traction motor and a direction motor that are controlled through the GPIO pins of a Raspberry Pi Zero. The program tests if the motors are working as expected, but it may also be used to configure the movement speed, if needed.


For this project, you should be familiar with the  [SmartMob platform](https://github.com/TeresaMVazao/VehicularNetworks/SmartMob-platform/SmartMob.pdf), as well as with basic use of [Raspberry Pi](https://github.com/TeresaMVazao/VehicularNetworks/SmartMob-platform/Intro-RasperryPI.pdf).

Before running the project you will need a that the Raspberry Pi Zero of the SmartMob car is ready to use, with ssh enabled. 
 
 
### Requirements

**1. Hardware  requirements**
* **SmartMob car**: "Raystar remote control car", at a scale 1:24, equipped with the [SmartMob platform](https://github.com/TeresaMVazao/VehicularNetworks/SmartMob-platform/SmartMob.pdf). 
* **Regular AA batteries**: Three AA batteries of 1.5 V, used to to power up the motors.
* **Power bank**: a power bank used to power up the Raspberry Pi Zero. 
* **Power-bank support**: an acrylic support to add on the top of the car to place a power bank.

**2. Software  requirements**
* **Operating System**: last version available at [Raspberry Pi website](https://www.raspberrypi.org/documentation/installation). The version used is "2018-11-13-raspbian-stretch.img" (updated and ready to use)
* **Programming language**: Python3.
* **Other tools**:

**3. Raspberry Pi Configuration  requirements**
*  **Remote access**: ssh enabled

**4. Networking options**
*  **Raspberry PI Zero**: Raspberry PI and PC in the same wireless network.

### Installation guide
**I. SmartMob car assembly**
Start by assembly the SmartMob car to work in [integrated mode](https://github.com/TeresaMVazao/VehicularNetworks/SmartMob-platform/SmartMob-car-integrated-mode.png). Fo that:
1. Place three regular AA batteries into the batteries compartment.
2. Open the car and remove the coverage.
3. Place a power bank acrylic support on the top of the car and fixed the power bank to it.

**II. Access the Raspberry PI**
Now that you have assembled the car, it's time to boot the system and remotely access the Raspberry Pi. For this, proceed as follows:
1. On the car, turn on the [Switch S1](https://github.com/TeresaMVazao/VehicularNetworks/SmartMob-platform/SmartMob-power-supply.png), near the batteries compartment.
2. Connect the Raspberry Pi Zero to the power bank. 
3. Check if there is connectivity between the Raspberry PI and your PC. For this:
    `````
    $ ping raspberrypi.local
    `````
4. Remotely access the Raspberry Pi by ssh . After digiting the commnand, upon request, digit "Yes" and enter the Raspberry Pi password.
    `````
    $ ssh pi@raspberrypi.local 
    ....upon request, digit "Yes" 
    .... upon request, enter the Raspberry Pi password.
    `````
**IV. Installing the software**
1. At the Raspberry Pi, clone the git repository to the directory **/home/pi/code-examples/sensors/car-motor-test**. 
    `````
    $ cd /home/pi/code-example/sensors
    $ git clone https://github.com/TeresaMVazao/VehicularNetworks/sensors/car-motor-test car-motor-test
    `````
2. Check if the Raspberry Pi contains the following software:
    `````
    -> /home/pi/code-examples/sensors/car-motor-test
             +------------gpio_pins.txt 	
             +------------test-motor.py 	
    `````
## Deployment

**I. System status check**
Before running and test the system, start by an initial check of the main components.
1. Check if the SmartMob car is correctly assembled by detecting if:
	* There is no coverage
	* It has three AA 1.5V batteries and the switch S1 is turned on..
	* There is a power bank attached to an acrylic support and connected to the Raspberry Pi.
2. Check if the Raspberry PI is accesssible by detecting if:
	*  The boot  is completed 
	*  There is an active remote access session between the Raspberry PI and your PC. 

**II.  System execution and test**
Now, the system is ready for test. For that:
1. At the Raspberry PI,  run the program, as follows: 
    `````
    $ cd /code-examples/sensors/car-motor-test
    $ sudo python3 test-motor.py
    ....Upon request, enter Raspberry Pi password
    `````
3. Check the movement sequence:
`````Forward > Backward > Forward > Right > Left > Stop`````


## Authors

* **Teresa Vazao** - *Initial work* - [SmartMob@Tecnico](https://github.com/TeresaMVazao/VehicularNetworks/sensors/car-motor-test)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.




