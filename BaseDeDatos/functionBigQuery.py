import pyarrow.parquet as pq
import gcsfs
import pandas as pd
from pandas_gbq import to_gbq
import bigframes.pandas as bpd
import json
from google.cloud import storage


PROJECT_ID = 'adsac-455509'
LOCATION = "southamerica-east1" 

bpd.options.bigquery.project = PROJECT_ID
bpd.options.bigquery.location = LOCATION
bpd.options.display.progress_bar = None

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
    to_gbq(df_business, destination_table, project_id=PROJECT_ID, if_exists='replace')  # Use 'append' if you want to add rows
    print("Termino con éxito la creación de la tabla: ",destination_table)


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
    to_gbq(df_user, destination_table, project_id=PROJECT_ID, if_exists='replace')  # Use 'append' if you want to add rows
    print("Termino con éxito la creación de la tabla:",destination_table)



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
    # This is how you read a BigQuery table
    client = storage.Client.from_service_account_json('adsac-455509-0d5538a0d624.json')
    bucket = client.get_bucket('adsac')
    #blob = bucket.blob('Yelp/review.json')
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    
    json_file = read_json_content(content)

    df_sitios = pd.DataFrame(json_file)
    df_sitios_no_duplicates = df_sitios.drop_duplicates(['name','gmap_id','latitude','longitude','address'])

    df_sitios_no_duplicates = df_sitios_no_duplicates.drop(columns=['price','relative_results','url'])
    
    #Insertar en la tabla curada
    destination_table = 'adsac-455509.Curated.Review'

    # Upload DataFrame
    to_gbq(df_sitios_no_duplicates, destination_table, project_id=PROJECT_ID, if_exists='replace')  # Use 'append' if you want to add rows
    print("Termino con éxito la creación de la tabla:",destination_table)

def etl_checkin_json_file(file_path):
    # This is how you read a BigQuery table
    client = storage.Client.from_service_account_json('adsac-455509-0d5538a0d624.json')
    bucket = client.get_bucket('adsac')
    #blob = bucket.blob('Yelp/checkin.json')
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    
    json_file = read_json_content(content)

    df_checkin = pd.DataFrame(json_file)
    df_checkin = df_checkin.drop_duplicates()
    
    #Insertar en la tabla curada
    destination_table = 'adsac-455509.Curated.CheckIn'
    # Upload DataFrame
    to_gbq(df_checkin, destination_table, project_id=PROJECT_ID, if_exists='replace')  # Use 'append' if you want to add rows
    print("Termino con éxito la creación de la tabla:",destination_table)

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
    to_gbq(df_business, destination_table, project_id=PROJECT_ID, if_exists='replace')  # Use 'append' if you want to add rows
    print("Termino con éxito la creación de la tabla:",destination_table)

def etl():
    #etl_picklet_file('gs://adsac/Yelp/business.pkl')
    #etl_parquet_file('gs://adsac/Yelp/user.parquet')
    #etl_checkin_json_file('Yelp/checkin.json')
    etl_review_json_file('Yelp/review.json')
   
    