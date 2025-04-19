import pyarrow.parquet as pq
import gcsfs
import pandas as pd
from pandas_gbq import to_gbq
import bigframes.pandas as bpd
import json
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import re

PROJECT_ID = 'acme-987654'
LOCATION = "southamerica-east1" 
service_account_path = 'C:/Data/json/acme-987654-c052039ac4cd.json'

bucket_name = "acme_storage"

dataset_raw = "Raw"
dataset_curated = "Curated"

table_checkin_id = "CheckIn"
table_user_id = "User" 
table_business_id = "Business"
table_review_id ="Review"
table_sitios_id = "Sitios"
table_estados_id = "Estados"
table_tip_id = "Tip"

bpd.options.bigquery.project = PROJECT_ID
bpd.options.bigquery.location = LOCATION
bpd.options.display.progress_bar = None

# Descargar recursos de NLTK (solo la primera vez)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

sid = SentimentIntensityAnalyzer()

def limpiar_texto(text):
    """Limpia el texto eliminando caracteres no alfanuméricos y convirtiendo a minúsculas."""
    if text is not None:
        text = re.sub(r'[^a-zA-Z\s]', '', text, re.I|re.A)
        text = text.lower()
        return text
    else:
        return ''

def analizar_sentimiento(text):
    """Analiza el sentimiento de un texto y devuelve las polaridades."""
    if isinstance(text, str) and text:
        scores = sid.polarity_scores(text)
        return scores
    else:
        return {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}


def merge_checkin_records(df_new_data):
    # Load DataFrame into a temporary table
    client = bigquery.Client(project=PROJECT_ID)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    print("Project is: ",PROJECT_ID)
    client.load_table_from_dataframe(df_new_data, f"{PROJECT_ID}.{dataset_raw}.{table_checkin_id}", job_config=job_config).result()
    # Merge data from temp table into main table
    try:
        query = f"""
        MERGE `{PROJECT_ID}.{dataset_curated}.{table_checkin_id}` AS target
        USING `{PROJECT_ID}.{dataset_raw}.{table_checkin_id}` AS source
        ON target.business_id = source.business_id
        WHEN MATCHED THEN
            UPDATE SET target.date = source.date
        WHEN NOT MATCHED THEN
            INSERT (business_id, date) VALUES (source.business_id, source.date)
        """
        # Load DataFrame into a temporary table
        query_job = client.query(query)
        query_job.result()  # Waits for the query to finish
        print("Update and insert successful!")
    except NotFound:
        print(f"Table `{PROJECT_ID}.{dataset_curated}.{table_checkin_id}` does not exist.")
        job = client.load_table_from_dataframe(df_new_data, f"""{PROJECT_ID}.{dataset_curated}.{table_checkin_id}""")
        job.result() # Wait for the job to complete

def merge_tip_records(df_new_data):
    # Load DataFrame into a temporary table
    client = bigquery.Client(project=PROJECT_ID)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    print("Project is: ",PROJECT_ID)
    client.load_table_from_dataframe(df_new_data, f"{PROJECT_ID}.{dataset_raw}.{table_tip_id}", job_config=job_config).result()
    # Merge data from temp table into main table
    try:
        query = f"""
        MERGE `{PROJECT_ID}.{dataset_curated}.{table_tip_id}` AS target
        USING `{PROJECT_ID}.{dataset_raw}.{table_tip_id}` AS source
            ON target.user_id = source.user_id
            and target.business_id = source.business_id
            and target.date = source.date
            and target.text = source.text
        WHEN MATCHED THEN
            UPDATE SET target.compliment_count = source.compliment_count
        WHEN NOT MATCHED THEN
            INSERT (user_id, business_id, text, date, compliment_count) 
            VALUES (source.user_id, source.business_id, source.text, source.date, source.compliment_count)
        """
        print(query)
        # Load DataFrame into a temporary table
        query_job = client.query(query)
        query_job.result()  # Waits for the query to finish
        print("Update and insert successful!")
    except NotFound:
        print(f"Table `{PROJECT_ID}.{dataset_curated}.{table_tip_id}` does not exist.")
        job = client.load_table_from_dataframe(df_new_data, f"""{PROJECT_ID}.{dataset_curated}.{table_tip_id}""")
        job.result() # Wait for the job to complete

