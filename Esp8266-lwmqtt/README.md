# ESP8266 firmware

---


To modify script for your Google Cloud account and Wifi network, in
`ciotc_config.h` change: 

**ssid** = "Your Wifi SSID"; <br>
**password** = "Your wifi password";<br>

Cloud iot details. This can be found under the `IoT Core` tab on your Google Cloud Platform  <br>
**project_id** = "the nane you gave it - unique numbers assigned to it"     <br>
**location** = "europe-west1" or "us-central1"                              <br>
**registry_id** = "the name you gave it"                                    <br>
**device_id** = "the name you gave it"                                      <br>

**private_key[]** = {0x00, format} paste <ins>private key</ins> generated using `Create_Eliptic_device_keys.sh`. 
Use `Convert.py` script to quickly convert the output to the correct format <br>

Remember to add the **public key** (found in ) to the device authentication key found in `IoT Core` => `"Your Registry ID"` 
=> `Devices` => `"Your Device ID"` => `
AUTHENTICATION`. Select `ES256` and paste the key <br>

It should look something like <br>
`-----BEGIN PUBLIC KEY-----` <br>
`MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE5O9a2jM7Eo2KUkr95EGCoLZzGGVz`<br>
`TEJzgGymRLfEx9gPtyf5aN50qMGhjSfs4gxuxXUUZBi7kokcwky305cTqw==`<br>
`-----END PUBLIC KEY-----` <br>

