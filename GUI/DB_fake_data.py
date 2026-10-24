import time
from pprint import pprint
from datetime import datetime
from random import randint
import sqlite3
import numpy as np


#====================== VARIABLES ======================#
DB_PATH = 'test.db'
broker_address="127.0.0.1" #the gateway adress
sub_topic="AUTOPONICS_DEVICES"
pub_topic="AUTOPONICS_CLIENTS"
message = ''
users = dict()
last_update = 0
now = datetime.now()
start_time = float(now.timestamp())


#====================== CLEAR DB ======================#
def clear_DB():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'") #select all tables
            tables = np.array(cursor.fetchall()) #convert to np array
            print("TABLES: " + str(tables))

            for table in tables:
                table_str = np.array2string(table, separator=' ', max_line_width=np.inf)[1:-1] #cut off brackets
                cursor.execute("DROP TABLE IF EXISTS " + table_str) #drop table

            conn.commit()
            print("database cleared")

    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred in clearing database- ', error)

clear_DB()

#====================== UPDATING DATA DICTS ======================#

#class for managing datapoints specific to a device, such as ammonia levels, temperature, pump state, etc
class dataPoint:
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
                #print("Data Point Updated")
        if (exists == False):#if no existing device with ID was detected, create a new one
            self.dataPoints[dataType] = dataPoint(dataType, value, measureTime)
            #print("Data Point Added")

        #print(self.userID, ": ", self.name, ": ", self.dataPoints)
    
    def reset(self):
        for data in self.dataPoints:
            data.reset()


#====================== UPDATING USER DATA DICT ======================#

devices = dict()
def update(deviceName, dataType, value, measureTime):
    #Update or create devices
    exists = False
    for d in devices:
        if (devices[d].name == deviceName): #if the device exists, update it
            devices[deviceName].update(dataType, value, measureTime)
            exists = True
            print("Device Updated")
    if (exists == False):#if no existing device with ID was detected, create a new one
        devices[deviceName] = device(deviceName, "DB_Fake_Data")
        devices[deviceName].update(dataType, value, measureTime)
        print("Device Added")

def clear():
    devices.clear()

def update_data():
    #====================== CONNECT TO DB ======================#
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            #print('Connected to DB')

            clear()
            #select all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = np.array(cursor.fetchall())
            #print("TABLES: " + str(tables))

            for table in tables:
                table_str = np.array2string(table, separator=' ', max_line_width=np.inf)[1:-1] #cut off brackets of table name
                cursor.execute("SELECT * FROM "+table_str) #select all data from table
                rows = cursor.fetchall()
                #convert data to numpy array for processing
                rows_array = np.array([])
                if rows:
                    rows_array = np.array(rows)
                
                for row in rows_array: #for reach row (data point), update the data stored in memory
                    update(table_str.strip("'"), str(row[1]), float(row[2]), float(row[0]))

            print("DATA UPDATED")
            conn.commit()

    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred in update_data- ', error)
            


#====================== PRINTING DATA ======================#

def printCurrentData():
    for device in devices:
        device_obj = devices[device]
        print(" "*2, device_obj.name)
        for dataPoint in device_obj.dataPoints:
            dataPoint_obj = device_obj.dataPoints[dataPoint]
            print(" "*4, dataPoint_obj.dataType, ": ",  dataPoint_obj.values)
            #print(" "*4+f"Times: ", users[user].devices[device].dataPoints[dataPoint].times)

def serializeCurrentData():
    s = ""
    for device in devices:
        device_obj = devices[device]
        s += ("\n" + " "*2 + device_obj.name)
        for dataPoint in device_obj.dataPoints:
            dataPoint_obj = device_obj.dataPoints[dataPoint]
            s += ("\n" + " "*4 + dataPoint_obj.dataType+ ": "+  str(dataPoint_obj.values))
            #print(" "*4+f"Times: ", users[user].devices[device].dataPoints[dataPoint].times)
    return s
            
#====================== ADD DATA POINT ======================#   

def add_data(cursor, deviceName, dataType, value, measureTime):
    #create a new table if needed
    table = """ CREATE TABLE IF NOT EXISTS """+deviceName+""" (
    timestamp INT,
    datatype VARCHAR(255),
    value INT
    ); """
    cursor.execute(table)

    #insert data into database
    cursor.execute("INSERT INTO "+ deviceName +"(timestamp,datatype,value) VALUES(" + measureTime + "," + dataType + "," + value + ");")

#====================== ADD RANDOM DATA ======================#

def addRandomData():
    #Read Data
    print("RANDOMIZING DATA...")

    r_device = randint(0,2)
    r_data_type = randint(0,2)

    f_device = ""
    f_data_type = ""
    f_value = 0

    #generate random data
    if r_device == 0:
        f_device = "'aeroponic system'"
    elif r_device == 1:
        f_device = "'greenhouse control'"
    else:
        f_device = "'grow bed'"
    
    if r_data_type == 0:
        f_data_type = "'Ammonia'"
        f_value = randint(25,200)
    elif r_data_type == 1:
        f_data_type = "'pH'"
        f_value = randint(60,80) / 10
    else:
        f_data_type = "'Temperature'"
        f_value = randint(50,70)

    #get time and make sure in string form
    now = datetime.now()
    timestamp = str(float(now.timestamp()) - start_time)
    f_value = str(f_value)

    #====================== CONNECT TO DB ======================#
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            #add random data to database
            add_data(cursor, f_device, f_data_type, f_value, timestamp)
            conn.commit()

    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred in add random data- ', error)
    

    #Publish Data
    global last_update
    last_update = timestamp
    #printCurrentData()



