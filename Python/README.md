# Python scripts

---
This Python folder contains all the code used to get this project to where it is. As the project and its
functionality evolves, so will the code base. `Python 3.9` is used throughout. Couldnt be bothered debugging
into stability issue with 3.10+. 

## `BigQuery.py`
Contains scripts that:
- Adds data to the bigquery data base
- Reads or queries the database using standard SQL queries
- Creates an interactive plot of the time series data using Plotly.  


## `Cloud Device Management.py`
Contains scripts to managed cloud devices

- Add new devices
  - Creates new device
  - Adds it to registry
- Lost a lot of code. Need to update this file
- Todo:
  - Creates EC keys and adds it to device. Also create the ESP private keys.

## DataConverter.py
Downloads data stored in Google Cloud. This needs an API key to access the API. [Read](https://cloud.google.com/docs/authentication/getting-started)

## Processed_data.csv 
Data currently collected (4 May 2022 to 27 May 2022). Can be plotted and explored 