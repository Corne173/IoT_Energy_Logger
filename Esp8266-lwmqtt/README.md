# ESP8266 firmware

---


~~To modify script for your Google Cloud account and Wifi network, in
`ciotc_config.h` change: <br>
**ssid** = "Your Wifi SSID"; <br>
**password** = "Your wifi password";<br>~~

**WifiManager** manages your wifi credientials. No need to hardcode them. After flashing the ESP, 
connect to the AP, open your browser and enter `192.168.4.1`. Find your network and connect. 
After connecting, your script will run. 

Cloud iot details. This can be found under the `IoT Core` tab on your Google Cloud Platform  <br>
**project_id** = "the nane you gave it - unique numbers assigned to it"     <br>
**location** = "europe-west1" or "us-central1"                              <br>
**registry_id** = "the name you gave it"                                    <br>
**device_id** = "the name you gave it"                                      <br>

**private_key[]** = {0x00,0xf3,..,..} 32 bytes. This private key is an elliptical device keys generated using 
[Generate_ec_device_keys.py](https://github.com/Corne173/IoT_Energy_Logger/blob/master/Python/Cloud%20Device%20Management/Generate_ec_device_keys.py). 
You could also use [generate_keys.sh](https://github.com/Corne173/IoT_Energy_Logger/blob/master/Python/Cloud%20Device%20Management/generate_keys.sh)
but its more of a hassle since you have to convert the format before you can paste in into the Arduino script. 
<br>

Remember to add the **public key**, generated in the process above, to the device authentication key found in `IoT Core` => `"Your Registry ID"` 
=> `Devices` => `"Your Device ID"` => `
AUTHENTICATION`. Select `ES256` and paste the key <br>

It should look something like <br>
`-----BEGIN PUBLIC KEY-----` <br>
`MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE5O9a2jM7Eo2KUkr95EGCoLZzGGVz`<br>
`TEJzgGymRLfEx9gPtyf5aN50qMGhjSfs4gxuxXUUZBi7kokcwky305cTqw==`<br>
`-----END PUBLIC KEY-----` <br>

To test if you have done everything correctly, go to your device in `Cloud Core` and check the **Latest Activity**. 
If it doesn't work, make sure that your project details that were entered into the firmware matches your project details 100%.
