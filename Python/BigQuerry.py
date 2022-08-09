import datetime
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas_gbq
import os
import time

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service_account.json'
dataset_id = "BigQuerryStorage"
table_id = "PotchPower"


## Fetching data from the database via queries


def query_last(number_entries):
    """Fetching the last number of entiers from the database and returns it as a pandas dataframe"""

    credentials = service_account.Credentials.from_service_account_file(
        '../service_account.json',
    )
    query = f"""
        SELECT *
        FROM `BigQuerryStorage.PotchPower`
        ORDER BY Epoch DESC
        LIMIT {number_entries}
    """

    df = pandas_gbq.read_gbq(query, project_id="mqtt-352311", credentials=credentials)
    df.index = pd.to_datetime(df["datetime"])
    del df["datetime"]
    # print(df)
    return df


def query_to_dataframe(max_entries):
    """This is my implementation of a BigQuery query that returns the last <max_entries> in pandas dataframe format.
     It works okay for queries smaller than 10k. Larger than that it starts to suck. Problem is with the dataframe creation
     process. Its very inefficient"""
    client = bigquery.Client()

    query = f"""
        SELECT *
        FROM `BigQuerryStorage.PotchPower`
        ORDER BY Epoch DESC
        LIMIT {max_entries}
    """
    print("Sending query")
    t1 = time.perf_counter_ns()
    query_job = client.query(query)  # Make an API request.
    t2 = time.perf_counter_ns()
    print(f"Query time: {(t2 - t1) * 1e-9}")
    # create empty dataframe
    dfGlobal = pd.DataFrame()
    for row in query_job:
        # Row values can be accessed by field name or index.
        # convert rowdata to pandas dataframe and save the transpose.
        # print(row)
        df = pd.DataFrame(row[:]).T
        # get the keys and save them as the col names
        df.columns = row.keys()
        #append the dataframa
        dfGlobal = pd.concat([dfGlobal, df])

    t3 = time.perf_counter_ns()
    print(f"Query job done: {(t3 - t2) * 1e-9}")
    print("Query complete")
    # convert the index to a datetime object. makes life so much easier later on
    dfGlobal.index = pd.to_datetime(dfGlobal["datetime"])
    #delete the datetime col. dont need it anymore
    del dfGlobal["datetime"]
    # convert the data from strings to numbers
    dfGlobal = dfGlobal[:].apply(pd.to_numeric)
    # print(dfGlobal)
    t4 = time.perf_counter_ns()

    print(f"Dataframe Processing time: {(t4 - t3) * 1e-9}")
    return dfGlobal


## -------- Loading Data into the database ------------------------


def to_BigQuerry(data):
  """Loads data into the BigQuery database. """
  data = parse_data(data)
  client = bigquery.Client()
  dataset_ref = client.dataset(dataset_id)
  table_ref = dataset_ref.table(table_id)
  table = client.get_table(table_ref)

  errors = client.insert_rows(table, [data])
  print(errors)


def parse_data(data):


  data = data.split(";")

  if len(data) > 6:
      raise "Error: Data contains too many points"
      quit()
  elif len(data) < 6:
      raise "Error: Data contains too few points"
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

  return json_data

