""" Changes by Chathura """

"""
 IoT Smart Home: Smart Garage Door Solution using Raspberry Pi Pico W.
 MicroPython program to read and display the data from the sensors related to the Smart Garage Door Solution

 Read data from Ultrasonic Sensor (HC-SR04)
 Read data from Temperature & Humidity Sensor (DHT22)
 Display text from 12C LCD

 @author (MSDP523ME2 Team)
 @version (14/05/2023)

"""
import network
import ujson
import _thread
from machine import I2C, Pin, time_pulse_us
from time import sleep_us, sleep
from dht import DHT22
from pico_i2c_lcd import I2cLcd
from umqttsimple import MQTTClient

# Define the GPIO pin numbers for the untronicsonic sensor trigger and echo pins
US_ECHO_PIN = 26
US_TRIGGER_PIN = 27

# Define the GPIO pin numbers for the Temperature & Humidity Sensor data pin
THS_SDA_PIN = 15

# Define the GPIO pin numbers for the I2C LCD data & clock pin
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1

# Initialize untrasonic sensor trigger and echo pins
usTrigger = Pin(US_TRIGGER_PIN, Pin.OUT)
usEcho = Pin(US_ECHO_PIN, Pin.IN)

# Initialize Temperature & Humidity Sensor data pin
dht = DHT22(Pin(THS_SDA_PIN))

# Initialize I2C object
i2c = I2C(0, sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN), freq=400000)
# getting I2C address
I2C_ADDR = i2c.scan()[0]
# creating an LCD object using the I2C address and specifying number of rows and columns in the LCD
# LCD number of rows = 2, number of columns = 16
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

#Define a semaphore Lock for multi threading
sLock = _thread.allocate_lock()

beaconID = 'E0C912D24340' #Scanned Becon ID near to the garge door
deviceID = 'E0C912D24340' #UID from the PICO W Board

#Define Info Json Objects
objInfo = {}
objInfo['deviceID'] = deviceID
objInfo['environmentData'] = {}
objInfo['environmentData']['humidity'] = 0
objInfo['environmentData']['temperature'] = 0
objInfo['environmentData']['pressure'] = 0
objInfo['garageDoor'] = {}
objInfo['garageDoor']['status'] = "close"

#Define Action Json Objects
objAction = {}
objAction['deviceID'] = deviceID
objAction['beaconID'] = '' #UID from the PICO W Board
objAction['distance'] = 0
objAction['status'] = ""



"""
Function: getDistance
Messure the distance of the object in centimeters using Ultrasonic Sensor (HC-SR04)
"""
def getDistance():
    # Ensure trigger is low initially
    usTrigger.low()
    sleep_us(2)

    # Send a 10 microsecond pulse to the trigger pin
    usTrigger.high()
    sleep_us(10)
    usTrigger.low()

    # Measure the duration of the echo pulse (in microseconds)
    pulseDuration = time_pulse_us(usEcho, Pin.high)

    # Calculate the distance (in centimeters) using the speed of sound (343 m/s)
    distance = pulseDuration * 0.0343 / 2
    return distance
"""

""" Changes by Imasha """

Function: getTemperature
Messure the current temperature in the envioment in °C using Temperature & Humidity Sensor (DHT22)
"""
def getTemperature():
    # Getting sensor readings
    dht.measure()
    # return temperature in °C
    temp = dht.temperature()
    return temp

"""
Function: getHumidity
Messure the current humidity in the envioment in hum using Temperature & Humidity Sensor (DHT22)
"""
def getHumidity():
    # Getting sensor readings
    dht.measure()
    # return humidity in hum
    hum = dht.humidity()
    return hum

""" Changes from chamath """


"""
Function: printLCD
Print the input string in the I2C LCD Display
@param      msg     string
"""
def printLCD(msg):
    # Clear the LCD fro previous text
    lcd.clear();
    # Printing the text in the LCD screen
    lcd.putstr(msg)

"""
Function: main
This method will run continuously to check the any vehicle approched to the garage drive way
and if does send the data and validate them and open the gate automatically andpublish informational data fro display purposes
"""
def main():

    distance = 1
    if objInfo['garageDoor']['status'] == "close":
        printLCD("Door Close!")
    if objInfo['garageDoor']['status'] == "open":
        printLCD("Door Open!")

    while True:

        temperature = getTemperature()
        humidity = getHumidity()

        objInfo['environmentData']['humidity'] = "{:.1f}".format(humidity)
        objInfo['environmentData']['temperature'] = "{:.1f}".format(temperature)
        objInfo['environmentData']['pressure'] = 1013.25

        #publish to the MQTT brocker
        client.publish(MQTT_INFO_TOPIC, ujson.dumps(objInfo))
        client.ping()
        client.check_msg()

        if objInfo['garageDoor']['status'] == "close" and deviceID != "" and int("{:.0f}".format(distance)) != int("{:.0f}".format(getDistance())):

            #Retrive values from the sensors and assign then to Json Object
            distance = getDistance()
            objAction['beaconID'] = beaconID
            objAction['distance'] = "{:.0f}".format(distance)
            objAction['status'] = objInfo['garageDoor']['status']

            #publish to the MQTT brocker
            client.publish(MQTT_ACT_TOPIC, ujson.dumps(objAction))
            client.ping()
            client.check_msg()

        # Wait for 5 second before taking the next measurement
        sleep(2)
        client.ping()
        client.check_msg()

# WiFi Network Parameters
# SSID: Wokwi-GUEST
# Security: Open

printLCD("Connecting to WiFi")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")
while not wlan.isconnected():
  sleep(0.1)
printLCD("WiFi Connected!")
