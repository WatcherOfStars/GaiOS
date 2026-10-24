#include <Adafruit_AHTX0.h>
#include <addr_latch.h>

#include <OneWireNg.h>

//#include <Time.h>
#include <Arduino.h>
#include <ArduinoJson.h>

#include <SPI.h>

#include <display_manager.h>
#include <network_manager.h>

//==============MESSAGING VARS==============
const int message_time = 5; //time in seconds between messages
float last_message_time = 0;


//==============AEROPONICS VARS==============
float flow_on_time = 15; //seconds
float flow_off_time = 15; //seconds should be 300
float last_change_time = 0;
bool flow_state;
int flow_test_pin = 10; //example pin number for testing

//==============SENSOR PINS==============
Adafruit_AHTX0 aht; //humidity and temp

//==============ADDR LATCH VARS==============
AddrLatch addr_latch;


void setup() 
{
  delay(1000); // wait 1 second before starting setup
  pinMode(flow_test_pin, OUTPUT);
  addr_latch.begin();
  Serial.begin(9600);

  setupDisplay();
  
  // if (! aht.begin()) {
  //     Serial.println("Could not find AHT? Check wiring");
  //     while (1) delay(10);
  // }
  // Serial.println("AHT10 or AHT20 found");

  flow_state = false; // OFF
  last_change_time = millis()/1000.0;
  last_message_time = millis()/1000.0;

  //wifi setup
  setup_wifi();
    

}

void manageSystem(){
  float current_time = millis()/1000.0;

  //manage flow from pressure tank to grow tower
  switch(flow_state){
    case true: //in open mode
      digitalWrite(flow_test_pin, HIGH);
      addr_latch.writeAll(0xFF); //set all outputs high to open valve
      if(current_time-last_change_time >= flow_on_time){ //switch states if needed
        Serial.println("VALVE_CLOSED");
        addText("VALVE_STATE", "VALVE_CLOSED", RED);
        last_change_time = current_time;
        flow_state = false; // OFF
      }
      break;
    case false: //in closed mode
      digitalWrite(flow_test_pin, LOW);
      addr_latch.writeAll(0x00); //set all outputs low to close valve
      if(current_time-last_change_time >= flow_off_time){ //switch states if needed
        Serial.println("VALVE_OPEN");
        addText("VALVE_STATE", "VALVE_OPEN", GREEN);
        last_change_time = current_time;
        flow_state = true; // ON
      }
      break;
  }

  //read humidity and air temperature
  // sensors_event_t humidity, temp;
  // aht.getEvent(&humidity, &temp);
  // char humidity_str[32];
  // dtostrf(humidity.relative_humidity, 7, 2, humidity_str);
  // addText("HUMIDITY", humidity_str, BLUE);
  // Serial.println("Humidity: " + String(humidity.relative_humidity));
  // char air_temp_str[32];
  // dtostrf(temp.temperature, 7, 2, air_temp_str);
  // addText("AIR_TEMP", air_temp_str, BLUE);
  // Serial.println("Air Temp: " + String(temp.temperature));

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
  // sensors_event_t humidity, temp;
  // aht.getEvent(&humidity, &temp);

  //add sensor data
  // doc["humidity"] = humidity.relative_humidity;
  // doc["air_temperature"] = temp.temperature;
  doc["valve_status"] = flow_state; //TODO: change to an array of the 8 valves


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

    delay(200);
}


