import base64
from google.cloud import bigquery
import os
import datetime

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'
dataset_id = "BigQuerryStorage"
table_id = "PotchPower"


def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    to_BigQuerry(pubsub_message)


def to_BigQuerry(data):
  data = parse_data(data)
  client = bigquery.Client()
  dataset_ref = client.dataset(dataset_id)
  table_ref = dataset_ref.table(table_id)
  table = client.get_table(table_ref)

  errors = client.insert_rows(table, [data])
  print(errors)


def parse_data(data):
  data = data.split(";")
  print(f"Data len {len(data)}: {data}")
  if len(data) > 6:
      raise Execption("Error: Data contains too many points")
      quit()
  elif len(data) < 6:
      raise Execption("Error: Data contains too few points")
      quit()

  date_time = datetime.datetime.fromtimestamp(int(data[5]) + 60 * 60 * 2)
  json_data = {
    "datetime": str(date_time),
    "V_a" :  float(data[0]),
    "f": float(data[1]),
    "P_t":  float(data[2]),
    "S_t":  float(data[3]),
    "E_t": float(data[4]),
    "Epoch": int(data[5])
  }
  print(json_data)
  return json_data