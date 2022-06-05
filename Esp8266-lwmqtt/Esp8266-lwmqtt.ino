#include <SoftwareSerial.h>   // ESP Software Serial
#include <stdio.h>

int postFrequency             = 5000;     // default posting frequency

#define RE        16  //D0      //MAX485 Receiver Enable pin 
#define DE        5   //D1      //MAX485 Output Driver Enable pin 
#define RX        4   //D2     
#define TX        0   //D3  

#define UInt16    uint16_t

SoftwareSerial softSerial;


// Built in LED used for debugging without terminal. Both LEDs turn on when initialisation is successful    
#define LED_1 2            // LED 1 turns off when communicating with energy meter. Normal operation LED will flash
#define LED_2 16              

#if defined(ARDUINO_SAMD_MKR1000) or defined(ESP32)
#define __SKIP_ESP8266__
#endif

#if defined(ESP8266)
#define __ESP8266_MQTT__
#endif

#ifdef __SKIP_ESP8266__

#include <Arduino.h>

void setup(){
  Serial.begin(115200);
}

void loop(){
  Serial.println("Hello World");
}

#endif

#ifdef __ESP8266_MQTT__
#include <CloudIoTCore.h>
#include "esp8266_mqtt.h"

// ------------------------ VARIABLES------------------------------------

String mqqt_message_payload = "";

char voltage_A_line_neutral[] = {0x01,0x04,0x00,0x00,0x00,0x02,0x71,0xCB};
char frequency[]              = {0x01,0x04,0x00,0x46,0x00,0x02,0x90,0x1E};
char current[]                = {0x01,0x04,0x00,0x06,0x00,0x02,0x91,0xCA};
char real_power[]             = {0x01,0x04,0x00,0x0C,0x00,0x02,0xB1,0xC8};
char apparent_power[]         = {0x01,0x04,0x00,0x12,0x00,0x02,0xD1,0xCE};
char active_energy_Import[]   = {0x01,0x04,0x00,0x48,0x00,0x02,0xF1,0xDD};
String current_unix_time      = "";

static unsigned long lastMillis = 0;

//--------------------------------------------------------------------------

// union used to convert data types, ie bytes to float
union 
    {
    byte asBytes[4];
    float asFloat;
    long asLong;
    double asDouble;
    } data; 

void flash_LED(int LedNumber,int flashTimes,int Speed){

  bool state = 0;
  for (int i = 0;i<2*flashTimes;i++){
      delay(Speed);
      digitalWrite(DE,!state);
      delay(Speed);
        }
}

//---------------------    SETUP  -----------------------------------------------

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(19200);
  setupCloudIoT(); // Creates globals for MQTT
  pinMode(LED_1, OUTPUT);
  digitalWrite(LED_1,1);
//  pinMode(LED_2, OUTPUT);
//  digitalWrite(LED_2,1);

  softSerial.begin(19200, SWSERIAL_8N1, RX, TX, false);
  
  pinMode(RE,OUTPUT);
  pinMode(DE,OUTPUT);

//  Enable trancever listening
  digitalWrite(RE,0);
  digitalWrite(DE,0);

  Serial.println("Meter has staterd");
}

// -----------------  MAIN LOOP ---------------------------------------------

void loop()
{
  if (!mqtt->loop())
  {
    mqtt->mqttConnect();                                            
  }

  delay(100);                                                         // delay fixes some issues with WiFi stability
  flash_LED(LED_1,2,50);
  
  if (millis() - lastMillis > postFrequency)                          // check if the last time a payload was sent was longer than x miliseconds ago
  {
    digitalWrite(LED_1,1);                                           // Debug LED 1 - Turns ON when successfully connected to Wifi 
    
    current_unix_time = intToString( time(nullptr));                 // Debug LED 2 - Turns ON when successfully connected MQTT server
    Serial.println(current_unix_time);
    
    mqqt_message_payload = "";                                       // Clears the message payload 
    send(voltage_A_line_neutral,sizeof(voltage_A_line_neutral),"V");
    send(frequency,sizeof(frequency),"f");  
    send(real_power,sizeof(real_power),"P");  
    send(apparent_power,sizeof(apparent_power),"S");  
    send(active_energy_Import,sizeof(active_energy_Import),"E");  
    mqqt_message_payload += current_unix_time;                        // adds unix time to msg payload
    //Serial.println(mqqt_message_payload);                           // debug message
    publishTelemetry(mqqt_message_payload);                           // Sends data to cloud MQTT server
    mqqt_message_payload = "";                                        // Clears the message payload buffer for the next round
    delay(10);      
    digitalWrite(LED_1,0);                                            // Turns debug LED ON to indicate energy coms completed
    lastMillis = millis();                                            // setups the last time a payload was sent
    
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
  sprintf(string, "%d", number); // can also use itoa
  return string;
}


// Reverses the byte order and uses the union operator to convert from byte to float
float bytesArr_to_float(char *serialBuffer){    
  // reverse the order because Adruino Nano & ESP 8266 is Little-Endian
  for(int i = 0; i< 4; i++) data.asBytes[i] = serialBuffer[6-i];  
  return data.asFloat;
}

// sends commands to energy meter and automatically listens for response. Watchdog timer 
void send(char *data, int len, String type){
  ESP.wdtDisable();   // disables WDT. Not sure if it does what it intends, but sometimes serial operation is interupted which leads to data loss. 
  
  // Receiver Output Enable(RE) active LOW
  // Driver Output Enable (DE) active HIGH
  // To write, pull DE and RE HIGH 

  bool state = 1;
  
  digitalWrite(RE,state);                       //RE high = disable 
  digitalWrite(DE,state);                       //DE high = enabled so that it can stop listening and transmit
  softSerial.write(data,len);                                    
  digitalWrite(RE,!state);                     //RE low = enabled - so that it can listen for the reply
  digitalWrite(DE,!state);                     //DE low = disabled
  receive(type);                                // listens for response
  ESP.wdtEnable(0);
}


void receive(String type){
  char serialBuffer[9];
  int i = 0;
  delay(20);                      //wait a bit for the meter to respond
  // Receives MODBUS data
  if (softSerial.available() > 0 )              // Check if bytes has been received, if it has, enter while loop and read all bytes
  {                                             // usually a terminating byte is needed as the while loop reads bytes faster than its received which causes the while  
                                                // condition to become false since there is no more bytes in the RX buffer. But this works as is. 
    //SDM230 replies with 9 bytes      
    //The first 3 bytes are overhead stuff
    //Next 4 bytes is - Data of type float
    //Last 2 bytes is modbus CRC16
    
    memset(serialBuffer, 0, 10);                // Clear the receiving buffer    
    lastMillis = millis();                      // setups timer to exit while loop or else WTD will reset the ESP
   
    while(softSerial.available() > 0 )         // read all bytes for the RX buffer
    {
      serialBuffer[i] = softSerial.read();
      //Serial.println(serialBuffer[i],HEX);   //debug, print as bytes   
      i++;

      if (millis() - lastMillis > 100)        // exists while loop iif it gets stuck
        {
          //flash_LED(LED_2,5,50);
          Serial.println("Stuck in the while loop");
          break;
        }
    }
   
    float value = bytesArr_to_float( serialBuffer );    //convert data to float
    String dataMetric = floatToString(value);           // converts float to String 
    
    mqqt_message_payload += dataMetric + " ;" ;         // builds the paidload string
    
    //Serial.println(type +": " +  dataMetric + ";" );  // for debugging
  }

  // delay gives the energy meter time to process the next command. Meter does not respond if there is no delay
  delay(50);
}



#endif
