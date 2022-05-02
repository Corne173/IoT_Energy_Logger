#include <SoftwareSerial.h>




#define RE        16  //D0      //MAX485 Receiver Enable pin 
#define DE        5   //D1      //MAX485 Output Driver Enable pin 
#define RX        4   //D2     
#define TX        0   //D3  

#define UInt16    uint16_t
#define LED       2         // built-in LED



SoftwareSerial softSerial;


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
char voltage_A_line_neutral[] = {0x01,0x04,0x00,0x00,0x00,0x02,0x71,0xCB};
char frequency[]              = {0x01,0x04,0x00,0x46,0x00,0x02,0x90,0x1E};
char current[]                = {0x01,0x04,0x00,0x06,0x00,0x02,0x91,0xCA};
char real_power[]             = {0x01,0x04,0x00,0x0C,0x00,0x02,0xB1,0xC8};
char apparent_power[]         = {0x01,0x04,0x00,0x12,0x00,0x02,0xD1,0xCE};
char active_energy_Import[]   = {0x01,0x04,0x00,0x48,0x00,0x02,0xF1,0xDD};


// Compute the MODBUS RTU CRC
UInt16 ModRTU_CRC(char *buf,int len)
{
  UInt16 crc = 0xFFFF;

  for (int pos = 0; pos < len; pos++) {
    crc ^= (UInt16)buf[pos];          // XOR byte into least sig. byte of crc
    for (int i = 8; i != 0; i--) {    // Loop over each bit
      if ((crc & 0x0001) != 0) {      // If the LSB is set
        crc >>= 1;                    // Shift right and XOR 0xA001
        crc ^= 0xA001;
      }
      else                            // Else LSB is not set
        crc >>= 1;                    // Just shift right
    }
  }
  // Note, this number has low and high bytes swapped, so use it accordingly (or swap bytes)
  crc = (crc & 0x00ff)<<8 | (crc & 0xff00)>>8;
  return crc;  
}

void setup()
{

  pinMode(LED,OUTPUT);
  
  
  //setup serial ports
  softSerial.begin(19200, SWSERIAL_8N1, RX, TX, false);
  Serial.begin(19200);
  while(!Serial);
  
  pinMode(RE,OUTPUT);
  pinMode(DE,OUTPUT);

  //Enable trancever listening
  digitalWrite(RE,0);
  digitalWrite(DE,0);

  Serial.println("Meter has staterd");

}

// Holds the incomming data and is used to convert to float
union 
    {
    byte asBytes[4];
    float asFloat;
    long asLong;
    double asDouble;
    } data; 


void loop()
{

  send(voltage_A_line_neutral,sizeof(voltage_A_line_neutral));
  send(frequency,sizeof(frequency));  
  send(current,sizeof(current));  
  send(real_power,sizeof(real_power));
  send(apparent_power,sizeof(apparent_power));
  send(active_energy_Import,sizeof(active_energy_Import));
  
  while(Serial.available() > 0 )
  {
    ESP.wdtFeed();
    digitalWrite(LED,1); 
    Serial.println("Serial input received");    
    String result = Serial.readString();
    send(voltage_A_line_neutral,sizeof(voltage_A_line_neutral));
    Serial.println(result);
    digitalWrite(LED,0);
    break; 
  }

  receive();
  digitalWrite(LED,1);
  delay(100); // need to wait until the TX buffer has sent all the data - to slow things down  
  digitalWrite(LED,0);  
}

float bytesArr_to_float(char *serialBuffer){    
  // reverse the order because Adruino Nano is Little-Endian
  for(int i = 0; i< 4; i++) data.asBytes[i] = serialBuffer[6-i];  
  return data.asFloat;
}

void send(char *data, int len){
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
  
  receive();
}


void receive(){
  char serialBuffer[9];
  int i = 0;
  // Receives MODBUS data
  if (softSerial.available() > 0 )
  {
    //SDM230 replies with 9 bytes      
    //The first 3 bytes are overhead stuff
    //Next 4 bytes is - Data of type float
    //Last 2 bytes is modbus CRC16
         

    // read all bytes for the RX buffer
    while(softSerial.available() > 0 )
    {
      serialBuffer[i] = softSerial.read();
      //Serial.println(serialBuffer[i],HEX);      
      i++;
    }
    //convert data to float
    bytesArr_to_float(serialBuffer);        
    Serial.println(data.asFloat);
    
    // Clear the buffer    
    memset(serialBuffer, 0, 20);
  }

  // delay give the energy meter time to process the next command. Meter does not respond if there is no delay
  delay(50);
  
}
