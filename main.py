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
