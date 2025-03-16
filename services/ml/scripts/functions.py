import os
import json
import pandas as pd
from sqlalchemy import create_engine
from functions import opciones_impresion, validar_df

def main():
    # 1) Configuración de la conexión
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    db_name = os.getenv('POSTGRES_DB', 'postgres')

    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

    # 2) Carga de datos JSON
    opciones_impresion()

    ruta = '/app/data/Google/metadata-sitios/11.json'  # Ajusta la ruta según tu carpeta montada
    lista = []
    with open(ruta, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                try:
                    registro = json.loads(line)
                    lista.append(registro)
                except json.JSONDecodeError as e:
                    print(f"Error al decodificar una línea: {e}")

    df = pd.DataFrame(lista)
    print("DataFrame validado:", validar_df(df))
    print(df.head(10))

    # 3) Insertar los datos en la tabla "google_metadata" (por ejemplo)
    df.to_sql("google_metadata", con=engine, if_exists="append", index=False)
    print("Datos insertados en la tabla google_metadata")

if __name__ == "__main__":
    main()
