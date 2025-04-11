import pyarrow.parquet as pq
import gcsfs
import pandas as pd
from pandas_gbq import to_gbq
import bigframes.pandas as bpd
import json
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import bigquery



PROJECT_ID = 'adsac-455509'
LOCATION = "southamerica-east1" 
service_account_path = 'adsac-455509-0d5538a0d624.json'

bpd.options.bigquery.project = PROJECT_ID
bpd.options.bigquery.location = LOCATION
bpd.options.display.progress_bar = None

def merge_records(service_account_path, destination_table, column_ids, df_new_data):
    #If y}oy have more than one identifier, please split by comma, example 1,2,3
    # Initialize a BigQuery client using the service account key file
    credentials = service_account.Credentials.from_service_account_file(service_account_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    # Load the existing table data into a DataFrame
    query = f"SELECT {column_ids} FROM {destination_table}"
    existing_data = client.query(query).to_dataframe()

    # Check for duplicates based on the unique identifier
    merged_df = pd.merge(df_new_data, existing_data, on=column_ids, how="left", indicator=True)

    non_duplicates_df = merged_df[merged_df["_merge"] == "left_only"].drop(columns=["_merge"])
    # Check if the DataFrame is empty
    if not non_duplicates_df.empty:
        print("The DataFrame has data!")
        # Load the non-duplicate records to BigQuery
        job = client.load_table_from_dataframe(non_duplicates_df, destination_table)
        job.result() # Wait for the job to complete

        print("New records inserted successfully without duplicating information.")
    else:
        print("We do not have new data, then we canno insert anything")



def etl_picklet_file(file_path):
    # Create a GCS file system object
    fs = gcsfs.GCSFileSystem(project=PROJECT_ID)

    # Path to your Parquet file in GCS
    #file_path = 'gs://adsac/Yelp/business.pkl'
    df_business = pd.read_pickle(file_path)
    #Eliminando duplicados
    df_business = df_business.loc[:, ~df_business.columns.duplicated()]

    #Actualizando tipos
    df_business['attributes'] = df_business['attributes'].astype(str)
    df_business['hours'] = df_business['hours'].astype(str)

    #Eliminando nulos
    df_business = df_business[df_business['business_id'].isnull() == False]
    df_business = df_business[df_business['latitude'].isnull() == False]
    df_business = df_business[df_business['longitude'].isnull() == False]
    df_business = df_business[df_business['stars'].isnull() == False]
    df_business = df_business[df_business['review_count'].isnull() == False]
    df_business = df_business[df_business['is_open'].isnull() == False]

    #Insertar en la tabla curada
    destination_table = 'adsac-455509.Curated.Business'

    # Upload DataFrame
    column_ids = "business_id"
    merge_records(service_account_path, destination_table, column_ids, df_business)



def etl_parquet_file(file_path):
    # Create a GCS file system object
    fs = gcsfs.GCSFileSystem(project=PROJECT_ID)

    # Path to your Parquet file in GCS
    #file_path = 'gs://adsac/Yelp/user.parquet'

    # Open the file and read it
    with fs.open(file_path) as f:
        parquet_file = pq.ParquetFile(f)
        df_user = parquet_file.read().to_pandas()

    #print(df_user.head())
    #Eliminando archivos 
    df_user = df_user[df_user['review_count'] > 0]
    df_user = df_user.drop(columns=['compliment_more', 'compliment_profile', 'compliment_cute', 'compliment_list', 'compliment_note', 'compliment_plain', 'compliment_cool'])
    df_user = df_user.drop(columns=['compliment_hot', 'compliment_funny', 'compliment_writer', 'compliment_photos'])

    #Insertar en la tabla curada
    destination_table = 'adsac-455509.Curated.Usuario'

    # Upload DataFrame
    # Upload DataFrame
    column_ids = "user_id"
    merge_records(service_account_path, destination_table, column_ids, df_user)



def read_json_content(content):
    json_file = []
    for line in content.splitlines():
        # Parse each line if it's valid JSON
        try:
            json_line = json.loads(line)
            json_file.append(json_line)
        except json.JSONDecodeError:
            print("Invalid JSON line:", line)
    return json_file

def etl_review_json_file(file_path):
    json_file = []
    #   This is how you read a BigQuery table
    client = storage.Client.from_service_account_json('adsac-455509-0d5538a0d624.json')
    bucket = client.get_bucket('adsac')
    blob = bucket.blob(file_path)
    # Stream and process the blob in chunks
    with blob.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            try:
                json_line = json.loads(line.strip())
                json_file.append(json_line)
            except json.JSONDecodeError:
                print("Invalid JSON line:", line.strip())
    
    df_review = pd.DataFrame(json_file)
    df_review = df_review.drop_duplicates(['review_id', 'user_id', 'business_id', 'stars', 'useful', 'funny', 'cool', 'text'])
    destination_table = 'adsac-455509.Curated.Review'

    column_ids = "review_id"
    merge_records(service_account_path, destination_table, column_ids, df_review)



def etl_checkin_json_file(file_path):
    # This is how you read a BigQuery table
    client_storage = storage.Client.from_service_account_json(service_account_path)
    bucket = client_storage.get_bucket('adsac')
    #blob = bucket.blob('Yelp/checkin.json')
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    
    json_file = read_json_content(content)

    df_checkin = pd.DataFrame(json_file)
    df_checkin = df_checkin.drop_duplicates()
    
    #Insertar en la tabla curada
    destination_table = 'adsac-455509.Curated.CheckIn'

    column_ids = "business_id"
    merge_records(service_account_path, destination_table, column_ids, df_checkin)

    

def etl_business_json_file(file_path):
    # This is how you read a BigQuery table
    client = storage.Client.from_service_account_json('adsac-455509-0d5538a0d624.json')
    bucket = client.get_bucket('adsac')
    #blob = bucket.blob('Yelp/checkin.json')
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    
    json_file = read_json_content(content)

    df_business = pd.DataFrame(json_file)
    df_business = df_business.loc[:, ~df_business.columns.duplicated()]

    # Removing rows where state is None
    df_business = df_business.dropna(subset=['state'])

    # Removing rows where city is None
    df_business = df_business.dropna(subset=['city'])


    #Insertar en la tabla curada
    destination_table = 'adsac-455509.Curated.Business'
    # Upload DataFrame
    column_ids = "business_id"
    non_duplicates_df = merge_records(service_account_path, destination_table, column_ids, df_business)


def etl_tip_json_file(file_path):
    # This is how you read a BigQuery table
    client = storage.Client.from_service_account_json('adsac-455509-0d5538a0d624.json')
    bucket = client.get_bucket('adsac')
    #blob = bucket.blob('Yelp/tip.json')
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    
    json_file = read_json_content(content)

    df_tip = pd.DataFrame(json_file)

    # Removing rows where state is None
    df_tip = df_tip.dropna(subset=['user_id'])

    # Removing rows where city is None
    df_tip = df_tip.dropna(subset=['business_id'])

    df_tip = df_tip.drop_duplicates()
    #Insertar en la tabla curada
    destination_table = 'adsac-455509.Curated.Tip'
    # Upload DataFrame
    to_gbq(df_tip, destination_table, project_id=PROJECT_ID, if_exists='replace')  # Use 'append' if you want to add rows
    print("Termino con éxito la creación de la tabla:",destination_table)

def identify_restaurant(ref):
    #print(ref)
    if not ref:
        return 0
    value =  [item for item in ref if "rest" in item]
    
    if not value:
        return 0
    return 1

def etl_sitios_json_file(file_path):
    client = storage.Client.from_service_account_json(service_account_path)
    bucket = client.get_bucket('adsac')
    #blob = bucket.blob('Google/1.json')
    blob = bucket.blob(file_path)

    json_file = []
    with blob.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            try:
                json_line = json.loads(line.strip())
                json_file.append(json_line)
            except json.JSONDecodeError:
                print("Invalid JSON line:", line.strip())

    df_sitios = pd.DataFrame(json_file)
    
    f_sitios = df_sitios.drop_duplicates(['name','gmap_id','latitude','longitude','address'])
    df_sitios = df_sitios.drop(columns=['price'])
    df_sitios['is_restaurant'] = df_sitios.category.apply(identify_restaurant)
    


    df_sitios['category'] = df_sitios['category'].astype(str)
    df_sitios['hours'] = df_sitios['hours'].astype(str)
    df_sitios['MISC'] = df_sitios['MISC'].astype(str)
    df_sitios['relative_results'] = df_sitios['relative_results'].astype(str)


    df_sitios = df_sitios[df_sitios['category'].str.contains('resta', case=False, na=False)]

    df_sitios = df_sitios[df_sitios["is_restaurant"] == 1]

    #Insertar en la tabla curada
    destination_table = 'adsac-455509.Curated.Sitios'
    # Upload DataFrame
    column_ids = "gmap_id"
    non_duplicates_df = merge_records(service_account_path, destination_table, column_ids, df_sitios)



def etl():
    #etl_picklet_file('gs://adsac/Yelp/business.pkl')
    #etl_parquet_file('gs://adsac/Yelp/user.parquet')
    #etl_checkin_json_file('Yelp/checkin.json')
    #etl_review_json_file('Yelp/review.json') 
    #etl_tip_json_file('Yelp/tip.json')
    etl_sitios_json_file('Google/1.json')
   
   
    