def merge_review_records(df_new_data):
    # Load DataFrame into a temporary table
    client = bigquery.Client(project=PROJECT_ID)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    print("Project is: ",PROJECT_ID)
    client.load_table_from_dataframe(df_new_data, f"{PROJECT_ID}.{dataset_raw}.{table_review_id}", job_config=job_config).result()
    # Merge data from temp table into main table
    try:
        query = f"""
        MERGE `{PROJECT_ID}.{dataset_curated}.{table_review_id}` AS target
        USING `{PROJECT_ID}.{dataset_raw}.{table_review_id}` AS source
        ON target.business_id = source.business_id 
            and target.user_id = source.user_id
            and target.review_id = source.review_id
        WHEN MATCHED THEN
            UPDATE SET target.date = source.date
        WHEN NOT MATCHED THEN
            INSERT (review_id, user_id, business_id, stars, useful, funny, cool, text, date) 
            VALUES (source.review_id, source.user_id, source.business_id, source.stars, source.useful, source.funny, source.cool, source.text, source.date)
        """
        # Load DataFrame into a temporary table
        print(query)
        query_job = client.query(query)
        query_job.result()  # Waits for the query to finish
        print("Update and insert successful!")
    except NotFound:
        print(f"Table `{PROJECT_ID}.{dataset_curated}.{table_review_id}` does not exist.")
        job = client.load_table_from_dataframe(df_new_data, f"""{PROJECT_ID}.{dataset_curated}.{table_review_id}""")
        job.result() # Wait for the job to complete

def merge_user_records(df_new_data):
    # Load DataFrame into a temporary table
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(df_new_data, f"{PROJECT_ID}.{dataset_raw}.{table_user_id}", job_config=job_config).result()

    # Merge data from temp table into main table
    try:
        query = f"""
        MERGE `{PROJECT_ID}.{dataset_curated}.{table_user_id}` AS target
        USING `{PROJECT_ID}.{dataset_raw}.{table_user_id}` AS source
        ON target.user_id = source.user_id
        and target.review_count = source.review_count
        and target.yelping_since = source.yelping_since
        and target.useful = source.useful
        and target.funny = source.funny
        and target.cool = source.cool
        and target.elite = source.elite
        and target.name = source.name
        and target.friends = source.friends
        and target.fans = source.fans
        and target.average_stars = source.average_stars
        target.num_amigos = source.num_amigos
        WHEN MATCHED THEN
            UPDATE SET                                 
                target.fue_elite_2015 = source.fue_elite_2015,
                target.total_compliment = source.total_compliment
        WHEN NOT MATCHED THEN
            INSERT (user_id, name, review_count, yelping_since, useful, funny, cool, elite, friends, fans, average_stars, num_amigos, fue_elite_2015, total_compliment)
            VALUES (source.user_id, source.name,  source.review_count, source.yelping_since, source.useful, source.funny, source.cool, source.elite, source.friends, source.fans, source.average_stars, source.num_amigos, source.fue_elite_2015, source.total_compliment)
        """
        # Load DataFrame into a temporary table
        query_job = client.query(query)
        query_job.result()  # Waits for the query to finish
        print("Update and insert successful!")
    except NotFound:
        print(f"Table `{PROJECT_ID}.{dataset_curated}.{table_user_id}` does not exist.")
        job = client.load_table_from_dataframe(df_new_data, f"""{PROJECT_ID}.{dataset_curated}.{table_user_id}""")
        job.result() # Wait for the job to complete

