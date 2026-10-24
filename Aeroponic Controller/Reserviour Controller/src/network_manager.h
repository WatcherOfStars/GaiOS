//wifi connection data
#define WLAN_SSID         "Melhorn Wifi"//wifi network ssid
#define WLAN_PASS         "Melhorn528"//wifi password

//buffers
#define MQTT_TX_BUFSIZE   1024
#define MQTT_RX_BUFSIZE   1024

// ====================================================== //"10.1.99.175"
#define HOST              "192.168.1.167"
#define PORT              1883
#define CLIENT_ID       "ReserviourController"
// ======================================================

#define TOPIC            "GAIOS_DEVICES"

//DEVICE DATA
#define DEVICE_USER       "GaiOS Prototype V4"
#define DEVICE_NAME       "Reserviour Controller"

void setup_wifi();
void callback(char* topic, byte* message, unsigned int length);
void update_wifi();
void reconnect();
void publishToMQTT(const char* topic, const char* message);