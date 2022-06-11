from os import listdir
import pandas as pd
from google.cloud import storage
import os
from dateutil import parser,tz
from datetime import datetime,timedelta


import csv

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'

def process_cloud_files():
    listOfFiles = listdir("MQTT_data")

    DATA = pd.DataFrame()
    count = 0
    # for filename in listOfFiles:

    for filename in listOfFiles:
        with open(f"MQTT_data/{filename}","r") as file:
            print(filename)
            V = []
            F = []
            P = []
            S = []
            E = []

            numberOfBlanks = 0
            data = file.read().split("\n")[:-1]
            length = len(data)
            for i,k in enumerate(data):
                try:
                    d = k.split(";")
                    # print(d)
                    if len(d) <=5:
                        continue
                    V.append(float(d[0].split(" ")[1]))
                    F.append(float(d[1].split(" ")[1]))
                    P.append(float(d[2].split(" ")[1]))
                    S.append(float(d[3].split(" ")[1]))
                    E.append(float(d[4].split(" ")[1]))

                except:
                    numberOfBlanks +=1
                    print("ERRROOOSSS!!!!!")




            date = filename.split("_data")[1].split("-")
            year = int(date[0])
            month = int(date[1])
            day = int(date[2].split("T")[0])
            hour = int(date[2].split("T")[1])
            minitute = int(date[3])
            sec = int(date[4].split(".")[0])

            date_list = [str(datetime(year, month, day, hour, minitute, sec) + timedelta(seconds=300 / length * x)) for x in range(0, len(V))]

            # print(f"{len(V)} {len(F)} {len(P)} {len(S)} {len(E)}")
            q = pd.to_datetime(date_list)
            q = q.to_frame(index=False, name='DateTime')

            q["Voltage"] = V
            q["Frequency"] = F
            q["Active Power"] = P
            q["Apparent Power"] = S
            q["Energy"] = E

            DATA = pd.concat([DATA, q], axis=0)
            count +=1

    DATA.to_csv("Processes_data.csv")


def get_cloud_files():
    storage_client = storage.Client()
    listOffileNames = list_blobs("mqtt_data")
    bucket_name = "mqtt_data"
    bucket = storage_client.bucket(bucket_name)
    for file in listOffileNames:
        print(f"Working on blob {file}")
        newFileName = file.split("Z")[0].replace(":", "-").split(".")[0]
        source_blob_name = file
        blob = bucket.blob(source_blob_name)
        destination_file_name = f"MQTT_data/{newFileName}.txt"
        blob.download_to_filename(destination_file_name)
        print("Donwload completed")



def list_blobs(bucket_name,folder=None,_prefix =None,_delimiter = None ):
    """Lists all the blobs in the bucket."""
    # Instantiates a client
    storage_client = storage.Client()
    # Get GCS bucket
    bucket = storage_client.get_bucket(bucket_name)
    # Get blobs in bucket (including all subdirectories)
    blobs = list(bucket.list_blobs(prefix=_prefix,delimiter=_delimiter))

    listOffileNames = [blob.name for blob in blobs]
    return listOffileNames

def bucket_metadata(bucket_name):
    """Prints out a bucket's metadata."""
    # bucket_name = 'your-bucket-name'

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    print(f"ID: {bucket.id}")
    print(f"Name: {bucket.name}")
    print(f"Storage Class: {bucket.storage_class}")
    print(f"Location: {bucket.location}")
    print(f"Location Type: {bucket.location_type}")
    print(f"Cors: {bucket.cors}")
    print(f"Default Event Based Hold: {bucket.default_event_based_hold}")
    print(f"Default KMS Key Name: {bucket.default_kms_key_name}")
    print(f"Metageneration: {bucket.metageneration}")
    print(
        f"Public Access Prevention: {bucket.iam_configuration.public_access_prevention}"
    )
    print(f"Retention Effective Time: {bucket.retention_policy_effective_time}")
    print(f"Retention Period: {bucket.retention_period}")
    print(f"Retention Policy Locked: {bucket.retention_policy_locked}")
    print(f"Requester Pays: {bucket.requester_pays}")
    print(f"Self Link: {bucket.self_link}")
    print(f"Time Created: {bucket.time_created}")
    print(f"Versioning Enabled: {bucket.versioning_enabled}")
    print(f"Labels: {bucket.labels}")