def merge_business_records(df_new_data):
    # Load DataFrame into a temporary table
    client = bigquery.Client(project=PROJECT_ID)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    print("Project is: ",PROJECT_ID)
    client.load_table_from_dataframe(df_new_data, f"{PROJECT_ID}.{dataset_raw}.{table_business_id}", job_config=job_config).result()
    # Merge data from temp table into main table
    try:
        query = f"""
        MERGE `{PROJECT_ID}.{dataset_curated}.{table_business_id}` AS target
        USING `{PROJECT_ID}.{dataset_raw}.{table_business_id}` AS source
        ON target.business_id = source.business_id
        WHEN MATCHED THEN
            UPDATE SET target.name = source.name,
            target.address = source.address,
            target.city = source.city,
            target.state = source.state,
            target.postal_code = source.postal_code,
            target.latitude = source.latitude,
            target.longitude = source.longitude,
            target.stars = source.stars,
            target.review_count = source.review_count,
            target.is_open = source.is_open,
            target.attributes = source.attributes,
            target.categories = source.categories,
            target.hours = source.hours
        WHEN NOT MATCHED THEN
            INSERT (business_id, name, address, city, state, postal_code, latitude, longitude, stars, review_count, is_open, attributes, categories, hours ) 
            VALUES (source.business_id, source.name, source.address, source.city, source.state, source.postal_code, source.latitude, source.longitude, source.stars, source.review_count, source.is_open, source.attributes, source.categories, source.hours )
        """
        # Load DataFrame into a temporary table
        query_job = client.query(query)
        query_job.result()  # Waits for the query to finish
        print("Update and insert successful!")
    except NotFound:
        print(f"Table `{PROJECT_ID}.{dataset_curated}.{table_business_id}` does not exist.")
        job = client.load_table_from_dataframe(df_new_data, f"""{PROJECT_ID}.{dataset_curated}.{table_business_id}""")
        job.result() # Wait for the job to complete


def merge_sitios_records(df_sitios):
    # Load DataFrame into a temporary table
    client = bigquery.Client(project=PROJECT_ID)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    print("Project is: ",PROJECT_ID)
    client.load_table_from_dataframe(df_sitios, f"{PROJECT_ID}.{dataset_raw}.{table_sitios_id}", job_config=job_config).result()
    # Merge data from temp table into main table
    try:
        query = f"""
        MERGE `{PROJECT_ID}.{dataset_curated}.{table_sitios_id}` AS target
        USING `{PROJECT_ID}.{dataset_raw}.{table_sitios_id}` AS source
        ON target.gmap_id = source.gmap_id 
            and target.address = source.address
            and target.name = source.name
            and target.latitude = source.latitude
            and target.longitude = source.longitude
            and target.city = source.city
            and target.state = source.state
            and target.category = source.category
        WHEN MATCHED THEN
            UPDATE SET 
            target.avg_rating = source.avg_rating,
            target.num_of_reviews = source.num_of_reviews  
        WHEN NOT MATCHED THEN
            INSERT (name, address, gmap_id, description, latitude, longitude, category, avg_rating, num_of_reviews, hours, MISC, state, city) 
            VALUES (source.name, source.address, source.gmap_id, source.description, source.latitude, source.longitude, source.category, source.avg_rating, source.num_of_reviews, source.hours, source.MISC, source.state, source.city)
        """

        print("query is: ",query)

        # Load DataFrame into a temporary table
        query_job = client.query(query)
        query_job.result()  # Waits for the query to finish
        print("Update and insert successful!")
    except NotFound:
        print(f"Table `{PROJECT_ID}.{dataset_curated}.{table_sitios_id}` does not exist.")
        job = client.load_table_from_dataframe(df_sitios, f"""{PROJECT_ID}.{dataset_curated}.{table_sitios_id}""")
        job.result() # Wait for the job to complete


