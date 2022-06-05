from os import listdir
import pandas as pd
from datetime import datetime, timedelta
from google.cloud import storage

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



def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"

    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    listOffileNames = [blob.name for blob in blobs]
    return listOffileNames

def plot_data():


    data = pd.read_csv("Processes_data.csv", header=0, infer_datetime_format=True,
                       parse_dates=['DateTime'], index_col=['DateTime'],dtype="float" )

    q = data.values