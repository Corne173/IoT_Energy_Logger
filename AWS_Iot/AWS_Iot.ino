#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "secrets.h"
#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include <SoftwareSerial.h>   // ESP Software Serial
#include <stdio.h>

unsigned long lastMillis = 0;
unsigned long previousMillis = 0;
const long interval = 5000;

#define AWS_IOT_PUBLISH_TOPIC   "esp8266/pub"
#define AWS_IOT_SUBSCRIBE_TOPIC "esp8266/sub"

WiFiClientSecure net;

BearSSL::X509List cert(cacert);
BearSSL::X509List client_crt(client_cert);
BearSSL::PrivateKey key(privkey);

PubSubClient client(net);

time_t now;
time_t nowish = 1510592825;

WiFiManager wifiManager; // WiFiManager object

StaticJsonDocument<400> mqqt_json;

#define RE        16  //D0      //MAX485 Receiver Enable pin 
#define DE        5   //D1      //MAX485 Output Driver Enable pin 
#define RX        4   //D2     
#define TX        0   //D3  

#define UInt16    uint16_t
#define RESET_PIN 14 //D5
SoftwareSerial softSerial;

// Built in LED used for debugging without terminal. Both LEDs turn on when initialisation is successful    
#define LED_1 2            // LED 1 turns off when communicating with energy meter. Normal operation LED will flash
#define LED_2 16    


// union used to convert data types, ie bytes to float
union 
    {
    byte asBytes[4];
    float asFloat;
    long asLong;
    double asDouble;
    } data; 



// ------------------------ VARIABLES------------------------------------

String mqqt_message_payload = "";

/* 
 
    MODBUS Protocol Message Format - 32 bit IEEE 754 floating point format
    A =  Slave address of the SDM230 - Default is 0x01
    B =  Function code - 0x04=Holding Registers, 0x03=Input Registers
    C =  High byte register address
    D =  Low byte register address
    E =  Number of registers to read high byte - usually 0x00
    F =  Number of regsiters to read low byte - usually 0x02 since we onyl want to to read 1 regsiter
    G =  CRC low byte - I dont know why, but its swapped around
    H =  CRC high byte

 */

// List of commands with CRC - could not get the ModRTU_CRC to work so... here we are
//                                A    B    C    D    E    F    G    H
char V_a[]                 = {0x01,0x04,0x00,0x00,0x00,0x02,0x71,0xCB};
char V_b[]                 = {0x01,0x04,0x00,0x02,0x00,0x02,0xD0,0x0B};
char V_c[]                 = {0x01,0x04,0x00,0x04,0x00,0x02,0x30,0x0A};

char P_a[]             = {0x01,0x04,0x00,0x0C,0x00,0x02,0xB1,0xC8};
char P_b[]             = {0x01,0x04,0x00,0x0E,0x00,0x02,0x10,0x08};
char P_c[]             = {0x01,0x04,0x00,0x10,0x00,0x02,0x70,0x0E};

char Q_a[]             = {0x01,0x04,0x00,0x18,0x00,0x02,0xF1,0xCC};
char Q_b[]             = {0x01,0x04,0x00,0x1A,0x00,0x02,0x50,0x0C};
char Q_c[]             = {0x01,0x04,0x00,0x1C,0x00,0x02,0xB0,0x0D};

char S_a[]             = {0x01,0x04,0x00,0x12,0x00,0x02,0xD1,0xCE};
char S_b[]             = {0x01,0x04,0x00,0x14,0x00,0x02,0x31,0xCF};
char S_c[]             = {0x01,0x04,0x00,0x16,0x00,0x02,0x90,0x0F};

char E_a_import[]         = {0x01,0x04,0x01,0x5A,0x00,0x02,0x50,0x24};
char E_b_import[]         = {0x01,0x04,0x01,0x5C,0x00,0x02,0xB0,0x25};
char E_c_import[]         = {0x01,0x04,0x01,0x5E,0x00,0x02,0x11,0xE5};

char E_total_import[]     = {0x01,0x04,0x00,0x48,0x00,0x02,0xF1,0xDD};

char frequency[]              = {0x01,0x04,0x00,0x46,0x00,0x02,0x90,0x1E};

char current[]                = {0x01,0x04,0x00,0x06,0x00,0x02,0x91,0xCA};


String current_unix_time      = "";



