# Iniciamos con la carga de datos para su revision:
# La data está alojada en un archivo json que contiene la metadata de los sitios de Google
# Los metadatos estan organizados por filas donde cada una es un elemento json que contiene una lista de diccionarios
# con la información de cada sitio
import json
import pandas as pd
import sys
from functions import opciones_impresion, validar_df

def main():
    opciones_impresion()
    
    ruta = '/app/data/Google/metadata-sitios/11.json'
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
    print(validar_df(df))
    print(df.head(10))

if __name__ == "__main__":
    main()