def csv_to_bigquerry():
    from google.cloud import bigquery
    import pandas

    # Construct a BigQuery client object.
    client = bigquery.Client()

    table_id = "mqtt-352311.BigQuerryStorage.PotchPower"

    dataframe = pandas.read_csv("DATA.csv")


    job_config = bigquery.LoadJobConfig(
        # Specify a (partial) schema. All columns are always written to the
        # table. The schema is used to assist in data type definitions.
        schema=[
            # Specify the type of columns whose type cannot be auto-detected. For
            # example the "title" column uses pandas dtype "object", so its
            # data type is ambiguous.
            bigquery.SchemaField("datetime", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("V_a", bigquery.enums.SqlTypeNames.FLOAT),
            bigquery.SchemaField("f", bigquery.enums.SqlTypeNames.FLOAT),
            bigquery.SchemaField("P_t", bigquery.enums.SqlTypeNames.FLOAT),
            bigquery.SchemaField("S_t", bigquery.enums.SqlTypeNames.FLOAT),
            bigquery.SchemaField("E_t", bigquery.enums.SqlTypeNames.FLOAT),
            bigquery.SchemaField("Epoch", bigquery.enums.SqlTypeNames.FLOAT),
        ],
        # Optionally, set the write disposition. BigQuery appends loaded rows
        # to an existing table by default, but with WRITE_TRUNCATE write
        # disposition it replaces the table with the loaded data.
        write_disposition="WRITE_TRUNCATE",

    )

    job = client.load_table_from_dataframe(
        dataframe, table_id,job_config=job_config
    )  # Make an API request.
    job.result()  # Wait for the job to complete.


def pd_DataFrame_example():
    import datetime

    from google.cloud import bigquery
    import pandas
    import pytz

    # Construct a BigQuery client object.
    client = bigquery.Client()


    table_id = "mqtt-352311.BigQuerryStorage.demo_table"

    records = [
        {
            "title": "The Meaning of Life",
            "release_year": 1983,
            "length_minutes": 112.5,
            "release_date": pytz.timezone("Europe/Paris")
            .localize(datetime.datetime(1983, 5, 9, 13, 0, 0))
            .astimezone(pytz.utc),
            # Assume UTC timezone when a datetime object contains no timezone.
            "dvd_release": datetime.datetime(2002, 1, 22, 7, 0, 0),
        },
        {
            "title": "Monty Python and the Holy Grail",
            "release_year": 1975,
            "length_minutes": 91.5,
            "release_date": pytz.timezone("Europe/London")
            .localize(datetime.datetime(1975, 4, 9, 23, 59, 2))
            .astimezone(pytz.utc),
            "dvd_release": datetime.datetime(2002, 7, 16, 9, 0, 0),
        },
        {
            "title": "Life of Brian",
            "release_year": 1979,
            "length_minutes": 94.25,
            "release_date": pytz.timezone("America/New_York")
            .localize(datetime.datetime(1979, 8, 17, 23, 59, 5))
            .astimezone(pytz.utc),
            "dvd_release": datetime.datetime(2008, 1, 14, 8, 0, 0),
        },
        {
            "title": "And Now for Something Completely Different",
            "release_year": 1971,
            "length_minutes": 88.0,
            "release_date": pytz.timezone("Europe/London")
            .localize(datetime.datetime(1971, 9, 28, 23, 59, 7))
            .astimezone(pytz.utc),
            "dvd_release": datetime.datetime(2003, 10, 22, 10, 0, 0),
        },
    ]
    dataframe = pandas.DataFrame(
        records,
        # In the loaded table, the column order reflects the order of the
        # columns in the DataFrame.
        columns=[
            "title",
            "release_year",
            "length_minutes",
            "release_date",
            "dvd_release",
        ],

        # Optionally, set a named index, which can also be written to the
        # BigQuery table.
        index=pandas.Index(
            ["Q24980", "Q25043", "Q24953", "Q16403"], name="wikidata_id"
        ),
    )
    job_config = bigquery.LoadJobConfig(
        # Specify a (partial) schema. All columns are always written to the
        # table. The schema is used to assist in data type definitions.
        schema=[
            # Specify the type of columns whose type cannot be auto-detected. For
            # example the "title" column uses pandas dtype "object", so its
            # data type is ambiguous.
            bigquery.SchemaField("title", bigquery.enums.SqlTypeNames.STRING),
            # Indexes are written if included in the schema by name.
            bigquery.SchemaField("wikidata_id", bigquery.enums.SqlTypeNames.STRING),
        ],
        # Optionally, set the write disposition. BigQuery appends loaded rows
        # to an existing table by default, but with WRITE_TRUNCATE write
        # disposition it replaces the table with the loaded data.
        write_disposition="WRITE_TRUNCATE",
    )

    job = client.load_table_from_dataframe(
        dataframe, table_id
    )  # Make an API request.
    job.result()  # Wait for the job to complete.

    table = client.get_table(table_id)  # Make an API request.
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), table_id
        )
    )


def CSV_to_bigquery():
    from google.cloud import bigquery

    # Construct a BigQuery client object.
    client = bigquery.Client()

    table_id = "mqtt-352311.BigQuerryStorage.demo_table"

    job_config = bigquery.LoadJobConfig(
        schema=[
                    # Specify the type of columns whose type cannot be auto-detected. For
                    # example the "title" column uses pandas dtype "object", so its
                    # data type is ambiguous.
                    bigquery.SchemaField("datetime", bigquery.enums.SqlTypeNames.STRING),
                    bigquery.SchemaField("V_a", bigquery.enums.SqlTypeNames.FLOAT),
                    bigquery.SchemaField("f", bigquery.enums.SqlTypeNames.FLOAT),
                    bigquery.SchemaField("P_t", bigquery.enums.SqlTypeNames.FLOAT),
                    bigquery.SchemaField("S_t", bigquery.enums.SqlTypeNames.FLOAT),
                    bigquery.SchemaField("E_t", bigquery.enums.SqlTypeNames.FLOAT),
                ],
        # skip_leading_rows=1,
        # The source format defaults to CSV, so the line below is optional.
        source_format=bigquery.SourceFormat.CSV,
        write_disposition="WRITE_TRUNCATE",
    )
    uri = "https://storage.cloud.google.com/mqtt_data_1/DATA.csv"

    load_job = client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )  # Make an API request.

    load_job.result()  # Waits for the job to complete.

    destination_table = client.get_table(table_id)  # Make an API request.
    print("Loaded {} rows.".format(destination_table.num_rows))




if __name__ == "__main__":
    # # csv_to_bigquerry()



    data = query_last(100000)

    import plotly.express as px
    t5 = time.perf_counter_ns()
    fig = px.line(data)
    fig.update_xaxes(rangeslider_visible=True)
    fig.show()
    t6 = time.perf_counter_ns()
    print(f"Displaying processing time: {(t6 - t5) * 1e-9}")