def merge_estados_records(df_estados):
    # Load DataFrame into a temporary table
    client = bigquery.Client(project=PROJECT_ID)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    print("Project is: ",PROJECT_ID)
    client.load_table_from_dataframe(df_estados, f"{PROJECT_ID}.{dataset_raw}.{table_estados_id}", job_config=job_config).result()
    # Merge data from temp table into main table
    try:
        query = f"""
        MERGE `{PROJECT_ID}.{dataset_curated}.{table_estados_id}` AS target
        USING `{PROJECT_ID}.{dataset_raw}.{table_estados_id}` AS source
        ON target.user_id = source.user_id 
            and target.gmap_id = source.gmap_id
        WHEN MATCHED THEN
            UPDATE SET 
            target.name = source.name,
            target.time = source.time, 
            target.rating = source.rating, 
            target.text = source.text, 
            target.city = source.city, 
            target.state = source.state,
            target.sitio_name = source.sitio_name,
            target.sitio_address = source.sitio_address,
            target.latitude = source.latitude,
            target.longitude = source.longitude,
            target.is_seafood = source.is_seafood,
            target.texto_limpio = source.texto_limpio,
            target.neg = source.neg,
            target.neu = source.neu,
            target.pos = source.pos,
            target.compound = source.compound
        WHEN NOT MATCHED THEN
            INSERT (user_id, name, time, rating, text, gmap_id, city, state, sitio_name, sitio_address, latitude, longitude, is_seafood, texto_limpio, neg, neu, pos, compound) 
            VALUES (source.user_id, source.name, source.time, source.rating, source.text, source.gmap_id, source.city, source.state, source.sitio_name, source.sitio_address, source.latitude, source.longitude, source.is_seafood, source.texto_limpio, source.neg, source.neu, source.pos, source.compound)
        """
    
    

        # Load DataFrame into a temporary table
        query_job = client.query(query)
        query_job.result()  # Waits for the query to finish
        print("Update and insert successful!")
    except NotFound:
        print(f"Table `{PROJECT_ID}.{dataset_curated}.{table_estados_id}` does not exist.")
        job = client.load_table_from_dataframe(df_estados, f"""{PROJECT_ID}.{dataset_curated}.{table_estados_id}""")
        job.result() # Wait for the job to complete


def procesar_checkins(df_checkin):
    """
    Procesa el DataFrame de checkins para convertir la columna 'date' en una lista de fechas.

    Args:
        df_checkin (pd.DataFrame): DataFrame con la información de checkins.

    Returns:
        pd.DataFrame: DataFrame con la columna 'date' procesada como lista de fechas.
    """
    # Función para convertir la cadena de fechas en una lista de fechas
    def convertir_fechas_a_lista(fecha_str):
        """
        Convierte una cadena de fechas separadas por comas en una lista de objetos datetime.

        Args:
            fecha_str (str): Cadena con fechas separadas por comas.

        Returns:
            list: Lista de objetos datetime.
        """
        if isinstance(fecha_str, str):
            return fecha_str.split(', ')
        else:
            return []

    # Aplica la función para convertir la columna 'date' en una lista de fechas
    df_checkin['date'] = df_checkin['date'].apply(convertir_fechas_a_lista)

    return df_checkin

def procesar_columnas_fecha(df, columna_fecha):
    """Convierte una columna de fecha a objetos datetime y extrae características."""
    df[columna_fecha] = pd.to_datetime(df[columna_fecha], errors='coerce')  # Maneja formatos de fecha inválidos
    df['año'] = df[columna_fecha].dt.year
    df['mes'] = df[columna_fecha].dt.month
    df['dia_semana'] = df[columna_fecha].dt.dayofweek  # 0 = Lunes, 6 = Domingo
    df['hora'] = df[columna_fecha].dt.hour
    return df

def contar_amigos(lista_amigos):
    """
    Calcula la cantidad de amigos de un usuario.

    Args:
        lista_amigos (str): Una cadena que contiene la lista de amigos, separados por comas.

    Returns:
        int: El número de amigos. Retorna 0 si la lista es vacía o no es una cadena.
    """
    if isinstance(lista_amigos, str):
        amigos = lista_amigos.split(', ')
        return len(amigos)
    else:
        return 0

