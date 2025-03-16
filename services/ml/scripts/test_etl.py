# Iniciamos con la carga de datos para su revision:
# La data está alojada en un archivo json que contiene la metadata de los sitios de Google
# Los metadatos estan organizados por filas donde cada una es un elemento json que contiene una lista de diccionarios
# con la información de cada sitio
import json
import pandas as pd
import sys
sys.path.append('/Users/usuario/Documents/PF_Henry/Proyecto-Final-Grupal')
from functions import *

opciones_impresion() # Invocamos la función para mejorar la impresion y que no se recorte la información al imprimir.

ruta = '/Users/usuario/Documents/PF_Henry/Proyecto-Final-Grupal/Data/Google/metadata-sitios/11.json'
lista = []

with open(ruta, 'r') as file:
    for line in file:
        line = line.strip()  # Elimina espacios y saltos de línea
        if line:  # Evita procesar líneas vacías
            try:
                registro = json.loads(line)
                lista.append(registro)
            except json.JSONDecodeError as e:
                print(f"Error al decodificar una línea: {e}")

df = pd.DataFrame(lista)
print(validar_df(df))
print(df.head(10))