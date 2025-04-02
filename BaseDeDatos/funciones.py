import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd
import os
import json

def get_connection_engine():
    # Database connection details
    user = 'postgres'
    password = '98020927'
    host = 'localhost'
    port = '5432'
    database = 'ADSAC'

    # Create the connection string
    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')
    return engine


def upload_json_file(path_file):
    """Carga reviews desde todos los archivos JSON en un directorio a una lista de diccionarios."""
    json_file = []
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    json_line = json.loads(line)
                    json_file.append(json_line)
                except json.JSONDecodeError:
                    print(f"Omitiendo línea JSON inválida en {path_file}: {line.strip()}")
                except FileNotFoundError:
                    print(f"Error: Archivo no encontrado: {path_file}")
                except json.JSONDecodeError:
                    print(f"Error decodificando JSON en el archivo: {path_file}")
    except Exception as e:
        print(f"Ocurrió un error inesperado al procesar {path_file}: {e}")
               
    return json_file

def upload_json_from_directory(path_dir):
    """Carga reviews desde todos los archivos JSON en un directorio a una lista de diccionarios."""
    reviews = []
    for filename in os.listdir(path_dir):
        if filename.endswith(".json"):
            ruta_archivo = os.path.join(path_dir, filename)
            json_bunch = upload_json_file(ruta_archivo)
            
    return json_bunch

def insertar_sql(df_no_duplicates, table_name, engine, type_operation, index_value):
    df_no_duplicates.to_sql(table_name, engine, if_exists=type_operation, index=index_value)

    print(f"Data inserted successfully into the table '{table_name}'!")

def get_only_target_city(df_full, engine):    

    #with engine.connect() as connection:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT state, city FROM target_city"))

        # Fetch all rows
        rows = result.fetchall()

        # Convert the results into a pandas1 DataFrame
        df_target_city = pd.DataFrame(rows, columns=result.keys())
        
        df_state_target = df_full[df_full['state'].isin(df_target_city['state'])]
        
        #df_state_target.to_csv('output.csv', index=False)

        print("Validating the unique states in dataframe: ", df_state_target['state'].unique())

        # Display the DataFrame        
        matches = df_state_target[
            df_state_target.apply(lambda row: ((row['state'], row['city']) in zip(df_target_city['state'], df_target_city['city'])), axis=1)
        ]
        print("matches: ",matches)
        return matches


def clean_checkin_dataframe(df_no_duplicates):
    return df_no_duplicates

def clean_tip_dataframe(df_no_duplicates):
    return df_no_duplicates

def clean_usuario_dataframe(df_no_duplicates):
    return df_no_duplicates

def clean_sitios_dataframe(df_no_duplicates):
    #Dejar solamente restaurantes
    df_no_duplicates = df_no_duplicates[df_no_duplicates['category'].str.contains('resta', case=False, na=False)]
    return df_no_duplicates

def clean_review_dataframe(df_no_duplicates):
    return df_no_duplicates

def clean_business_dataframe(df_no_duplicates, engine):

    #with engine.connect() as connection:
    with engine.connect() as connection:
        result = connection.execute(text("select state, city, nicknames from state_city"))

        # Fetch all rows
        rows = result.fetchall()

        # Convert the results into a pandas DataFrame
        df_state_city = pd.DataFrame(rows, columns=result.keys())

        # Removing rows where state is None
        df_no_duplicates = df_no_duplicates.dropna(subset=['state'])

        # Removing rows where city is None
        df_no_duplicates = df_no_duplicates.dropna(subset=['city'])

        #print("State ", df_state_city['state'].tolist())

        df_no_duplicates = df_no_duplicates[df_no_duplicates['state'].isin(df_state_city['state'].tolist())]
        #df_no_duplicates = df_no_duplicates[df_no_duplicates['state'].isin(df_state_city['state'].tolist())]
        
        #print("City unique is Tampa?: ", 'Tampa Bay'.find(df_state_city['nicknames'].values), "values a vers: ",df_state_city['nicknames'].values )
        #Removing states that are not target in this market
        #df_no_duplicates = df_no_duplicates[df_no_duplicates['state'] != 'Bob']

        #for i in df_state_city.index :
            #print("Los nicknames son: ",df_state_city.loc[i, 'nicknames'], "Example in is: ", ('Tampa' in df_state_city.loc[i, 'nicknames']))


        df_no_duplicates['MatchedCity'] = df_no_duplicates.apply(
            lambda row: next(                
                (df_state_city.loc[i, 'city'] for i in df_state_city.index 
                
                if (row['city'] in df_state_city.loc[i, 'nicknames'] ) and (df_state_city.loc[i, 'state'] in row['state'])), 
                None
            ), 
            axis=1
        )
            
    
    print(df_no_duplicates[['MatchedCity','city','state']])
    
    return df_no_duplicates