def etl_checkin_json_file(file_path):
    # This is how you read a BigQuery table
    client_storage = storage.Client.from_service_account_json(service_account_path)
    bucket = client_storage.get_bucket(bucket_name)
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    
    json_file = read_json_content(content)

    df_checkin = pd.DataFrame(json_file)
    df_checkin = df_checkin.drop_duplicates()
    df_checkin = procesar_checkins(df_checkin)    
    #df_checkin = procesar_columnas_fecha(df_checkin, 'date')
    merge_checkin_records(df_checkin)

def fue_elite_en(lista_anios, anio):
    """
    Verifica si un usuario fue miembro elite en un año específico.

    Args:
        lista_anios (list): Una lista de años en los que el usuario fue miembro elite.
        anio (int): El año a verificar.

    Returns:
        bool: True si el usuario fue miembro elite en el año especificado, False de lo contrario.
              Retorna False si la lista no es una lista.
    """
    if isinstance(lista_anios, list):
        return anio in lista_anios
    else:
        return False

def etl_business_file(file_path):
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

    # Upload DataFrame
    merge_business_records(df_business)



def etl_user_file(file_path):
    # Create a GCS file system object
    fs = gcsfs.GCSFileSystem(project=PROJECT_ID)

    with fs.open(file_path) as f:
        parquet_file = pq.ParquetFile(f)
        df_user = parquet_file.read().to_pandas()

    df_user['num_amigos'] = df_user['friends'].apply(contar_amigos)
    df_user['fue_elite_2015'] = df_user['elite'].apply(lambda x: fue_elite_en(x, 2015))

    columnas_complidos = [
        'compliment_hot', 'compliment_more', 'compliment_profile', 'compliment_cute',
        'compliment_list', 'compliment_note', 'compliment_plain', 'compliment_cool',
        'compliment_funny', 'compliment_writer', 'compliment_photos'
    ]

    # Suma las columnas de cumplidos para obtener el total
    df_user['total_compliment'] = df_user[columnas_complidos].sum(axis=1)

    df_user = df_user[df_user['review_count'] > 0]
    df_user = df_user.drop(columns=columnas_complidos)
    #return df_user
    merge_user_records(df_user)




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
    client = storage.Client.from_service_account_json(service_account_path)
    bucket = client.get_bucket(bucket_name)
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

    merge_review_records(df_review)




def etl_business_json_file(file_path):
    # This is how you read a BigQuery table
    client = storage.Client.from_service_account_json(service_account_path)
    bucket = client.get_bucket(bucket_name)
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
    #destination_table = '{PROJECT_ID}.Curated.Business'
    # Upload DataFrame
    column_ids = "business_id"
    merge_records(service_account_path, destination_table, column_ids, df_business)


def etl_tip_json_file(file_path):
    # This is how you read a BigQuery table
    client = storage.Client.from_service_account_json(service_account_path)
    bucket = client.get_bucket(bucket_name)
    #blob = bucket.blob('Yelp/tip.json')
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    
    json_file = read_json_content(content)

    df_tip = pd.DataFrame(json_file)

    # Removing rows where state is None
    df_tip = df_tip.dropna(subset=['user_id'])

    # Removing rows where city is None
    df_tip = df_tip.dropna(subset=['business_id'])

    # Removing rows where city is None
    df_tip = df_tip.dropna(subset=['date'])

    # Removing rows where city is None
    df_tip = df_tip.dropna(subset=['text'])

    df_tip = df_tip.drop_duplicates()
    #Insertar en la tabla curada
    #destination_table = '{PROJECT_ID}.Curated.Tip'
    # Upload DataFrame
    merge_tip_records(df_tip)

def identify_kind_of_restaurant(ref):
    #print(ref)
    if not ref:
        return 0
    value =  [item for item in ref if "rest" in item ]    
    if not value:
        #No es restaurante
        return 2
    value =  [item for item in ref if es_maritimo(item)]
    if not value:
        return 0    
    return 1

