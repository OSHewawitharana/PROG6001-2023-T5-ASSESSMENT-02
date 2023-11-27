"""
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
