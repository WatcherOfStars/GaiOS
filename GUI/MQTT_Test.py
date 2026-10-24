import paho.mqtt.client as mqtt #import the client
import time
import json
from pprint import pprint
from datetime import datetime

#VARIABLES
broker_address="10.1.99.127" #the gateway adress
running = True
lastTime = time.time()
interval = 5
shadow = ''
message = ''
users = dict()

#Warning Variables
maxTemp = 80
minTemp = 40
maxpH = 75
minpH = 65

##====================== Classes for data management ======================#

#class for managing datapoints specific to a device, such as ammonia levels, temperature, pump state, etc
class dataPoint:
    # dataType = "" #string for name of data, eg "pH"
    # values = [] #list of values
    # times = [] #list of times when recorded

    def __init__(self, dataType, value, measureTime):
        self.dataType = dataType
        self.values = [] #list of values
        self.times = [] #list of times when recorded
        self.values.append(value)
        self.times.append(measureTime)

    def update(self, value, measureTime):
        self.values.append(value)
        self.times.append(measureTime)

    def reset(self):
        self.values.clear()
        self.times.clear()

#class that defines a device with a name and a dict of values. Created automatically based on data collected
class device:
    # name=""
    # userID=""
    # dataPoints = dict()

    def __init__(self, name, userID):
        self.name = name
        self.userID = userID
        self.dataPoints = dict()

    def update(self, dataType, value, measureTime):
        #Update or create data points
        exists = False
        for d in self.dataPoints:
            if (self.dataPoints[d].dataType == dataType): #if the device exists, update it
                self.dataPoints[dataType].update(value, measureTime)
                exists = True
                print("Data Point Updated")
        if (exists == False):#if no existing device with ID was detected, create a new one
            self.dataPoints[dataType] = dataPoint(dataType, value, measureTime)
            print("Data Point Added")

        print(self.userID, ": ", self.name, ": ", self.dataPoints)

        # try: #first try to add to existing data point
        #     self.dataPoints[dataType].update(value, measureTime)
        # except: #if data point does not already exist, add it
        #     self.dataPoints[dataType] = dataPoint(dataType, value, measureTime)
    
    def reset(self):
        for data in self.dataPoints:
            data.reset()

#class that defines a user with a name and dict of devices
class user:
    # name = ""
    # devices = dict()

    def __init__(self, name):
        self.name = name
        self.devices = dict()

    def update(self, deviceName, dataType, value, measureTime):
        #Update or create devices
        exists = False
        for d in self.devices:
            if (self.devices[d].name == deviceName): #if the device exists, update it
                self.devices[deviceName].update(dataType, value, measureTime)
                exists = True
                print("Device Updated")
        if (exists == False):#if no existing device with ID was detected, create a new one
            self.devices[deviceName] = device(deviceName, self.name)
            self.devices[deviceName].update(dataType, value, measureTime)
            print("Device Added")

        # try: #first try to add to existing device
        #     self.devices[deviceName].update(dataType, value, measureTime)
        # except: #if device does not already exist, add it
        #     self.devices[deviceName] = device(deviceName, self.name)
        #     self.devices[deviceName].update(dataType, value, measureTime)

    
    def reset(self):
        for device in self.devices:
            device.reset()

def printCurrentData():
    for user in users:
        user_obj = users[user]
        print(user_obj.name)
        for device in user_obj.devices:
            device_obj = user_obj.devices[device]
            print(" "*2, device_obj.name)
            for dataPoint in device_obj.dataPoints:
                dataPoint_obj = device_obj.dataPoints[dataPoint]
                print(" "*4, dataPoint_obj.dataType, ": ",  dataPoint_obj.values)
                #print(" "*4+f"Times: ", users[user].devices[device].dataPoints[dataPoint].times)

def updateData(shadowMessage):
    #Read Data
    print("PROCESSING DATA...")
    data = json.loads(shadowMessage) #loads data and prints it

    #Update or create users
    exists = False
    for u in users:
        if (users[u].name == data['user']): #if the device exists, update it
            users[u].update(data['device_name'], data['type'], data['value'], time.localtime())
            exists = True
            print("User Updated")
    if (exists == False):#if no existing device with ID was detected, create a new one
        users[data['user']] = user(data['user'])
        users[data['user']].update(data['device_name'], data['type'], data['value'], time.localtime())
        print("User Added")

    # try: #first try to add to existing user
    #         users[data['user']].update(data['device_name'], data['type'], data['value'], time.localtime())
    # except: #if user does not already exist, add it
    #         users[data['user']] = user(data['user'])
    #         users[data['user']].update(data['device_name'], data['type'], data['value'], time.localtime())

    #Publish Data
    client.publish("AUTOPONICS_CLIENT", "This is the Client")
    lastTime = time.time()
    printCurrentData()

#====================== MQTT CODE ======================#

#define callback
def on_message(client, userdata, message):
    print("\n message received " ,str(message.payload.decode("utf-8")))
    global shadow
    shadow = str(message.payload.decode("utf-8"))
    message = str(message.payload.decode("utf-8"))
    updateData(message)

#Connects to gateway
client = mqtt.Client("Client") #create new instance
client.on_message=on_message        #attach function to callback
client.connect(broker_address) #connect to broker
client.loop_start()    #start the loop
client.subscribe("AUTOPONICS_DEVICES")

while running:
    if(input == "stop"):
        running = False