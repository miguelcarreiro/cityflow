import time
import serial
import string

def parseGPS(raw_data):
    #print ("raw:", raw_data)  #prints raw data
    data=raw_data.decode('ascii')
    if data[0:6] == '$GPRMC':
        print ('data[0:6]', data[0:6])
        sdata = data.split(",")
        if sdata[2] == 'V':
            print ("no satellite data available")
            return
        time = sdata[1][0:2] + ":" + sdata[1][2:4] + ":" + sdata[1][4:6]
        lat = decode(sdata[3]) #latitude
        dirLat = sdata[4]      #latitude direction N/S
        lon = decode(sdata[5]) #longitute
        dirLon = sdata[6]      #longitude direction E/W
        speed = sdata[7]       #Speed in knots
        trCourse = sdata[8]    #True course
        date = sdata[9][0:2] + "/" + sdata[9][2:4] + "/" + sdata[9][4:6]#date

        print ("time : %s, latitude : %s(%s), longitude : %s(%s), speed : %s, True Course : %s, Date : %s" %  (time,lat,dirLat,lon,dirLon,speed,trCourse,date))

def decode(coord):
    #Converts DDDMM.MMMMM > DD deg MM.MMMMM min
    x = coord.split(".")
    head = x[0]
    tail = x[1]
    deg = head[0:-2]
    min = head[-2:]
    return (deg + " deg " + min + "." + tail +  "min ")


ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                       bytesize=serial.EIGHTBITS, timeout=0.5)

while True:
    data = ser.readline()
    parseGPS(data)
