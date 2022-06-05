# IoT-Energy-Logger

---
ESP8266 Modbus MQTT Google Cloud Energy Logger. 



## ESP 8266 - Node MCU
Setup instructions and code found at https://github.com/GoogleCloudPlatform/google-cloud-iot-arduino

Code for Node MCU ESP8266 12E is found in [Esp8266-lwmqtt](https://github.com/Corne173/IoT_Energy_Logger/tree/master/Esp8266-lwmqtt).

Requires Arduino libraries: Search in Library manager <br>
**"Google Cloud IoT Core JWT"** by Gus Class    <br>
**"ESPSoftwareSerial"** by Dirk Kaar    <br>
**"MQTT"** by Joel Gaehwiler    <br>

### NODE MCU1.0 12E Pinout   
Because the pin numbers on the board ARE NOT THE SAME as the internal pin numbers.

![Pinout](https://i0.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-NodeMCU-kit-12-E-pinout-gpio-pin.png?quality=100&strip=all&ssl=1)

Internal pin number referencing is used in Arduino script. See pinout.                              <br>
Pin name  &emsp;  Board number    &emsp;    Internal pin number                                                 <br>
RE &emsp;&emsp;&emsp;&emsp;       16 &emsp;&emsp;&emsp;&emsp;&emsp; &emsp;              D0                                                                  <br>
DE      &emsp;&emsp;&emsp;&emsp;    5     &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;              D1                                                                  <br>
RX   &emsp;&emsp;&emsp;&emsp;      4 &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;           D2                                                                  <br>
TX &emsp;&emsp;&emsp; &emsp;     0 &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;              D3                                                                  <br>



## Energy Meter


[SMD230 Modbus made by Eastron](https://www.aliexpress.com/item/32698830575.html?spm=a2g0o.productlist.0.0.799f2566qN7t5A&algo_pvid=e990826b-f171-4fc6-b30f-6c9e8352ca5d&algo_exp_id=e990826b-f171-4fc6-b30f-6c9e8352ca5d-2&pdp_ext_f=%7B%22sku_id%22%3A%2260671643988%22%7D&pdp_npi=2%40dis%21ZAR%21%21621.51%21621.51%21%21%21%21%402103399116544212040123485e3ca8%2160671643988%21sea)

![SMD230 Product sheet](https://ae01.alicdn.com/kf/HTB1MM.XKFXXXXX3XVXXq6xXFXXXj/201669291/HTB1MM.XKFXXXXX3XVXXq6xXFXXXj.jpg?size=136937&height=1067&width=1000&hash=ccb6c38d63b40e63e373261727f7feaf)

## Current Issues 

- There is still an Interrupt Service Routine(ISR) that interrupts serial processes which leads to data loss. 
Not sure how to disable an ESP 8266's global ISR or whether moving away from Software Serial will help?
- Using the `DataFlow` service is very expensive especially at sub minute data collection interval. 
- `DataFlow` is required as it acts as a `pipeline` from the `PubSub` Topic data to `Cloud Storage`.
As it uses a Virtual Machine to accomplish this, you are charge for the time you use this VM. 

## Future Work
- Move away from `DataFlow` service and create a local MQTT server using a **Raspberry Pi** and **Node Red**. 
- Will still use `Google Cloud` service or some other free(ish) SQL server. 
- Add a web server that displays current and past energy usage. 
