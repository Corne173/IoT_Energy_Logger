# How to setup Cloud Function

---

<br>

- ### Get the credentials file used for authentication
    - Firstly, complete the OAuth screen, found in the `APIs & Services` tab. The **Scopes** are the level of access you allow 
    you service account user. For this specific case only add <>
    - Create a `Service Account` found under the `IAM & Admin` tab and makes sure
    to give the `role` of "Owner"(found under the "Basic" list). 
    - Navigate into the newly created service account, goto the `KEYS` tab and add a
    `JSON` key. 
    - Download the json file. The content of this file will be used when creating the cloud function
- ### Create `Cloud Function`
  - Navigate to the `Cloud Function` tab
  - `+ CREATE FUNCTION`
    - Basics
      - Environment : 1st gen
      - Function name : Of your choice
      - Region: Closest to you. 
    - Trigger 
      - Trigger type : Cloud Pub/Sub
      - Select your topic for the drop down menu
    - Runtime,build, connections and security
      - Memory allocated : 256MB
      - Timeout : 10s (it's a quick operation) 
      - Runtime service account : Select the one you created when you got the
      credentials json file. 
      - Autoscaling - Max number of instances : 2- you may need to add more if you're posting frequency is higher than 
      the default (5s)
    - Code
      - Runtime: Python 3.8 (using 3.9+ can lead to some unpredictable behaviour and dependency issues)
      - Source code: Inline Editor
      - Copy the contents of `main.py` of this repository into the `main.py` of the 
      cloud function
      - Do the same for the `requirements.txt` file
      - Create a new file but clicking on the plus sign (+), name it 
      `service_account.json` and copy the content of the credential json file in 
      this new file.
      - Deploy and confirm proper operation. If you get a red tic, it's a syntax error or build error. 
      Check logs to troubleshoot runtime errors.
      
- ### Summnary
  - Before deploying the cloud function, verify that there are 3 files:
    - The `main.py` file containing the google cloud API code
    - `Requirements.txt` file containing 2 items
    - `service_account.json` file which contains the credentials obtained when adding a 
    new `key` to the service account

