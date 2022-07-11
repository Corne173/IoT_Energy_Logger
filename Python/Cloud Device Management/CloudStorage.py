from os import listdir
import pandas as pd
from google.cloud import storage
import os
from dateutil import parser,tz
from datetime import datetime,timedelta
import tempfile
import csv
TEMP_DIR = tempfile.gettempdir()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'

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

def save_to_cloud(mqtt_data):
    FILE_PREFIX = "Energy"
    BUCKET_NAME = "mqtt_data_1"
    FILE_TYPE = "txt"
    TEMP_DIR = tempfile.gettempdir()
    DEST_FOLDER = "Braby"

    storage_client = storage.Client()                   # get client session
    bucket = storage_client.get_bucket(BUCKET_NAME)     # Get bucket
    # check to see where new data should be written to by
    # getting the date from the filename of the last file and check if now's date matches the file date
    list_of_filenames = list_blobs(BUCKET_NAME)
    TIMEZONE = "GMT+2"
    todays_date = datetime.now(tz=tz.tzstr(TIMEZONE))
    # todays_date += timedelta(days=1)                  # used for testing
    # first list all the blobs
    file_exists = False
    list_of_target_filenames = []
    for filename in list_of_filenames:
        if FILE_PREFIX in filename:
            list_of_target_filenames.append(filename)
            file_exists = True
    print(list_of_target_filenames)
    del list_of_filenames
    if not file_exists:
        todays_date_string = todays_date.strftime("%Y-%m-%d")

        filename = f'{FILE_PREFIX}_{todays_date_string}.{FILE_TYPE}'  # build filename string
        file_path = f"{TEMP_DIR}/{filename}"
        print(f"No existing files have been found. Creating new file: {file_path}")
        with open(file_path, "w") as file:  # create new file with todays date
            file.write(mqtt_data)
        upload_filename = f"{DEST_FOLDER}/{filename}"

    elif file_exists:
        print("Existing files exist. Looking for most recent file")
        last_blob_filename = list_of_target_filenames[-1]                      # get last file
        # last_blob_filename=  "EnergyData_2022-06-11"
        last_blob_date = last_blob_filename.split("_")[1].split(".")[0]   # extract the data string
        last_date = parser.parse(last_blob_date)            # parse string into date
        file_path = f"{TEMP_DIR}/{last_blob_filename}"


        # if days does not match, create new file with current date to it, add the data to that file and upload it
        if datetime.date(last_date) < datetime.date(todays_date)  :             # check if today's day is the same as the files date
            # days are different, this should only trigger when first implemented and at midnight

            todays_date_string = todays_date.strftime("%Y-%m-%d")

            filename = f'{FILE_PREFIX}_{todays_date_string}.{FILE_TYPE}'    # build filename string
            file_path = f"{TEMP_DIR}/{filename}"
            print(f"Most recent file does not match today's date. Creating a file for new day. Writing to file: {file_path}")
            with open(file_path,"w") as file:                        # create new file with todays date
                file.write(mqtt_data)                                # write data to file

            upload_filename = f"{DEST_FOLDER}/{filename}"


        # if it matches, download that file, append new data to it and re-upload the file
        elif datetime.date(last_date) == datetime.date(todays_date):

            last_day_blob = bucket.get_blob(last_blob_filename)
            print(f"Downloading: {last_blob_filename}")
            temp_name = f"{TEMP_DIR}/{last_blob_filename.split('/')[1]}"
            last_day_blob.download_to_filename(temp_name)
            # filename = f'{last_blob_filename}'
            # file_path = f"{TEMP_DIR}/{filename}"
            print(f"Most recent file matches today's date. Writing to existing file: {file_path}")
            with open(temp_name, 'a') as file:
                file.write('\n')
                file.write(mqtt_data)
            upload_filename = last_blob_filename
            file_path = temp_name

        else:
            raise ("Date comparison error")

    print(f"Uploading file: {upload_filename}")
    blob = bucket.blob(f"{upload_filename}")              # convert file to blob
    blob.upload_from_filename(file_path)       # upload file to bucket









if __name__ == "__main__":
    # blobs = list_blobs("mqtt_data_1")
    # print(blobs)
    # # Get blobs in specific subirectory
    # lastFileName = blobs[-2]

    data = "227.702 ;50 ;2977.57 ;2977.69 ;552.393 ;1654772376"
    save_to_cloud(data)