def insert_into_table_checkin(path_file ):    

    json_file = upload_json_file(path_file)    
    df = pd.DataFrame(json_file)
    df_no_duplicates = df.drop_duplicates()

    df_final = clean_checkin_dataframe(df_no_duplicates)

    engine = get_connection_engine()
    type_operation= 'append'
    index_value = False
    insertar_sql(df_final, 'checkin', engine, type_operation, index_value)

def insert_into_table_tip(path_file ):    

    json_file = upload_json_file(path_file)    
    df = pd.DataFrame(json_file)
    df_no_duplicates = df.drop_duplicates()

    df_final = clean_tip_dataframe(df_no_duplicates)

    engine = get_connection_engine()
    type_operation= 'append'
    index_value = False
    insertar_sql(df_final, 'tip', engine, type_operation, index_value)

def insert_into_table_usuarios(path_file ):    

    # Read a Parquet file into a DataFrame
    df = pd.read_parquet(path_file)
    df_no_duplicates = df.drop_duplicates()

    df_final = clean_usuario_dataframe(df_no_duplicates)

    engine = get_connection_engine()
    type_operation= 'append'
    index_value = False
    insertar_sql(df_final, 'user_yelp', engine, type_operation, index_value)

def insert_into_table_business(path_file ):    

    # Read a Parquet file into a DataFrame
    df = pd.read_pickle(path_file)
    df = df.loc[:, ~df.columns.duplicated()]

    df['attributes'] = df['attributes'].astype(str)
    df['hours'] = df['hours'].astype(str)

    engine = get_connection_engine()
    #df_final = clean_business_dataframe(df, engine)

    #df_target = get_only_target_city(df, engine)

    #try:
    type_operation= 'replace'
    index_value = False
    insertar_sql(df, 'business', engine, type_operation, index_value)
    #except:
    #    print("fails with: :'( )")

    return df


def insert_into_table_sitios(path_directory):     

    json_bunch = upload_json_from_directory(path_directory)    
    df = pd.DataFrame(json_bunch)

    df_no_duplicates = df.drop_duplicates(['name','gmap_id','latitude','longitude','address'])
    
    df_no_duplicates['price'] = df_no_duplicates['price'].apply(lambda x:  None if x == '$' else x)
    df_no_duplicates['price'] = df_no_duplicates['price'].apply(lambda x:  None if x == '$$' else x)
    df_no_duplicates['price'] = df_no_duplicates['price'].apply(lambda x:  None if x == '$$$' else x)
    df_no_duplicates['price'] = df_no_duplicates['price'].apply(lambda x:  None if x == '$$$$' else x)

    df_no_duplicates['price'] = df_no_duplicates['price'].apply(lambda x:  None if x == '₩' else x)
    df_no_duplicates['price'] = df_no_duplicates['price'].apply(lambda x:  None if x == '₩₩' else x)
    df_no_duplicates['price'] = df_no_duplicates['price'].apply(lambda x:  None if x == '₩₩₩' else x)
    df_no_duplicates['price'] = df_no_duplicates['price'].apply(lambda x:  None if x == '₩₩₩₩' else x)

    df_no_duplicates['category'] = df_no_duplicates['category'].astype(str)
    df_no_duplicates['hours'] = df_no_duplicates['hours'].astype(str)
    df_no_duplicates['MISC'] = df_no_duplicates['MISC'].astype(str)
    df_no_duplicates['relative_results'] = df_no_duplicates['relative_results'].astype(str)

    df_final = clean_sitios_dataframe(df_no_duplicates)

    engine = get_connection_engine()
    type_operation= 'replace'
    index_value = False
    insertar_sql(df_final, 'sitios', engine, type_operation, index_value)




def insert_into_table_review(path_file ):    

    json_file = upload_json_file(path_file)    
    df = pd.DataFrame(json_file)
    df_no_duplicates = df.drop_duplicates()

    df_final = clean_review_dataframe(df_no_duplicates)

    #engine = get_connection_engine()
    #type_operation= 'append'
    #index_value = False
    #insertar_sql(df_final, 'review', engine, type_operation, index_value)
    return df_final