/******************************************************************************
 * Copyright 2018 Google
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*****************************************************************************/

#include <SoftwareSerial.h>   // ESP Software Serial

#include <stdio.h>


#define RE        16  //D0      //MAX485 Receiver Enable pin
#define DE        5   //D1      //MAX485 Output Driver Enable pin
#define RX        4   //D2
#define TX        0   //D3

#define UInt16    uint16_t


SoftwareSerial softSerial;

#define payload_lenght 100
#define LED_1 2
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

static unsigned long lastMillis = 0;

//--------------------------------------------------------------------------

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

String toString(float number){

  char string[10]; //size of the number
  sprintf(string, "%g", number);

  return string;
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

  delay(100); // <- fixes some issues with WiFi stability
  flash_LED(LED_1,2,50);

  if (millis() - lastMillis > 1000)
  {
    digitalWrite(LED_1,1);                                            //Debug LED - Turns OFF when communicating with energy meter

    Serial.println(time(nullptr));
    mqqt_message_payload = "";
    send(voltage_A_line_neutral,sizeof(voltage_A_line_neutral),"V");
    send(frequency,sizeof(frequency),"f");
    send(real_power,sizeof(real_power),"P");
    send(apparent_power,sizeof(apparent_power),"S");
    send(active_energy_Import,sizeof(active_energy_Import),"E");

    Serial.println(mqqt_message_payload);
    publishTelemetry(mqqt_message_payload);                           // Sends data to cloud MQTT server
    mqqt_message_payload = "";                 // Clears the message payload buffer for the next round
    delay(10);
    digitalWrite(LED_1,0);
    lastMillis = millis();

  }
}


//-------------------- Supporting functions----------------------------------------

float bytesArr_to_float(char *serialBuffer){
  // reverse the order because Adruino Nano & ESP 8266 is Little-Endian
  for(int i = 0; i< 4; i++) data.asBytes[i] = serialBuffer[6-i];
  return data.asFloat;
}

void send(char *data, int len, String type){
  ESP.wdtDisable();
  // Receiver Output Enable(RE) active LOW
  // Driver Output Enable (DE) active HIGH
  // To write, pull DE and RE HIGH

  bool state = 1;

  digitalWrite(RE,state);
  digitalWrite(DE,state);

  softSerial.write(data,len);

 // Disable output driver and Enable receiver
  digitalWrite(RE,!state);  //RE low = enabled - so that it can listen for the reply
  digitalWrite(DE,!state);  //DE low = disabled

  receive(type);
  ESP.wdtEnable(0);
}


void receive(String type){
  char serialBuffer[9];
  int i = 0;
  delay(20);                      //wait a bit for the meter to respond
  // Receives MODBUS data
  if (softSerial.available() > 0 )
  {

    //SDM230 replies with 9 bytes
    //The first 3 bytes are overhead stuff
    //Next 4 bytes is - Data of type float
    //Last 2 bytes is modbus CRC16

     // Clear the buffer
    memset(serialBuffer, 0, 20);

    lastMillis = millis();
    // read all bytes for the RX buffer
    while(softSerial.available() > 0 )
    {
      serialBuffer[i] = softSerial.read();
      //Serial.println(serialBuffer[i],HEX);
      i++;

      // exists while loop iif it gets stuck
      if (millis() - lastMillis > 100)
        {
          //flash_LED(LED_2,5,50);
          Serial.println("Stuck in the while loop");

        }


    }
    //convert data to float
    float value = bytesArr_to_float( serialBuffer );
    String dataMetric = toString(value);

    mqqt_message_payload += type + ": " + dataMetric + " ;" ;

    Serial.println(type +": " +  dataMetric + ";" );
    //Serial.println(serialBuffer);

  }

  // delay give the energy meter time to process the next command. Meter does not respond if there is no delay
  delay(50);

}



#endif
