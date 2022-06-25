#include <stdio.h>
#include <CloudIoTCore.h>
#include "esp8266_mqtt.h"


#define RESET_PIN 14 //D5

// Built in LED used for debugging without terminal. Both LEDs turn on when initialisation is successful    
#define LED_1 2            // LED 1 turns off when communicating with energy meter. Normal operation LED will flash
#define LED_2 16              


// ------------------------ VARIABLES------------------------------------


static unsigned long lastMillis = 0;
String current_unix_time      = "";

//---------------------    SETUP  -----------------------------------------------

void setup()
{
  Serial.begin(19200);                                    // for debugging
  setupCloudIoT();                                        // Creates globals for MQTT
  pinMode(LED_1, OUTPUT);
  digitalWrite(LED_1,1);
  pinMode(RESET_PIN, INPUT_PULLUP);

}

// -----------------  MAIN LOOP ---------------------------------------------
void loop()
{
  if (!mqtt->loop())
  {
    mqtt->mqttConnect();
    delay(100);                                            
  }

                                                           // delay fixes some issues with WiFi stability
  
  if (millis() - lastMillis > postFrequency)                          // check if the last time a payload was sent was longer than x miliseconds ago
  {
    digitalWrite(LED_1,1);                                           // Debug LED 1 - Turns ON when successfully connected to Wifi 
    current_unix_time = intToString( time(nullptr));                 // Debug LED 2 - Turns ON when successfully connected MQTT server
    publishTelemetry(current_unix_time);                         // Sends data to cloud MQTT server

    digitalWrite(LED_1,0);                                            // Turns debug LED ON to indicate energy coms completed
    lastMillis = millis();                                            // setups the last time a payload was sent
    
  }
  checkButton();
}

//-------------------- Supporting functions----------------------------------------
// converts float to string
String intToString(int number){
  char string[12]; //size of the number
  sprintf(string, "%d", number); // can also use itoa
  return string;
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
        wm.resetSettings();
        ESP.restart();
      }
    }
  }
}
