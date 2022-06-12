import base64
from google.cloud import storage
import os
from dateutil import parser, tz
from datetime import datetime,timedelta
import tempfile


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'        # sets environment variable to the credentails file
FILE_PREFIX = "EnergyData"           # the name all files will share
BUCKET_NAME = "mqtt_data_1"          # the name of you Cloud Storage bucket
FILE_TYPE = "txt"                    # type of file you want to store
TEMP_DIR = tempfile.gettempdir()     # Caveat- Cloud function runs on a Linux machine with limited privileges. The only
                                     # folder that is not restricted is the "/tmp/" folder. Else you wont be able to write files


def save_to_cloud(mqtt_data):

    storage_client = storage.Client()                   # get client session
    bucket = storage_client.get_bucket(BUCKET_NAME)     # Get bucket
    # check to see where new data should be written to by
    # getting the date from the filename of the last file and check if now's date matches the file date
    list_of_filenames = list_blobs(BUCKET_NAME)
    TIMEZONE = "GMT+2"
    todays_date = datetime.now(tz=tz.tzstr(TIMEZONE))   # Correct for time zone incase server is in different time zone

    # create a list of files containing the shared prefix name, incase there are other things in your bucket
    file_exists = False
    list_of_target_filenames = []
    for filename in list_of_filenames:
        if FILE_PREFIX in filename:
            list_of_target_filenames.append(filename)
            file_exists = True  # sets the flag to true when at least one shared prefix is found
    #print(list_of_target_filenames)
    del list_of_filenames  # delete the stuff we dont need to conserve RAM
    if not file_exists:     # if not file with shared prefix is found, create a new file
        todays_date_string = todays_date.strftime("%Y-%m-%d")   #converts datetime obj to string with format

        filename = f'{FILE_PREFIX}_{todays_date_string}.{FILE_TYPE}'  # build filename string
        file_path = f"{TEMP_DIR}/{filename}"
        print(f"No existing files have been found. Creating new file: {file_path}")
        with open(file_path, "w") as file:  # create new file with todays date
            file.write(mqtt_data)
        upload_filename = filename

    elif file_exists:   # if a file or files has bee found, check its date
        print("Existing files exist. Looking for most recent file")
        last_blob_filename = list_of_target_filenames[-1]                      # get last file
        # last_blob_filename=  "EnergyData_2022-06-11"
        last_blob_date = last_blob_filename.split("_")[1].split(".")[0]   # extract the data string
        last_date = parser.parse(last_blob_date)            # parse string into date
        file_path = f"{TEMP_DIR}/{last_blob_filename}"


        # if days do not match, create new file with current date to it, add the data to that file and upload it
        if last_date.day < todays_date.day:             # check if today's day is the same as the files date
            # days are different, this should only trigger at midnight

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
