#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <display_manager.h>
#include <Arduino.h>
#include <network_manager.h>

WiFiClient espClient;
PubSubClient client(espClient);
// long lastMsg = 0;
// char msg[50];

void setup_wifi() {
  delay(1000);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WLAN_SSID);
  addText("WIFI_STATE", "Connecting to wifi", ORANGE);

  WiFi.begin(WLAN_SSID, WLAN_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    manageDisplay();
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  client.setServer(HOST, PORT);
  client.setCallback(callback);
  //client.subscribe(TOPIC);

  addText("WIFI_STATE", "Connected!", GREEN);
}

//callback for when a message arrives
void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();
}

void update_wifi(){
  //reconnect to wifi if needed
  if (!client.connected()) {
      reconnect();
  }
  client.loop();
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    addText("WIFI_STATE", "Connecting to MQTT...", ORANGE);
    // Attempt to connect
    if (client.connect(CLIENT_ID)) {
      Serial.println("connected");
      // Subscribe
      //client.subscribe(TOPIC);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      manageDisplay();
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
  addText("WIFI_STATE", "Connected to MQTT server", GREEN);
}

void publishToMQTT(const char* topic, const char* message){
  client.publish(topic,message);
}

