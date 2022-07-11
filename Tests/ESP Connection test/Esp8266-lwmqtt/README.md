# ESP8266 Test Firmware

---
Before you flash the firmware, add the details of **your** cloud platform to the `ciotc_config.h` file. Make sure
every detail is correct. It matters
   
    const char* project_id = 
    const char* location = 
    const char* registry_id = 
    const char* device_id = 

Next run `Create_Eliptic_device_keys.sh` file from your terminal. If it doesn't recognise `openssl` as a command, install 
`Git` and add to system path. Copy the public key to the device auth keys, it will only accept EC256. 

I've added `WifiMananger` so that no credentials have to be hardcoded. ESP8266
should boot up broadcast an access point with the following details. 

    SSID:       AutoConnectAP
    Password:   password

Go to the browser and enter `192.168.4.1`. Select your network from the list and enter the password. Check 
your terminal for status. LED should start flashing meaning it is successfully transmitting data. 