def plot_data():


    data = pd.read_csv("Processes_data.csv", header=0, infer_datetime_format=True,
                       parse_dates=['DateTime'], index_col=['DateTime'], dtype="float")

    q = data.values


def list_buckets():
    """Lists all buckets."""

    storage_client = storage.Client()
    buckets = storage_client.list_buckets()

    for bucket in buckets:
        print(bucket.name)

def create_bucket(mqtt_data):
    FILE_PREFIX = "EnergyData"
    BUCKET_NAME = "mqtt_data_1"
    FILE_TYPE = ".txt"


    storage_client = storage.Client()                   # get client session
    bucket = storage_client.get_bucket(BUCKET_NAME)     # Get bucket

    # check to see where new data should be written to by
    # getting the date from the filename of the last file and check if now's date matches the file date

    blobs = list_blobs(BUCKET_NAME)

    TIMEZONE = "GMT+2"
    todays_date = datetime.now(tz=tz.tzstr(TIMEZONE))
    # todays_date = todays_date + timedelta(days=1)

    # first list all the blobs
    if not FILE_PREFIX in blobs:            # if there are no files in the bucket with FILE_PREFIX, then create a new file

        todays_date_string = todays_date.strftime("%Y-%m-%d")

        new_filename = f'/tmp/{FILE_PREFIX}_{todays_date_string}.{FILE_TYPE}'  # build filename string
        print(f"No existing files have been found. Creating new file: {new_filename}")
        with open(new_filename, "w") as file:  # create new file with todays date
            file.writelines(mqtt_data)
        upload_filename = new_filename

    elif FILE_PREFIX in blobs:
        print("Looking for existing file")
        last_blob_filename = blobs[-1]                      # get last file
        # last_blob_filename=  "EnergyData_2022-06-11"
        last_blob_date = last_blob_filename.split("_")[1]   # extract the data string
        last_date = parser.parse(last_blob_date)            # parse string into date


        # if days does not match, create new file with current date to it, add the data to that file and upload it
        if last_date.day < todays_date.day:             # check if today's day is the same as the files date
            # days are different, this should only trigger when first implemented and at midnight

            todays_date_string = todays_date.strftime("%Y-%m-%d")

            new_filename = f'/tmp/{FILE_PREFIX}_{todays_date_string}.{FILE_TYPE}'    # build filename string
            print(f"Writing to file: {new_filename}")
            with open(new_filename,"w") as file:                        # create new file with todays date
                file.writelines(mqtt_data)                             # write data to file

            upload_filename = new_filename


        # if it matches, download that file, append new data to it and re-upload the file
        elif last_date.day == todays_date.day:

            last_day_blob_ = bucket.get_blob(last_blob_filename)
            last_day_blob_.download_to_filename(f"/tmp/{last_blob_filename}")
            filename = f'/tmp/{last_blob_filename}.{FILE_TYPE}'
            print(f"Dates matched. Wrting to existing file: {filename}")
            with open(filename, 'a') as file:
                file.writelines(mqtt_data)
            upload_filename = f"{last_blob_filename}.{FILE_TYPE}"

    print(f"Uploading file: {upload_filename}")
    blob = bucket.blob(f"/tmp/{upload_filename}")              # convert file to blob
    blob.upload_from_filename(upload_filename)       # upload file to bucket









if __name__ == "__main__":
    # blobs = list_blobs("mqtt_data_1")
    # # Get blobs in specific subirectory
    # lastFileName = blobs[-2]

    data = "227.702 ;50 ;2977.57 ;2977.69 ;552.393 ;1654772376"
    create_bucket(data)

