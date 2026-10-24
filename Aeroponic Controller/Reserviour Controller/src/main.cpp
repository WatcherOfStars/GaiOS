#include <Adafruit_AHTX0.h>

#include <OneWireNg.h>

//#include <Time.h>
#include <Arduino.h>
#include <ArduinoJson.h>

#include <SPI.h>

#include <display_manager.h>
#include <water_temp_sensor.h>
#include <network_manager.h>
#include <TDS_sensor.h>
#include <pressure_transducer.h>

//==============MESSAGING VARS==============
const int message_time = 1; //time in seconds between messages
float last_message_time = 0;


//==============AEROPONICS VARS==============
const int PUMP_CTL_PIN = 0; //to control inflow pumps

float shutoff_pressure = 82; //psi, pressure at which to shut off pumps
float pressure_hysteresis = 5; //psi, pressure below shutoff_pressure at which to turn pumps back on

bool pumps_on = false;

CQRobotTDS tds(2, 5.0); //TDS sensor on pin 12, 5V reference
PressureTransducer pressure_sensor(1); //pressure sensor on pin 8
WaterTempSensor water_temp_sensor(3); //water temp sensor on pin 13

//==============SENSOR PINS==============
Adafruit_AHTX0 aht; //humidity and temp


void setup() 
{
    Serial.begin(9600);

    setupDisplay();

    //aeroponics setup
    //pinMode(FLOW_PIN, OUTPUT);
    pinMode(PUMP_CTL_PIN, OUTPUT);
    
    if (! aht.begin()) {
        Serial.println("Could not find AHT. Check wiring.");
        while (1) delay(10);
    }
    Serial.println("AHT10 or AHT20 found.");

    last_message_time = millis()/1000.0;

    //wifi setup
    setup_wifi();
    

}

void manageSystem(){
  float current_time = millis()/1000.0;

  //manage inflow from reservoir to pressure tank
  if(pressure_sensor.readPressure() >= shutoff_pressure){ //if pressure high, turn off pumps
    pumps_on = false;
    addText("PUMP_STATE", "PUMPS_OFF", RED);
    digitalWrite(PUMP_CTL_PIN, LOW);
  }
  else if(pressure_sensor.readPressure() <= shutoff_pressure-pressure_hysteresis){ //if pressure low and buffer time past, turn on pumps
    pumps_on = true;
    digitalWrite(PUMP_CTL_PIN, HIGH);
    addText("PUMP_STATE", "PUMPS_ON", GREEN);
  }

  //read temp
  double temperature = water_temp_sensor.readTemperature();
  char wtr_temp[32];
  dtostrf(temperature, 7, 2, wtr_temp);
  addText("WATER_TEMP", wtr_temp, BLUE);

  //read TDS
  double TDS_val = tds.update(temperature);
  char tds_str[32];
  dtostrf(TDS_val, 7, 2, tds_str);
  addText("TDS", tds_str, BLUE);

  //read pressure
  double pressure = pressure_sensor.readPressure();
  char pressure_str[32];
  dtostrf(pressure, 7, 2, pressure_str);
  addText("PRESSURE", pressure_str, BLUE);

  //read humidity and air temperature
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);
  char humidity_str[32];
  dtostrf(humidity.relative_humidity, 7, 2, humidity_str);
  addText("HUMIDITY", humidity_str, BLUE);
  char air_temp_str[32];
  dtostrf(temp.temperature, 7, 2, air_temp_str);
  addText("AIR_TEMP", air_temp_str, BLUE);

  manageDisplay();
}

void publishDataIndividual(String type, String value){
  //set up json and add timestamp
  char buffer[10];
  char message[256];
  JsonDocument doc;

  doc["time"] = millis()/60000.0;

  //add device data
  doc["user"] = DEVICE_USER;
  doc["device_name"] = DEVICE_NAME;

  //add sensor data
  doc["type"] = type;
  doc["value"] = value;

  //send the data
  serializeJson(doc,message);
  //Serial.println(message);
  publishToMQTT(TOPIC, message);
}

void publishData(){
  JsonDocument doc;
  doc["time"] = millis()/60000.0;

  //add device data
  doc["user"] = DEVICE_USER;
  doc["device_name"] = DEVICE_NAME;

  //get sensor vals
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);

  //add sensor data
  doc["water_temperature"] = water_temp_sensor.readTemperature();
  doc["TDS"] = tds.update(water_temp_sensor.readTemperature());
  doc["pressure"] = pressure_sensor.readPressure();
  doc["humidity"] = humidity.relative_humidity;
  doc["air_temperature"] = temp.temperature;
  doc["pump_state"] = pumps_on;


  //send the data
  char message[256];
  serializeJson(doc,message);
  Serial.println(message);
  publishToMQTT(TOPIC, message);
}

void loop() 
{
    update_wifi();

    float current_time = millis()/1000.0;

    //publish data if it is time
    if(current_time-last_message_time >= message_time){
      last_message_time = current_time;
      Serial.println("PUBLISHING");
      publishData();
    }

    manageSystem();

    delay(2000);
}