def identify_city(address):
    if not address:
        return ""
    
    if 'charleston' in address.lower() and ('sc' in address.lower() or 'carolina' in address.lower()):
        return "charleston"
    elif 'tampa' in address.lower() and ('fl' in address.lower() or 'florida' in address.lower()):
        return "tampa"
    elif 'boston' in address.lower() and ('ma' in address.lower() or 'massachusetts' in address.lower()):
        return "boston"
    elif 'galveston' in address.lower() and ('tx' in address.lower() or 'texas' in address.lower()):
        return "galveston"
    elif 'seattle' in address.lower() and ('wa' in address.lower() or 'washington' in address.lower()):
        return "seattle"
    elif 'san diego' in address.lower() and ('ca' in address.lower() or 'california' in address.lower()):
        return "san diego"
    elif 'new orleans' in address.lower() and ('la' in address.lower() or 'luisiana' in address.lower()):
        return "new orleans"
    else:
        return ""
   
    return 1

def identify_state(address):
    if not address:
        return ""
    
    if 'sc' in address.lower() or 'carolina' in address.lower():
        return "sc"
    elif 'fl' in address.lower() or 'florida' in address.lower():
        return "fl"
    elif 'ma' in address.lower() or 'massachusetts' in address.lower():
        return "ma"
    elif 'tx' in address.lower() or 'texas' in address.lower():
        return "tx"
    elif 'wa' in address.lower() or 'washington' in address.lower():
        return "wa"
    elif 'ca' in address.lower() or 'california' in address.lower():
        return "ca"
    elif 'la' in address.lower() or 'luisiana' in address.lower():
        return "la"
    else:
        return ""
   
    return 1

def etl_sitios_json_file(file_path):
    client = storage.Client.from_service_account_json(service_account_path)
    bucket = client.get_bucket(bucket_name)
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
    
    df_sitios = df_sitios.drop_duplicates(['name','gmap_id','latitude','longitude','address'])
    df_sitios = df_sitios.drop(columns=['price','url','relative_results'])

    df_sitios['is_seafood'] = df_sitios.category.apply(identify_kind_of_restaurant)    
    df_sitios = df_sitios[df_sitios["is_seafood"] != 2]

    df_sitios['city'] = df_sitios.address.apply(identify_city)
    df_sitios = df_sitios[df_sitios["city"] != ""]

    df_sitios['state'] = df_sitios.address.apply(identify_state)
    df_sitios['category'] = df_sitios['category'].astype(str)
    df_sitios['hours'] = df_sitios['hours'].astype(str)
    df_sitios['MISC'] = df_sitios['MISC'].astype(str)
   
    merge_sitios_records(df_sitios)

    

def procesar_json_gcs_a_dataframe(file_path):
    """
    Procesa un archivo JSON almacenado en Google Cloud Storage y crea un DataFrame de pandas.

    Args:
        file_path (str): La ruta del archivo JSON en el bucket de GCS.

    Returns:
        pd.DataFrame: Un DataFrame de pandas con los datos del archivo JSON, 
                      o None si hay errores.
    """

    try:
        # Inicializa el cliente de Google Cloud Storage con las credenciales
        client = storage.Client.from_service_account_json(service_account_path)
        # Obtiene el bucket de GCS
        bucket = client.get_bucket(bucket_name)
        # Obtiene el blob (archivo) del bucket
        blob = bucket.blob(file_path)

        # Lista para almacenar los registros JSON
        json_file = []
        # Abre el archivo JSON desde GCS en modo lectura con codificación UTF-8
        with blob.open("r", encoding="utf-8") as file_obj:
            # Itera sobre cada línea del archivo
            for line in file_obj:
                try:
                    # Intenta convertir la línea a un objeto JSON
                    json_line = json.loads(line.strip())
                    # Agrega el objeto JSON a la lista
                    json_file.append(json_line)
                except json.JSONDecodeError:
                    # Imprime un mensaje de error si la línea no es JSON válido
                    print("⚠ Línea JSON inválida:", line.strip())

        # Crea un DataFrame de pandas con los registros JSON
        df_review_estados = pd.DataFrame(json_file)

        # Limpieza de datos y manejo de la columna 'resp'
        # Limpieza de la columna 'text'
        df_review_estados['text'] = df_review_estados['text'].fillna('').str.replace('\x00', '')
        # Limpieza de la columna 'pics'
        df_review_estados['pics'] = df_review_estados['pics'].fillna('').apply(json.dumps).str.replace('\x00', '')
        # La columna 'resp' se mantiene sin descomponer

        # Devuelve el DataFrame creado
        return df_review_estados

    except Exception as e:
        # Imprime un mensaje de error si ocurre alguna excepción
        print(f"❌ Error al procesar {file_path}: {e}")
        # Devuelve None en caso de error
        return None


