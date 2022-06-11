import base64
from google.cloud import storage
import os
from dateutil import parser, tz
from datetime import datetime,timedelta

import tempfile


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'

os.listdir()

def save_to_cloud(mqtt_data):
    FILE_PREFIX = "EnergyData"
    BUCKET_NAME = "mqtt_data_1"
    FILE_TYPE = "txt"
    TEMP_DIR = tempfile.gettempdir()


    storage_client = storage.Client()                   # get client session
    bucket = storage_client.get_bucket(BUCKET_NAME)     # Get bucket
    # check to see where new data should be written to by
    # getting the date from the filename of the last file and check if now's date matches the file date
    list_of_filenames = list_blobs(BUCKET_NAME)
    TIMEZONE = "GMT+2"
    todays_date = datetime.now(tz=tz.tzstr(TIMEZONE))
    # todays_date += timedelta(days=1)
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
        upload_filename = filename

    elif file_exists:
        print("Existing files exist. Looking for most recent file")
        last_blob_filename = list_of_target_filenames[-1]                      # get last file
        # last_blob_filename=  "EnergyData_2022-06-11"
        last_blob_date = last_blob_filename.split("_")[1].split(".")[0]   # extract the data string
        last_date = parser.parse(last_blob_date)            # parse string into date
        file_path = f"{TEMP_DIR}/{last_blob_filename}"


        # if days does not match, create new file with current date to it, add the data to that file and upload it
        if last_date.day < todays_date.day:             # check if today's day is the same as the files date
            # days are different, this should only trigger when first implemented and at midnight

            todays_date_string = todays_date.strftime("%Y-%m-%d")

            filename = f'{FILE_PREFIX}_{todays_date_string}.{FILE_TYPE}'    # build filename string
            file_path = f"{TEMP_DIR}/{filename}"
            print(f"Most recent file does not match today's date. Creating a file for new day. Writing to file: {file_path}")
            with open(file_path,"w") as file:                        # create new file with todays date
                file.write(mqtt_data)                                # write data to file

            upload_filename = filename


        # if it matches, download that file, append new data to it and re-upload the file
        elif last_date.day == todays_date.day:

            last_day_blob = bucket.get_blob(last_blob_filename)
            last_day_blob.download_to_filename(file_path)
            # filename = f'{last_blob_filename}'
            # file_path = f"{TEMP_DIR}/{filename}"
            print(f"Most recent file matches today's date. Writing to existing file: {file_path}")
            with open(file_path, 'a') as file:
                file.write('\n')
                file.write(mqtt_data)
            upload_filename = f"{last_blob_filename}"

    print(f"Uploading file: {upload_filename}")
    blob = bucket.blob(upload_filename)              # convert file to blob
    blob.upload_from_filename(file_path)       # upload file to bucket





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



def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    save_to_cloud(pubsub_message)

    print(pubsub_message)
