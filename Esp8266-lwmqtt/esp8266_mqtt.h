// *****************************************************************************/
// This file contains static methods for API requests using Wifi / MQTT

#include <ESP8266WiFi.h>
#include "FS.h"
#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include "WiFiClientSecureBearSSL.h"
#include <time.h>

#include <MQTT.h>

#include <CloudIoTCore.h>
#include <CloudIoTCoreMqtt.h>
#include "ciotc_config.h" // Wifi configuration here

int postFrequency             = 5000;     // default posting frequency

WiFiManager wm;

// The MQTT callback function for commands and configuration updates
// Place your message handler code here.
void messageReceivedAdvanced(MQTTClient *client, char topic[], char bytes[], int length)
{
  Serial.printf("Incoming Topic: %s", topic);
  if (length > 0)// On message
  {
    Serial.printf("\n\r   Data: %s", bytes);
    postFrequency = atof(bytes);
  }
  Serial.println();
}
///////////////////////////////

// Initialize WiFi and MQTT for this board
static MQTTClient *mqttClient;
static BearSSL::WiFiClientSecure netClient;
static BearSSL::X509List certList;
static CloudIoTCoreDevice device(project_id, location, registry_id, device_id);
CloudIoTCoreMqtt *mqtt;

///////////////////////////////
// Helpers specific to this board
///////////////////////////////
String getDefaultSensor()
{
  return "Wifi: " + String(WiFi.RSSI()) + "db";
}

String getJwt()
{
  // Disable software watchdog as these operations can take a while.
  ESP.wdtDisable();
  time_t iat = time(nullptr);
  Serial.println("Refreshing JWT");
  String jwt = device.createJWT(iat, jwt_exp_secs);
  ESP.wdtEnable(0);
  return jwt;
}

static void readDerCert(const char *filename) {
  File ca = SPIFFS.open(filename, "r");
  if (ca)
  {
    size_t size = ca.size();
    uint8_t cert[size];
    ca.read(cert, size);
    certList.append(cert, size);
    ca.close();

    Serial.print("Success to open ca file ");
  }
  else
  {
    Serial.print("Failed to open ca file ");
  }
  Serial.println(filename);
}

static void setupCertAndPrivateKey()
{
  // Set CA cert on wifi client
  // If using a static (pem) cert, uncomment in ciotc_config.h:
  certList.append(primary_ca);
  certList.append(backup_ca);
  netClient.setTrustAnchors(&certList);

  device.setPrivateKey(private_key);
  return;

  // If using the (preferred) method with the cert and private key in /data (SPIFFS)
  // To get the private key run
  // openssl ec -in <private-key.pem> -outform DER -out private-key.der

  if (!SPIFFS.begin())
  {
    Serial.println("Failed to mount file system");
    return;
  }
  readDerCert("/gtsltsr.crt"); // primary_ca.pem
  readDerCert("/GSR4.crt"); // backup_ca.pem
  netClient.setTrustAnchors(&certList);


  File f = SPIFFS.open("/private-key.der", "r");
  if (f) {
    size_t size = f.size();
    uint8_t data[size];
    f.read(data, size);
    f.close();

    BearSSL::PrivateKey pk(data, size);
    device.setPrivateKey(pk.getEC()->x);

    Serial.println("Success to open private-key.der");
  } else {
    Serial.println("Failed to open private-key.der");
  }
  SPIFFS.end();
}

static void setupWifi()
{
  WiFi.mode(WIFI_STA); // explicitly set mode, esp defaults to STA+AP
  
  bool res;
  res = wm.autoConnect("AutoConnectAP","password"); // password protected ap

  // enters loop and restarts ESP when not connected
  while(!res){ 
    Serial.println("Failed to connect");
    digitalWrite(2,1);
    delay(100);
    digitalWrite(2,0);
    delay(100);
    ESP.restart(); 
}

  // the 2*3600 sets the time zone, +2 GMT
  configTime(2*3600, 0, ntp_primary, ntp_secondary);
  Serial.println("Waiting on time sync...");
  while (time(nullptr) < 1510644967)
  {
    delay(10);
  }
}

///////////////////////////////
// Orchestrates various methods from preceeding code.
///////////////////////////////
bool publishTelemetry(const String &data)
{
  Serial.print("Outcoming: ");
  Serial.println(data);
  return mqtt->publishTelemetry(data);
}

bool publishTelemetry(const char *data, int length)
{
  return mqtt->publishTelemetry(data, length);
}

// TODO: fix globals
void setupCloudIoT()
{
  // ESP8266 WiFi setup
  setupWifi();

  // ESP8266 WiFi secure initialization and device private key
  setupCertAndPrivateKey();

  mqttClient = new MQTTClient(512);
  mqttClient->setOptions(180, true, 1000); // keepAlive, cleanSession, timeout
  mqtt = new CloudIoTCoreMqtt(mqttClient, &netClient, &device);
  mqtt->setUseLts(true);
  mqtt->startMQTTAdvanced(); // Opens connection using advanced callback
}
