import sqlite3
import fake_data
import time

def add_device(deviceName):
    table = """ CREATE TABLE IF NOT EXISTS """+deviceName+""" (
            timestamp INT,
            datatype VARCHAR(255),
            value INT
        ); """
    cursor.execute(table)

def add_data(deviceName, dataType, value, measureTime):
    print("INSERT INTO "+ deviceName +"(timestamp,datatype,value) VALUES(" + measureTime + "," + dataType + "," + value + ");")
    cursor.execute("INSERT INTO "+ deviceName +"(timestamp,datatype,value) VALUES(" + measureTime + "," + dataType + "," + value + ");")

try:
    conn = sqlite3.connect('data/test.db')
    cursor = conn.cursor()
    print('Connected to DB')

    device = "'test_dev'"
    type = "'temperature'"
    value = str(6)
    timestamp = str(time.time())

    add_device(device)
    #cursor.execute("DELETE FROM device1;")s
    add_data(device, type, value, timestamp)


    print("Data inserted:")
    data = cursor.execute("SELECT * FROM device1")
    for row in data:
        print(row)

    conn.commit()
    conn.close()

# Handle errors
except sqlite3.Error as error:
    print('Error occurred - ', error)

# Close DB Connection irrespective of success
# or failure
finally:
   
    if conn:
        conn.close()
        print('SQLite Connection closed')



