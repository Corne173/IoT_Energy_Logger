# IoT-Energy-Logger

---
ESP8266 Modbus MQTT Google Cloud Energy Logger. 

## Overview
![Overvew diagram](./Datasheets/System%20Diagram.png)

## Google Cloud platform setup

- APIs to activate:
  - PubSub
  - IoT Core
  - Cloud Storage 
  - DataFlow
  - Compute Engine
- Setup Pub/Sub Topic 
- Setup `DataFlow` pipeline from MQTT payload to Cloud Storage
    - "Create a new job from Template"
    - Give it a name, select a regionand select the template `Pub/Sub to Text Files on Cloud Storage`
    - Required parameters:
      - The **Pub/Sub topic name** can be found under the `Pub/Sub` tab in the left-hand panel. Click on the topic to open it,
      and copy the content of the `Topic name`
      - Assuming you've already created a bucket in `Cloud Storage`, the "output file directory in Cloud storage" must look something like `gs://<yourBucketName>`
      - "Output filename prefix" is the name of the text file
      - For "Temporary Location", just create a folder in your bucket called `temp`. Your location then becomes 
      `gs://<yourBucketName>/temp`
      - `Run Job`, navigate to the Jobs tab in Dataflow and check if the status says Running
      
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
TX &emsp;&emsp;&emsp; &emsp;     0 &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;              D3             <br>
<br>




## Energy Meter

My project was completed using the SDM230 however I would rather recommend using a current transformer based meter such as the 
[SDM120 CT](https://www.aliexpress.com/item/4000107698147.html?spm=a2g0o.store_pc_allProduct.8148356.14.44d911e8DRQ5fK&pdp_npi=2%40dis%21ZAR%21ZAR%20459.88%21ZAR%20459.88%21%21%21%21%21%402103399116550308657151591efc12%2110000000279420919%21sh). 
Inline meters such as the SDM230 requires some rewiring of the distribution board using 16mm^2 wire if you intend on measuring
the main incoming power. This can be a timely exercise and if the terminals are not tight as hell, you can cause a fire as a result of 
the poor connection. 

The SMD120 CT
- requires half the space
- no extra cabling to be purchase
- is much safer as the full load of the house/office doesn't go through it
- is much quicker to install
- you do not have to disconnect the power to the whole building to install it


[SMD230 Modbus made by Eastron](https://www.aliexpress.com/item/32698830575.html?spm=a2g0o.productlist.0.0.799f2566qN7t5A&algo_pvid=e990826b-f171-4fc6-b30f-6c9e8352ca5d&algo_exp_id=e990826b-f171-4fc6-b30f-6c9e8352ca5d-2&pdp_ext_f=%7B%22sku_id%22%3A%2260671643988%22%7D&pdp_npi=2%40dis%21ZAR%21%21621.51%21621.51%21%21%21%21%402103399116544212040123485e3ca8%2160671643988%21sea)

<img alt="SMD230 Product sheet" src="https://ae01.alicdn.com/kf/HTB1MM.XKFXXXXX3XVXXq6xXFXXXj/201669291/HTB1MM.XKFXXXXX3XVXXq6xXFXXXj.jpg?size=136937&amp;height=1067&amp;width=1000&amp;hash=ccb6c38d63b40e63e373261727f7feaf" width="500"/>




## Current Issues 

- There is still an Interrupt Service Routine(ISR) that interrupts serial processes which leads to data loss. 
Not sure how to disable an ESP 8266's global ISR or whether moving away from Software Serial will help?
- Using the `DataFlow` service is very expensive especially at sub minute data collection interval. 
`DataFlow` acts as a `pipeline` from the `PubSub` Topic data to `Cloud Storage`.
As it uses a Virtual Machine to accomplish this, you are charged for the CPU time, RAM and storage that the VM uses.
A better alternative is to use serverless `Cloud Functions`.
- The MODBUS CRC16 calculation in firmware still need to be fixed. Modbus commands are hardcode with CRC already calculated
Its fine for my purposes, but when using a 3 phase energy meter, having the CRC calculation working will save a lot of effort.

## Future Work
- Add local MQTT Server option by means of Raspberry Pi, with either local or cloud storage
- Add a web server/web page that displays current and past energy usage. 
- Add Google shell console commands or Python API to setup Google Cloud Platform faster.
Also less chance to make a mistake or to forget a step.
- Add Wifi manager so that you dont have to hardcode wifi credintials
- Auto setup a new MQTT device - Will take a bit of work to get right
  - Will have to:
    - Modify Wifi manager sketch to give the option to specify details about the device
    - Add another cloud function triggered by HTTP, which creates a new registry(if device is in a different location)
    - Adds a new device to the registry(with given name)
    - Creates private and public keys. Saves public key to server and sends private key over HTTPS
    - Cloud function: 
      - Creates a new bucket for new device
      - Creates new PubSub topic 
      - Creates new cloud function that acts as a pipeline between the PubSub data and cloud storage. OORRRR use the same cloud function pipeline and pass an extra argument to it(the topic name? device name?) that directs the output to the correct bucket.