def es_maritimo(text):
    
    if isinstance(text, str):
        text_lower = text.lower()
        return 'seafood' in text_lower or 'fish' in text_lower or 'crab' in text_lower or 'oyster' in text_lower or 'acme' in text_lower or 'shrimp' in text_lower or 'lobster' in text_lower or 'squid' in text_lower or 'ocean' in text_lower  or 'sushi' in text_lower or 'salmon' in text_lower or 'tuna' in text_lower or 'marine' in text_lower or 'nautical' in text_lower     
    else:
        return False
    


def etl_estados_json_file(file_path):
    # Initialize BigQuery client
    client = bigquery.Client.from_service_account_json(service_account_path)

    # Define your query
    query = """
        SELECT gmap_id, city, state, name as sitio_name, address as sitio_address, latitude, longitude, is_seafood FROM `acme-987654.Curated.Sitios`
    """
    
    # Run the query
    query_job = client.query(query)
    df_sitios_validos = query_job.to_dataframe()

    df_estados = procesar_json_gcs_a_dataframe(file_path)
    df_estados.drop_duplicates(subset=["user_id", "time", "gmap_id"], inplace=True)

    df_merge_estados_sitios = pd.merge(df_estados, df_sitios_validos, on='gmap_id', how='inner')
    df_merge_estados_sitios = df_merge_estados_sitios.drop(columns=['resp','pics'])
    
    df_merge_estados_sitios = df_merge_estados_sitios.dropna(subset=['text'])
    
    # Only sea food             
    df_merge_estados_sitios = df_merge_estados_sitios.dropna(subset=['text'])
    df_merge_estados_sitios = df_merge_estados_sitios[df_merge_estados_sitios['text'].str.len() > 0]

    # 1. Limpiar el texto
    df_merge_estados_sitios['texto_limpio'] = df_merge_estados_sitios['text'].apply(limpiar_texto)

    # 2. Analizar el sentimiento
    df_merge_estados_sitios['sentimiento'] = df_merge_estados_sitios['texto_limpio'].apply(analizar_sentimiento)

    # 3. Expandir el diccionario de sentimiento en columnas separadas
    df_final = pd.concat([df_merge_estados_sitios, df_merge_estados_sitios['sentimiento'].apply(pd.Series)], axis=1)

    # 4. Eliminar la columna 'sentimiento' original
    df_final.drop(columns=['sentimiento'], inplace=True, errors='ignore')
   
    if df_final.empty == False:
        print("DF Estados no esta vacio, tiene: ", df_final.shape)
        merge_estados_records(df_final)
    else:
        print("DF Estados esta vacio :( ")
    

def get_table_curated_by_columns(table, columns):
    # Initialize BigQuery client
    client = bigquery.Client.from_service_account_json(service_account_path)

    # Define your query
    query = f"""
        SELECT {columns} FROM acme-987654.Curated.{table}
    """

    
    # Run the query
    print(query)
    query_job = client.query(query)
    df = query_job.to_dataframe()
    return df

    


    