void NTPConnect(void)
{
  Serial.print("Setting time using SNTP");
  configTime(TIME_ZONE * 3600, 0 * 3600, "pool.ntp.org", "time.nist.gov");
  now = time(nullptr);
  
  
  while (now < nowish)
  {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println(now);
  Serial.println("done!");
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  Serial.print("Current time: ");
  Serial.print(asctime(&timeinfo));
}


void messageReceived(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Received [");
  Serial.print(topic);
  Serial.print("]: ");
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}


void connectAWS()
{
  delay(3000);
  WiFi.mode(WIFI_STA);
  //WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  //Serial.println(String("Attempting to connect to SSID: ") + String(WIFI_SSID));

  //while (WiFi.status() != WL_CONNECTED)
  //{
   // Serial.print(".");
   // delay(1000);
 // }

  // start WiFiManager
  wifiManager.autoConnect("AutoConnectAP");

  NTPConnect();

  net.setTrustAnchors(&cert);
  net.setClientRSACert(&client_crt, &key);

  client.setServer(MQTT_HOST, 8883);
  client.setCallback(messageReceived);


  Serial.println("Connecting to AWS IOT");

  while (!client.connect(THINGNAME))
  {
    Serial.print(".");
    delay(1000);
  }

  if (!client.connected()) {
    Serial.println("AWS IoT Timeout!");
    return;
  }
  // Subscribe to a topic
  client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);

  Serial.println("AWS IoT Connected!");
}

void publishMessage()
{
 
  char jsonBuffer[512];
  serializeJson(mqqt_json, jsonBuffer); // print to client
  client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}


void setup()
{
  Serial.begin(38400);                                    // for debugging
  softSerial.begin(38400, SWSERIAL_8N1, RX, TX, false);   // UART - MODBUS 

  connectAWS();
  unsigned status;
  pinMode(LED_1, OUTPUT);
  digitalWrite(LED_1,1);
  pinMode(RESET_PIN, INPUT_PULLUP);
//  pinMode(LED_2, OUTPUT);
//  digitalWrite(LED_2,1);

  pinMode(RE,OUTPUT);     //RS485 read enable pin                         
  pinMode(DE,OUTPUT);     //RS485 write enable pin     

//  Enable trancever listening
  digitalWrite(RE,0);
  digitalWrite(DE,0);
}

void loop()
{
  //Serial.println();
  //delay(2000);
  checkButton();
  //now = time(nullptr);

  if (!client.connected())
  {
    connectAWS();
  }
  else
  {
    client.loop();
    if (millis() - lastMillis > 5000)
    {

      digitalWrite(LED_1,1);                                           // Debug LED 1 - Turns ON when successfully connected to Wifi 
      mqqt_json["time"] = String(time(nullptr));                 // Debug LED 2 - Turns ON when successfully connected MQTT server
      
      mqqt_message_payload = "";                                       // Clears the message payload 
      mqqt_json["V_a"] = send(V_a,sizeof(V_a),"V_a");
      mqqt_json["V_b"] = send(V_b,sizeof(V_b),"V_b");                                          // Gets voltage per phase
      mqqt_json["V_c"] = send(V_c,sizeof(V_c),"V_c");

      mqqt_json["P_a"] = send(P_a,sizeof(P_a),"P_a");
      mqqt_json["P_b"] = send(P_b,sizeof(P_b),"P_b");                                          // Gets real power per phase
      mqqt_json["P_c"] = send(P_c,sizeof(P_c),"P_c");

      mqqt_json["Q_a"] = send(Q_a,sizeof(Q_a),"Q_a");
      mqqt_json["Q_b"] = send(Q_b,sizeof(Q_b),"Q_b");                                          // Gets active power 
      mqqt_json["Q_c"] = send(Q_c,sizeof(Q_c),"Q_c");
      
      mqqt_json["E_a"] = send(E_a_import,sizeof(E_a_import),"E_a");
      mqqt_json["E_b"] = send(E_b_import,sizeof(E_b_import),"E_b");                            // Gets energy imported per phase
      mqqt_json["E_c"] = send(E_c_import,sizeof(E_c_import),"E_c");
      
     // mqqt_message_payload += "T: " +  String(intToString( time(nullptr))) + ";";                      // adds unix time to msg payload
      //Serial.println(mqqt_message_payload);
                        // Sends data to cloud MQTT server
      mqqt_message_payload = "";                                        // Clears the message payload buffer for the next round    
      digitalWrite(LED_1,0);                                            // Turns debug LED ON to indicate energy coms completed      

      lastMillis = millis();
      publishMessage();

    }
  }
}

//-------------------- Supporting functions----------------------------------------
// converts float to string
String floatToString(float number){

  char string[10]; //size of the number
  sprintf(string, "%g", number);
  return string;
}

// converts float to string
String intToString(int number){
  char string[12]; //size of the number
  sprintf(string, "%d", number); // can also use itoa. no idea why I didn't. Theres also a method called "String()" that does the same thing. Thank you Ardiuno
  return string;
}

// Reverses the byte order and uses the union operator to convert from byte to float
float bytesArr_to_float(char *serialBuffer){    
  // reverse the order because Adruino Nano & ESP 8266 is Little-Endian
  for(int i = 0; i< 4; i++) data.asBytes[i] = serialBuffer[6-i];  
  return data.asFloat;
}


//--------------------------------- Request DATA from meter ---------------------------------------------
// sends commands to energy meter and automatically listens for response. Watchdog timer 

String send(char *data, int len, String type){
  // Receiver Output Enable(RE) active LOW
  // Driver Output Enable (DE) active HIGH
  // To write, pull DE and RE HIGH 

  bool state = 1;
  
  digitalWrite(RE,state);                       //RE high = disable 
  digitalWrite(DE,state);                       //DE high = enabled so that it can stop listening and transmit
  softSerial.write(data,len);                                    
  digitalWrite(RE,!state);                     //RE low = enabled - so that it can listen for the reply
  digitalWrite(DE,!state);                     //DE low = disabled
  return receive(type);                               // listens for response and returns the response
}


/*void send(char *data, String type){
  // Receiver Output Enable(RE) active LOW
  // Driver Output Enable (DE) active HIGH
  // To write, pull DE and RE HIGH 

  bool state = 1;
  
  digitalWrite(RE,state);                       //RE high = disable 
  digitalWrite(DE,state);                       //DE high = enabled so that it can stop listening and transmit
  softSerial.write(data,strlen(data));                                    
  digitalWrite(RE,!state);                     //RE low = enabled - so that it can listen for the reply
  digitalWrite(DE,!state);                     //DE low = disabled
  receive(type);                               // listens for response
}

*/


//--------------------------------- Listen for DATA from meter ---------------------------------------------
String receive(String type){
  String dataMetric = "";
  char serialBuffer[9];
  int i = 0;
  delay(20);                      //wait a bit for the meter to respond
  // Receives MODBUS data
  if (Serial.available() > 0 )              // Check if bytes has been received, if it has, enter while loop and read all bytes
  {                                             // usually a terminating byte is needed as the while loop reads bytes faster than its received which causes the while  
                                                // condition to become false since there is no more bytes in the RX buffer. But this works as is. 
    //SDM230 replies with 9 bytes      
    //The first 3 bytes are overhead stuff
    //Next 4 bytes is - Data of type float
    //Last 2 bytes is modbus CRC16
    
    memset(serialBuffer, 0, 9);                // Clear the receiving buffer    
    lastMillis = millis();                      // setups timer to exit while loop or else WTD will reset the ESP
   
    while(Serial.available() > 0 )         // read all bytes for the RX buffer
    {
      serialBuffer[i] = Serial.read();
      //Serial.println(serialBuffer[i],HEX);   //debug, print as bytes   
      i++;

      if (millis() - lastMillis > 300)        // exists while loop iif it gets stuck
        {
          //flash_LED(LED_2,5,50);
          Serial.println("Stuck in the while loop");
          break;
        }
    }
   
    float value = bytesArr_to_float( serialBuffer );    //convert data to float
    dataMetric = floatToString(value);           // converts float to String 

    // the "type" is used to create a sudo json type string
    mqqt_message_payload +=  type +": " +  dataMetric + ";" ;         // builds the paidload string
    
    //Serial.println(type +": " +  dataMetric + ";" );  // for debugging
  }

  //Serial.println(data.asFloat);                       // for debugging
  // delay gives the energy meter time to process the next command. Meter does not respond if there is no delay. 50ms results in some errors 
  delay(100);
  return dataMetric;
}


void checkButton(){
  // check for button press
  if ( digitalRead(RESET_PIN) == LOW ) {
    // poor mans debounce/press-hold, code not ideal for production
    delay(50);
    if( digitalRead(RESET_PIN) == LOW ){
      Serial.println("Button Pressed");
      // still holding button for 3000 ms, reset settings, code not ideaa for production
      delay(3000); // reset delay hold
      if( digitalRead(RESET_PIN) == LOW ){
        Serial.println("Button Held");
        Serial.println("Erasing Config, restarting");
        wifiManager.resetSettings();
        ESP.restart();
      }
    }
  }
}

