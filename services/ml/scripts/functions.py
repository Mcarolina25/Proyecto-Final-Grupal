import pandas as pd
import numpy as np
import ast
from datetime import datetime

def opciones_impresion(width=1000, expand=True, max_columns=None, max_rows=None, max_colwidth=None, colheader_justify='left'):
    """
    Configura las opciones de visualización de Pandas para imprimir DataFrames.
    
    Parámetros:
      - width (int): Ancho máximo de la salida (por defecto 1000).
      - expand (bool): Si es False, muestra el DataFrame en una sola línea si es posible (por defecto False).
      - max_columns (int o None): Número máximo de columnas a mostrar; None muestra todas.
      - max_rows (int o None): Número máximo de filas a mostrar; None muestra todas.
      - max_colwidth (int o None): Ancho máximo de cada columna; None no trunca.
      - colheader_justify (str): Justificación de las cabeceras de columna (por ejemplo, 'left', 'right' o 'center').
    """
    pd.set_option('display.expand_frame_repr', expand)
    pd.set_option('display.max_columns', max_columns)
    pd.set_option('display.width', width)
    pd.set_option('display.max_rows', max_rows)
    pd.set_option('display.max_colwidth', max_colwidth)
    pd.set_option('display.colheader_justify', colheader_justify)

def renombrar_campos(df_dict, nuevos_nombres):
    """
    Renombra columnas de las hojas contenidas en df_dict según los renombramientos definidos en nuevos_nombres.
    
    Parámetros:
      - df_dict (dict): Diccionario donde cada clave es el nombre de la hoja y cada valor es un DataFrame.
      - nuevos_nombres (dict): Diccionario de mapeo, donde cada clave es el nombre de la hoja y el valor 
                         es otro diccionario con el mapeo de columnas (llave: nombre original, valor: nuevo nombre).
                         
    Retorna:
      dict: El mismo diccionario df_dict, con las hojas que se encuentran en nuevos_nombres renombradas según lo indicado.
    """
    for hoja, mapping in nuevos_nombres.items():
        if hoja in df_dict:
            df_dict[hoja] = df_dict[hoja].rename(columns=mapping)
        else:
            print(f"La hoja '{hoja}' no se encontró en el diccionario.")
    return df_dict

def load_excel_sheets(file_path):
    """
    Carga un archivo Excel y devuelve un diccionario con los nombres de las hojas y sus respectivos dataframes.
    """
    try:
        # Cargar todas las hojas en un diccionario
        sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
        return sheets
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return {}

# Función para validar un DataFrame, generando un resumen con información relevante de cada columna.
"""def validar_df(df):
    res = pd.DataFrame({
        "Tipo de Dato": df.dtypes,
        "Valores No Nulos": df.count(),
        "Valores Nulos": df.isna().sum(),
        "Valores Únicos": df.astype(str).nunique(dropna=True),
        "Valores Cero": (df == 0).sum(),
        "Inconsistentes ('?')": df.isin(['?']).sum(),
        "Valores Vacíos (string)": df.isin(["", " ", "NA", "NULL", "None"]).sum(),
        "valores_negativos": (df.select_dtypes(include=['int64', 'float64']) < 0).sum()
    })
    res = res.reindex(df.columns)
    return res"""

"""def validar_df(df):
    
    Valida un DataFrame, generando un resumen con información relevante de cada columna.
    Se omite la reindexación para evitar errores con etiquetas duplicadas.
    
    res = pd.DataFrame({
        "Tipo de Dato": df.dtypes,
        "Valores No Nulos": df.count(),
        "Valores Nulos": df.isna().sum(),
        "Valores Únicos": df.astype(str).nunique(dropna=True),
        "Valores Cero": (df == 0).sum(),
        "Inconsistentes ('?')": df.isin(['?']).sum(),
        "Valores Vacíos (string)": df.isin(["", " ", "NA", "NULL", "None"]).sum(),
        "valores_negativos": (df.select_dtypes(include=['int64', 'float64']) < 0).sum()
    })
    return res"""


#######################################################
# Funciones para validar DataFrames
#######################################################

import numpy as np
import pandas as pd
import datetime
from scipy.stats import zscore

def validar_df(
    df, 
    factor_iqr=3, 
    z_threshold=3.0
):
    """
    Valida un DataFrame generando un resumen con información clave de cada columna.
    
    Para cada columna se calcula:
      - Tipo de Dato
      - Int: Cantidad de valores no nulos que sean de tipo entero (isinstance(x, int)).
      - Int64: Conteo de valores no nulos si la columna tiene dtype "Int64" (entero nullable).
      - Float: Cantidad de valores no nulos de tipo float.
      - Bool: Cantidad de valores no nulos de tipo bool.
      - DateT: Cantidad de valores no nulos de tipo datetime (pd.Timestamp o datetime.datetime).
      - Str: Cantidad de valores no nulos de tipo str.
      - Ctgory: Cantidad de valores no nulos en columnas categóricas (si la columna es category).
      - Nulos: Número de valores nulos.
      - No_Nulos: Número de valores no nulos.
      - Únicos: Número de valores únicos (tras convertir a str).
      - Ceros: Conteo de valores == 0 (solo para columnas numéricas).
      - Vacíos (string): Conteo de "", "NA", "NULL", "None" en columnas de texto.
      - Skewness: Asimetría (solo numéricas).
      - Kurtosis: Curtosis (solo numéricas).
      - Media, Desviación_Std, Moda, Mínimo, Q1_25%, Q2_50% (Mediana), Q3_75%, Máximo, Negativos (solo numéricas).
      - IQR, FactorIQR, %OutL_IQR, LowerBound, UpperBound: Detección de outliers vía IQR.
      - Z-Score, Z_Threshold, %OutL_Z_Thresh: Detección de outliers vía Z-Score.
    
    Retorna:
      pd.DataFrame: Un DataFrame transpuesto, donde cada fila corresponde a una columna.
    """

    summary = {}
    
    for col in df.columns:
        s = df[col]
        # Si 's' es un DataFrame (por nombres duplicados), tomamos la primera columna.
        if isinstance(s, pd.DataFrame):
            print(f"Advertencia: La columna '{col}' aparece duplicada. Se usará la primera aparición.")
            s = s.iloc[:, 0]
        
        # Tipo de dato de la columna
        tipo = s.dtype
        
        # Conteo de valores no nulos y nulos
        val_no_nulos = s.count()
        val_nulos = s.isna().sum()
        
        # Número de valores únicos (tras convertir a str)
        val_unicos = s.astype(str).nunique(dropna=True)
        
        # Conteo de ceros (solo numéricas)
        val_cero = (s == 0).sum() if pd.api.types.is_numeric_dtype(s) else np.nan
        
        # Conteo de vacíos en texto
        if pd.api.types.is_string_dtype(s):
            val_vacios = s.apply(lambda x: x.strip() if isinstance(x, str) else x)\
                           .isin(["", "NA", "NULL", "None"]).sum()
        else:
            val_vacios = np.nan
        
        # Conteo de tipos en valores no nulos
        count_int = sum(isinstance(x, int) for x in s.dropna())
        count_float = sum(isinstance(x, float) for x in s.dropna())
        count_bool = sum(isinstance(x, bool) for x in s.dropna())
        count_datetime = sum(isinstance(x, (pd.Timestamp, datetime.datetime)) 
                             for x in s.dropna())
        count_str = sum(isinstance(x, str) for x in s.dropna())
        count_category = s.dropna().shape[0] if pd.api.types.is_categorical_dtype(s) else np.nan
        count_int64 = s.dropna().shape[0] if s.dtype.name == "Int64" else 0
        
        # Inicializamos variables para outliers e info numérica
        iqr_val = np.nan
        lower_bound = np.nan
        upper_bound = np.nan
        outliers_iqr = np.nan
        porc_outliers_iqr = np.nan

        max_zscore = np.nan
        outliers_z = np.nan
        porc_outliers_z = np.nan
        
        # Estadísticas numéricas
        if pd.api.types.is_numeric_dtype(s) and val_no_nulos > 0:
            serie_num = s.dropna()
            
            media = serie_num.mean()
            std = serie_num.std()
            minimo = serie_num.min()
            q1 = serie_num.quantile(0.25)
            mediana = serie_num.median()
            q3 = serie_num.quantile(0.75)
            maximo = serie_num.max()
            negativos = (serie_num < 0).sum()
            skew = serie_num.skew()
            kurtosis = serie_num.kurtosis()

            # Moda
            mode_series = serie_num.mode(dropna=True)
            moda = mode_series.iloc[0] if not mode_series.empty else np.nan
            
            # ---- Outliers via IQR ----
            iqr_val = q3 - q1
            lower_bound = q1 - factor_iqr * iqr_val
            upper_bound = q3 + factor_iqr * iqr_val
            mask_iqr = (serie_num < lower_bound) | (serie_num > upper_bound)
            outliers_iqr = mask_iqr.sum()
            if val_no_nulos > 0:
                porc_outliers_iqr = round((outliers_iqr / val_no_nulos) * 100, 3)
            
            # ---- Outliers via Z-Score ----
            # Para evitar error con constantes, checkeamos std>0
            if serie_num.nunique() > 1:
                zscores = np.abs(zscore(serie_num, nan_policy="omit"))
                max_zscore = zscores.max()  # valor max abs zscore
                mask_z = (zscores > z_threshold)
                outliers_z = mask_z.sum()
                if val_no_nulos > 0:
                    porc_outliers_z = round((outliers_z / val_no_nulos) * 100, 3)
            else:
                # Si no hay variación, zscore no es definible
                max_zscore = np.nan
                outliers_z = np.nan
                porc_outliers_z = np.nan

        else:
            # No numérica o sin datos
            media = std = minimo = q1 = mediana = q3 = maximo = negativos = np.nan
            skew = np.nan
            kurtosis = np.nan
            moda = np.nan
        
        summary[col] = {
            "Tipo de Dato": tipo,
            "Int": count_int,
            "Int64": count_int64,
            "Float": count_float,
            "Bool": count_bool,
            "DateT": count_datetime,
            "Str": count_str,
            "Ctgory": count_category,
            "Nulos": val_nulos,
            "No_Nulos": val_no_nulos,
            "Únicos": val_unicos,
            "Ceros": val_cero,
            "Vacíos (string)": val_vacios,
            "Skewness": skew,
            "Kurtosis": kurtosis,
            "Media": media,
            "Desviación_Std": std,
            "Moda": moda,
            "Mínimo": minimo,
            "Q1_25%": q1,
            "Q2_50%": mediana,
            "Q3_75%": q3,
            "Máximo": maximo,
            "Negativos": negativos,
            # Outliers por IQR
            "IQR": iqr_val,
            "%OutL_IQR": porc_outliers_iqr,
            "LowerBound": lower_bound,
            "UpperBound": upper_bound,
            # Outliers por Z-Score
            "Z-Score": max_zscore,
            "%OutL_Z_Thresh": porc_outliers_z
        }
    
    # Retornamos el DataFrame transpuesto
    return pd.DataFrame(summary).T

#######################################################

import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer

def imputador_k_NN(df, columnas_imputar, k=5, weights="uniform"):
    """
    Imputa valores nulos (NaN) en las columnas numéricas de 'df' 
    usando el método de k-vecinos más cercanos (KNNImputer).

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame que contiene los datos (incluyendo NaN) a imputar.
    columnas_imputar : list[str]
        Lista de nombres de columnas numéricas en las cuales se desea
        aplicar la imputación por k-NN.
    k : int, opcional
        Número de vecinos a considerar en la imputación. 
        Por defecto es 5.
    weights : str, opcional
        Tipo de ponderación a utilizar en la imputación. 
        Puede ser "uniform" o "distance". Por defecto es "uniform".
    
    Retorna
    -------
    df : pd.DataFrame
        El mismo DataFrame de entrada, pero con los valores nulos 
        imputados en las columnas indicadas.
    """
    # Creamos una copia de las columnas a imputar
    df_sub = df[columnas_imputar].copy()

    # Inicializamos el imputador KNN con los parámetros deseados
    imputer = KNNImputer(n_neighbors=k, weights=weights)

    # Ajustamos el imputador y transformamos 'df_sub'
    df_imputed_array = imputer.fit_transform(df_sub)

    # Convertimos el resultado a DataFrame, 
    # con el mismo índice y columnas que 'df_sub'
    df_imputed = pd.DataFrame(
        df_imputed_array, 
        columns=columnas_imputar, 
        index=df.index
    )

    # Reemplazamos las columnas originales por las imputadas
    for col in columnas_imputar:
        df[col] = df_imputed[col]

    return df

#######################################################

import seaborn as sns
import matplotlib.pyplot as plt

def calcular_correlaciones(df, cols_numericas=None, metodo="pearson"):
    """
    Calcula la matriz de correlaciones para un subconjunto de columnas numéricas en un DataFrame.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame que contiene los datos.
    cols_numericas : list[str] o None
        Lista de columnas numéricas a incluir en la matriz de correlación.
        Si es None, se seleccionan automáticamente las columnas numéricas.
    metodo : str
        Método de correlación. Puede ser 'pearson', 'spearman' o 'kendall'.

    Retorna:
    --------
    pd.DataFrame : Matriz de correlación resultante.
    """
    if cols_numericas is None:
        # Seleccionamos automáticamente columnas numéricas
        df_num = df.select_dtypes(include=["number"])
    else:
        df_num = df[cols_numericas]

    corr = df_num.corr(method=metodo)
    return corr


def plot_correlacion_heatmap(
    corr_matrix, 
    titulo="Matriz de Correlación", 
    cmap="coolwarm", 
    figsize=(11,12), 
    annot_fontsize=7
):
    """
    Genera un mapa de calor (heatmap) a partir de una matriz de correlación.

    Parámetros:
    -----------
    corr_matrix : pd.DataFrame
        Matriz de correlación.
    titulo : str
        Título para la gráfica.
    cmap : str
        Paleta de colores a usar (por defecto "coolwarm").
    figsize : tuple
        Tamaño de la figura (ancho, alto).
    annot_fontsize : int
        Tamaño de fuente de las anotaciones en el mapa de calor.
    """
    plt.figure(figsize=figsize)
    sns.heatmap(
        corr_matrix, 
        annot=True, 
        cmap=cmap, 
        fmt=".2f",          # formato numérico de las celdas
        square=True, 
        linewidths=0.5,
        annot_kws={"size": annot_fontsize},
        cbar_kws={"shrink": 0.5}  # reduce la barra de color al 50% de su tamaño original
    )
    plt.title(titulo, fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.show()

#######################################################

def boxplot_categ_num(df, cat_col, num_col, titulo="", figsize=(14,5)):
    """
    Genera un boxplot para visualizar la distribución de una variable numérica
    en función de una variable categórica.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con los datos.
    cat_col : str
        Columna categórica.
    num_col : str
        Columna numérica.
    titulo : str
        Título del gráfico.
    figsize : tuple
        Tamaño de la figura.
    """
    plt.figure(figsize=figsize)
    sns.boxplot(data=df, x=cat_col, y=num_col)
    plt.title(titulo, fontweight='bold', fontsize=14)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

#######################################################

import matplotlib.pyplot as plt
import seaborn as sns

def multivariado_dos_en_una_fila(df,
                                 x1, y1, hue1,
                                 x2, y2, hue2,
                                 titulo="Multivariado: Comparaciones en 2 Subplots"):
    """
    Realiza dos comparaciones multivariadas (scatterplot con hue) en una sola fila (2 subplots).

    - Subplot 1: df[x1] vs. df[y1], coloreado por df[hue1]
    - Subplot 2: df[x2] vs. df[y2], coloreado por df[hue2]

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con las columnas a analizar.
    x1, y1, hue1 : str
        Columnas para el 1er scatterplot multivariado:
          * x1: eje X
          * y1: eje Y
          * hue1: variable que define el color (tercera dimensión)
    x2, y2, hue2 : str
        Columnas para el 2do scatterplot multivariado.
    titulo : str
        Título global de la figura.
    """
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))
    fig.suptitle(titulo, fontweight='bold', fontsize=14)

    # ----- Subplot 1 -----
    sns.scatterplot(
        data=df,
        x=x1,
        y=y1,
        hue=hue1,         # Tercera variable para el color
        alpha=0.7,
        ax=ax1
    )
    ax1.set_title(f"{x1} vs {y1} (hue={hue1})", fontweight='bold')
    ax1.set_xlabel(x1)
    ax1.set_ylabel(y1)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # ----- Subplot 2 -----
    sns.scatterplot(
        data=df,
        x=x2,
        y=y2,
        hue=hue2,
        alpha=0.7,
        ax=ax2
    )
    ax2.set_title(f"{x2} vs {y2} (hue={hue2})", fontweight='bold')
    ax2.set_xlabel(x2)
    ax2.set_ylabel(y2)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    plt.tight_layout()
    plt.show()

#####################################################

import matplotlib.pyplot as plt
import seaborn as sns

def doble_grafico_bivariado(df,x1,y1,x2,y2,titulo="Bivariado: Comparaciones en 2 Subplots"):
    """
    Realiza dos comparaciones bivariadas (scatterplot) en una sola fila, con 2 subplots:
    
    - Subplot 1: df[x1] vs. df[y1]
    - Subplot 2: df[x2] vs. df[y2]

    Parámetros:
    -----------
    df    : pd.DataFrame
        DataFrame con las columnas a analizar.
    x1, y1: str
        Nombres de las columnas para el 1er scatterplot.
    x2, y2: str
        Nombres de las columnas para el 2do scatterplot.
    titulo: str
        Título global de la figura.
    """
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(11, 3))
    fig.suptitle(titulo, fontweight='bold', fontsize=14)

    # ----- Subplot 1 -----
    sns.scatterplot(
        data=df,
        x=x1,
        y=y1,
        alpha=0.7,
        color="blue",
        ax=ax1
    )
    ax1.set_title(f"{x1} vs {y1}", fontweight='bold')
    ax1.set_xlabel(x1)
    ax1.set_ylabel(y1)

    # ----- Subplot 2 -----
    sns.scatterplot(
        data=df,
        x=x2,
        y=y2,
        alpha=0.7,
        color="red",
        ax=ax2
    )
    ax2.set_title(f"{x2} vs {y2}", fontweight='bold')
    ax2.set_xlabel(x2)
    ax2.set_ylabel(y2)

    plt.tight_layout()
    plt.show()

#######################################################

import pandas as pd

def generar_diccionario_tipos(df_dict, sheet_name):
    """
    Genera un string que representa un diccionario de tipos de datos para cada columna de la hoja 
    especificada en el diccionario de DataFrames.

    La salida tendrá un formato similar a:
    
    diccionario_tipos_Dial-BAf = {
        "Año": "Int64",
        "Trimestre": "Int64",
        "Provincia": "category",
        "Tot_B_Ancha_Fija_x_Prov": "Int64",
        "Tot_DialUp_x_Prov": float,
        "Tot_DialUp_+_B_Ancha_Fija_x_Prov": "Int64"
    }
    
    Parámetros:
      - df_dict (dict): Diccionario de DataFrames (por ejemplo, el resultado de pd.read_excel(..., sheet_name=None)).
      - sheet_name (str): El nombre de la hoja a procesar.
    
    Retorna:
      str: Un string con la asignación del diccionario de tipos.
    """
    # Extrae el DataFrame correspondiente a la hoja
    if sheet_name not in df_dict:
        raise KeyError(f"El diccionario no contiene la hoja '{sheet_name}'")
    df = df_dict[sheet_name]
    
    header = f"diccionario_tipos_{sheet_name}"
    result = f"{header} = {{\n"
    
    for col in df.columns:
        dtype = df[col].dtype
        
        # Determinar la representación deseada según el tipo de dato.
        if isinstance(dtype, pd.CategoricalDtype):
            tipo_str = '"category"'
        elif pd.api.types.is_object_dtype(df[col]):
            tipo_str = "str"
        else:
            if dtype.name in ['int64', 'Int64']:
                tipo_str = '"Int64"'
            elif dtype.name in ['float64']:
                tipo_str = "float"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                tipo_str = "pd.Timestamp"
            else:
                tipo_str = f'"{dtype.name}"'
        result += f'    "{col}": {tipo_str},\n'
    result += "}"
    return result

#######################################################

# Función para obtener las hojas que contienen todos los campos indicados en 'lista_campos' y sus dimensiones.
def obtener_hojas_validas(lista_campos, df_dict, hojas_excluir=None):
    """
    Valida y crea una lista de hojas que contienen todos los campos indicados en 'lista_campos'.
    
    Parámetros:
      - lista_campos (list): Lista de nombres de campos requeridos.
      - df_dict (dict): Diccionario con DataFrames (clave: nombre de la hoja, valor: DataFrame).
      - hojas_excluir (list): Lista de nombres de hojas a excluir de la validación. 
                              Esta lista puede contener strings o tuplas donde el primer elemento es el nombre.
    
    Retorna:
      - list: Lista de tuplas (nombre de hoja, dimensionalidad) para las hojas que cumplen con tener todos los campos requeridos.
    """
    if hojas_excluir is None:
        hojas_excluir = []
    
    # Asegurarse de que la lista de exclusión sea solo de nombres (strings)
    hojas_excluir_nombres = []
    for item in hojas_excluir:
        if isinstance(item, tuple):
            hojas_excluir_nombres.append(item[0])
        else:
            hojas_excluir_nombres.append(item)
    
    hojas_validas = []
    for hoja, df in df_dict.items():
        # Si la hoja ya está en la lista de exclusión, la omitimos.
        if hoja in hojas_excluir_nombres:
            continue
        
        # Verificamos que la hoja contenga todos los campos requeridos.
        if all(campo in df.columns for campo in lista_campos):
            hojas_validas.append((hoja, df.shape))
    
    return hojas_validas

######################################################

# Función para validar y contar datos en campos especificos de un df:
import pandas as pd

def datos_unicos_hoja(item, campos):
    """
    Extrae los valores únicos de las columnas especificadas en 'campos' a partir de un item, y también
    cuenta cuántas veces aparece cada valor único. El parámetro 'item' es una tupla (sheet_name, data),
    donde data puede ser un DataFrame o un diccionario de DataFrames.
    
    Parámetros:
      - item (tuple): Una tupla (sheet_name, data) donde:
             * sheet_name (str): El nombre de la hoja.
             * data: Puede ser un DataFrame o un diccionario de DataFrames.
      - campos (dict): Diccionario donde cada clave es el nombre de la columna y el valor es 1 (imprimir)
                       o 0 (no imprimir) la información.
    
    Retorna:
      dict: Un diccionario donde cada clave es el nombre del campo y el valor es una tupla:
            (lista ordenada de valores únicos, diccionario de conteo de cada valor).
            Para columnas numéricas, se convierten los valores a enteros; de lo contrario, a cadenas.
    """
    sheet_name, data = item
    # Si data es un diccionario, extrae el DataFrame correspondiente a sheet_name.
    if isinstance(data, dict):
        if sheet_name in data:
            df = data[sheet_name]
        else:
            raise KeyError(f"El diccionario no contiene la hoja '{sheet_name}'")
    else:
        df = data

    result = {}
    for campo, imprimir_flag in campos.items():
        if campo in df.columns:
            # Convertir valores y obtener conteo
            if pd.api.types.is_numeric_dtype(df[campo]):
                # Para valores numéricos, convertir a int
                valores = sorted([int(x) for x in df[campo].dropna().unique()])
                # Obtenemos los conteos, convirtiendo las claves a int
                counts = {int(k): v for k, v in df[campo].dropna().value_counts().items()}
            else:
                valores = sorted([str(x) for x in df[campo].dropna().unique()])
                counts = {str(k): v for k, v in df[campo].dropna().value_counts().items()}
            result[campo] = (valores, counts)
            if imprimir_flag == 1:
                print(f"En la hoja '{sheet_name}', el campo {campo} tiene {len(valores)} valores únicos y son:\n{counts}\n")
        else:
            result[campo] = ([], {})
            if imprimir_flag == 1:
                print(f"En la hoja '{sheet_name}', el campo {campo} no se encuentra en el DataFrame.\n")
    return result

#######################################################

import unicodedata

def normalizar_texto(texto):
    """
    Elimina acentos y otros signos diacríticos de una cadena.
    """
    # Normaliza a forma 'NFKD' y codifica en ASCII ignorando errores, luego decodifica.
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

#######################################################

import pandas as pd
import re

def reemplazar_valor_en_hojas(df_dict, campo, cambio):
    """
    Recorre un diccionario de DataFrames (hojas de un Excel) y reemplaza en cada hoja
    los valores de la columna especificada que contengan la palabra a buscar, sustituyéndola
    por el nuevo valor.
    
    Parámetros:
      - df_dict (dict): Diccionario de DataFrames, donde la clave es el nombre de la hoja y 
                        el valor es el DataFrame.
      - campo (str): El nombre de la columna en la que se realizará la búsqueda y el reemplazo.
      - cambio (tuple): Una tupla (buscar, reemplazo) donde:
            * buscar (str): La palabra a buscar (la búsqueda es insensible a mayúsculas).
            * reemplazo (str): El valor con el que se reemplazará la palabra encontrada.
            
    Retorna:
      dict: El mismo diccionario de DataFrames, con la modificación aplicada a cada hoja donde exista la columna.
    """
    buscar, reemplazo = cambio
    for hoja, df in df_dict.items():
        if campo in df.columns:
            # Convertir la columna a string para asegurarse de que el método .str.replace funcione.
            df[campo] = df[campo].astype(str).str.replace(r'(?i)' + re.escape(buscar), reemplazo, regex=True)
            print(f"Se reemplazan valores en la hoja '{hoja}'.")
        '''else:
            print(f"En la hoja '{hoja}', el campo '{campo}' no se encuentra.")'''
    return df_dict

#######################################################

import pandas as pd
import datetime
import re

def convertidor_tipo_dato_campo(df_dict, campo, tipo_objetivo):
    """
    Recorre un diccionario de DataFrames y, para cada hoja que contenga la columna especificada (campo),
    convierte esa columna al tipo indicado (tipo_objetivo).

    Parámetros:
      - df_dict (dict): Diccionario de DataFrames (por ejemplo, el resultado de pd.read_excel(..., sheet_name=None)).
      - campo (str): Nombre de la columna a convertir.
      - tipo_objetivo: Tipo al que se desea convertir la columna. Por ejemplo, int o "Int64" (para enteros nullable),
                       float, bool, datetime, etc.
    
    Retorna:
      dict: El mismo diccionario de DataFrames, con la conversión aplicada en las hojas que contienen la columna.
    """
    for sheet, df in df_dict.items():
        if campo in df.columns:
            # Para enteros, se asume que la columna puede tener valores con caracteres extraños,
            # por lo que se extraen únicamente los dígitos y se convierte al tipo entero nullable "Int64".
            if tipo_objetivo in [int, "Int64"]:
                # Se convierte la columna a string, se extrae la primera secuencia de dígitos (uno o más)
                # y se convierte a número. Luego se asigna el tipo "Int64".
                df[campo] = pd.to_numeric(
                    df[campo].astype(str).str.extract(r'(\d+)')[0],
                    errors='coerce'
                ).astype("Int64")
            elif tipo_objetivo == float:
                df[campo] = pd.to_numeric(df[campo], errors='coerce')
            elif tipo_objetivo == bool:
                df[campo] = df[campo].apply(lambda x: str(x).strip().lower() in ['true', '1'] if pd.notna(x) else False)
            elif tipo_objetivo in [datetime.datetime, pd.Timestamp]:
                df[campo] = pd.to_datetime(df[campo], errors='coerce')
            else:
                # Para otros tipos, se usa la conversión estándar.
                df[campo] = df[campo].astype(tipo_objetivo)
        else:
            print(f"En la hoja '{sheet}', el campo '{campo}' no se encuentra.")
    return df_dict

#######################################################

import pandas as pd

def normalizar_y_categorizar_campo(df_dict, hojas, campo):
    """
    Recorre las hojas indicadas en el diccionario de DataFrames y normaliza el campo especificado.
    Para ello, elimina espacios, acentos y otros signos diacríticos de los valores, los pone en formato Title
    y convierte la columna a tipo category usando un conjunto global de categorías.
    
    Parámetros:
      - df_dict (dict): Diccionario de DataFrames (por ejemplo, obtenido con pd.read_excel(..., sheet_name=None)).
      - hojas (list): Lista de nombres (claves) de las hojas en las que se desea normalizar el campo.
      - campo (str): Nombre de la columna a normalizar (por ejemplo, "Partido").
    
    Retorna:
      dict: El diccionario de DataFrames con la columna especificada actualizada en las hojas indicadas.
    """
    from functions import normalizar_texto  # Asegúrate de que la función normalizar_texto esté definida en functions.py

    # Crear un conjunto para almacenar las categorías únicas globales del campo especificado
    categorias_global = set()
    
    # Recorremos cada hoja para recolectar las categorías únicas
    for hoja in hojas:
        df = df_dict.get(hoja)
        if df is not None and campo in df.columns:
            # Normalizamos la columna: convertimos a string, quitamos espacios, aplicamos normalizar_texto y Title Case
            serie_norm = df[campo].astype(str).str.strip().apply(normalizar_texto).str.title()
            categorias_global.update(serie_norm.unique())
    
    # Eliminamos posibles valores 'nan'
    categorias_global = {cat for cat in categorias_global if cat.lower() != 'nan'}
    # Convertir a lista ordenada
    categorias_global = sorted(categorias_global)
    
    print(f"Categorías globales para '{campo}':", categorias_global)
    print("Cantidad de categorías únicas:", len(categorias_global))
    
    # Recorremos nuevamente las hojas y actualizamos la columna especificada convirtiéndola a tipo category
    for hoja in hojas:
        df = df_dict.get(hoja)
        if df is not None and campo in df.columns:
            df[campo] = pd.Categorical(
                df[campo].astype(str).str.strip().apply(normalizar_texto).str.title(),
                categories=categorias_global,
                ordered=False  # Puedes cambiar a True si necesitas un orden específico
            )
    return df_dict

#######################################################

import pandas as pd

def normalizar_y_cast_numero(df_dict, hojas, campos):
    """
    Recorre las hojas indicadas en el diccionario de DataFrames y normaliza los campos especificados,
    extrayendo la primera secuencia de dígitos de cada valor, para luego hacer casting a entero nullable ("Int64").
    
    Parámetros:
      - df_dict (dict): Diccionario de DataFrames (por ejemplo, obtenido con pd.read_excel(..., sheet_name=None)).
      - hojas (list): Lista de nombres (claves) de las hojas en las que se desea normalizar y convertir los campos.
      - campos (list): Lista de nombres de columnas a procesar (por ejemplo, ["Año", "Trimestre"]).
    
    Retorna:
      dict: El diccionario de DataFrames con los campos especificados actualizados.
    """
    # Para cada hoja en la lista indicada:
    for hoja in hojas:
        df = df_dict.get(hoja)
        if df is not None:
            for campo in campos:
                if campo in df.columns:
                    # Convertir a string, quitar espacios, aplicar normalización (si se requiere)
                    # y extraer la primera secuencia de dígitos.
                    df[campo] = pd.to_numeric(
                        df[campo].astype(str)
                                .str.strip()
                                .apply(lambda x: x if x != "" else None)
                                .str.extract(r'(\d+)', expand=False),
                        errors='coerce'
                    ).astype("Int64")
                else:
                    print(f"El campo '{campo}' no se encuentra en la hoja '{hoja}'.")
    return df_dict

#######################################################

import pandas as pd

def fusionar_hojas_por_campos(df_dict, lista_hojas, lista_campos):
    """
    Fusiona las hojas especificadas en 'lista_hojas' (todas contenidas en df_dict)
    utilizando como llaves de unión los campos en 'lista_campos'.

    Parámetros:
    -----------
    - df_dict (dict): Diccionario de DataFrames, donde la clave es el nombre de la hoja
                      y el valor es el DataFrame correspondiente.
    - lista_hojas (list): Lista de nombres de las hojas a fusionar.
    - lista_campos (list): Lista de nombres de campos que sirven como llave compuesta de fusión.

    Retorna:
    --------
    pd.DataFrame
        DataFrame resultante de la fusión externa (outer join) de las hojas indicadas.
        Si no se pudo fusionar ninguna (por ausencia de hojas o campos), devuelve un DataFrame vacío.
    """
    df_fusionado = None  # Aquí iremos acumulando la fusión

    for hoja in lista_hojas:
        # Verificamos que la hoja exista en el diccionario
        if hoja not in df_dict:
            print(f"Advertencia: La hoja '{hoja}' no está en el diccionario. Se omite.")
            continue

        df_actual = df_dict[hoja]

        # Verificamos que todos los campos de 'lista_campos' existan en la hoja
        campos_faltantes = [campo for campo in lista_campos if campo not in df_actual.columns]
        if campos_faltantes:
            print(f"Advertencia: La hoja '{hoja}' no contiene estos campos: {campos_faltantes}. Se omite.")
            continue

        # Si es la primera hoja válida, la copiamos para iniciar la fusión
        if df_fusionado is None:
            df_fusionado = df_actual.copy()
        else:
            # Fusionamos (outer join) con el DataFrame acumulado
            df_fusionado = pd.merge(
                df_fusionado,
                df_actual,
                on=lista_campos,
                how='outer',
                suffixes=('', '_dup')
            )

            # (Opcional) Si deseas eliminar columnas duplicadas:
            # por ejemplo, si en dos hojas había columnas con el mismo nombre,
            # la fusión las renombra con '_dup'. Puedes decidir aquí qué hacer con ellas.
            # for col in df_fusionado.columns:
            #     if col.endswith('_dup'):
            #         # Lógica para eliminar o combinar esa columna
            #         ...
    
    # Si df_fusionado sigue siendo None, significa que ninguna hoja era válida
    if df_fusionado is None:
        return pd.DataFrame()

    return df_fusionado

#######################################################

def fusionar_por_campos(campo_id, lista_hojas, df_dict):
    """
    Fusiona (merge) las hojas indicadas en 'lista_hojas' usando los campos en 'campo_id'
    como llaves para la unión a nivel de cada fila.
    
    Para cada DataFrame en la lista, se verifica que contenga todos los campos indicados en 
    'campo_id'. Luego, se fusionan los DataFrames mediante un outer join, de modo que se combinan 
    aquellas filas donde el valor de cada campo en 'campo_id' coincide en ambos DataFrames.
    
    Por ejemplo, si 'campo_id' es ["Año", "Trimestre"] y se tienen tres DataFrames que incluyen una fila 
    con Año = 2024 y Trimestre = 3, entonces las filas correspondientes a esos valores se fusionarán en 
    una única fila, combinando la información de las hojas involucradas.
    
    Parámetros:
      - campo_id (list): Lista de nombres de campos que se utilizarán como llaves para la fusión 
                         (por ejemplo, ["Año", "Trimestre"]).
      - lista_hojas (list): Lista de nombres (strings) de las hojas (claves) a fusionar.
      - df_dict (dict): Diccionario que contiene los DataFrames, donde la clave es el nombre de la hoja 
                        y el valor es el DataFrame.
      
    Retorna:
      DataFrame: Resultado de la fusión externa (outer join) de los DataFrames, combinando las filas 
                 donde los valores de los campos en 'campo_id' coinciden.
    """
    df_fusionado = None

    for hoja in lista_hojas:
        # Verifica si la hoja se encuentra en el diccionario; si no, la omite.
        if hoja not in df_dict:
            print(f"La hoja '{hoja}' no se encuentra en el diccionario. Se omite.")
            continue

        # Obtiene el DataFrame correspondiente a la hoja.
        df = df_dict[hoja]

        # Verifica que el DataFrame contenga todos los campos indicados en 'campo_id'.
        if not all(campo in df.columns for campo in campo_id):
            print(f"La hoja '{hoja}' no contiene alguno de los campos {campo_id}. Se omite.")
            continue

        # Si es el primer DataFrame válido, lo copia en df_fusionado.
        if df_fusionado is None:
            df_fusionado = df.copy()
        else:
            # Fusiona el DataFrame actual con el acumulado usando un outer join.
            # Esto combina las filas donde los valores en los campos de 'campo_id' coinciden.
            df_fusionado = pd.merge(df_fusionado, df, on=campo_id, how='outer', suffixes=('', '_dup'))

    # Si no se fusionó ningún DataFrame, retorna un DataFrame vacío.
    if df_fusionado is None:
        return pd.DataFrame()
    
    return df_fusionado





# Función para convertir los tipos de datos de las columnas de un DataFrame según un diccionario de tipos.
def convertir_tipos(df, diccionario):
    """
    Convierte los tipos de datos de las columnas de un DataFrame según un diccionario de tipos.
    Parámetros:
    ------------
    df : pd.DataFrame - DataFrame a convertir.
    diccionario : dict - Diccionario con los tipos de datos esperados para cada columna.
    Retorno:
    ---------
    pd.DataFrame - DataFrame con los tipos de datos convert
    """
    for columna, tipo_esperado in diccionario.items():
        # Primero se verifica que la columna exista en el DataFrame.
        if columna in df.columns:
            # Si el tipo esperado es 'int', se convierte la columna a número entero:
            # 1. pd.to_numeric intenta convertir a número; en caso de error, reemplaza con NaN.
            # 2. fillna(0) reemplaza los NaN por 0.
            # 3. astype(int) convierte la columna a entero.
            if tipo_esperado == int:
                df[columna] = pd.to_numeric(df[columna], errors='coerce').fillna(0).astype(int)
            # Si el tipo esperado es 'float', se convierte la columna a número flotante.
            elif tipo_esperado == float:
                df[columna] = pd.to_numeric(df[columna], errors='coerce')
            # Si el tipo esperado es 'bool', se convierte la columna a booleano.
            # La conversión se hace comparando el valor (tras limpiarlo) con 'true' o '1'.
            elif tipo_esperado == bool:
                df[columna] = df[columna].apply(lambda x: str(x).strip().lower() in ['true', '1'] if pd.notna(x) else False)
            # Si el tipo esperado es una lista o un diccionario, se verifica si el valor es una cadena
            # y se utiliza la función auxiliar 'convertir_a_estructura' para intentar convertirlo.
            elif tipo_esperado in [list, dict]:
                df[columna] = df[columna].apply(lambda x: convertir_a_estructura(x, tipo_esperado) if isinstance(x, str) else x)
            # Si el tipo esperado es una fecha (ya sea 'datetime' o 'pd.Timestamp'),
            # se convierte la columna a formato datetime usando pd.to_datetime.
            elif tipo_esperado in [datetime, pd.Timestamp]:
                df[columna] = pd.to_datetime(df[columna], errors='coerce')
            # En caso de que no se trate de un tipo especial, se convierte la columna a cadena de texto.
            else:
                df[columna] = df[columna].astype(str).fillna("")
    # Se retorna el DataFrame con las conversiones aplicadas.
    return df

# Función auxiliar para convertir strings en listas o diccionarios de forma segura
def convertir_a_estructura(valor, tipo_esperado):
    """
    Convierte un valor string en una lista o diccionario si es posible, de lo contrario retorna el valor original.

    Parámetros:
    -----------
    valor : str
        Valor que potencialmente es una lista o un diccionario en formato string.
    tipo_esperado : type
        Tipo esperado (list o dict).

    Retorno:
    --------
    list/dict/None
        Retorna el objeto convertido o None si la conversión falla.
    """
    try:
        if isinstance(valor, str):
            resultado = ast.literal_eval(valor)
            return resultado if isinstance(resultado, tipo_esperado) else None
        return valor  # Si ya es list o dict, lo devuelve tal cual
    except (ValueError, SyntaxError):
        return None
    
#######################################################

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

def visualizacion_distribucion(df, columna, titulo=""):
    """
    Genera una cuadrícula de 2x2 con visualizaciones de la distribución de la columna especificada:
      1. Histograma + KDE
      2. Boxplot
      3. Q-Q Plot (comparación con distribución Normal)
      4. Violin Plot
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame que contiene la columna a analizar.
    columna : str
        Nombre de la columna (numérica) a graficar.
    titulo : str (opcional)
        Título base a mostrar en la figura.
    """

    # Calculamos skewness y kurtosis
    serie_no_nula = df[columna].dropna()
    kurt = serie_no_nula.kurt()
    skew = serie_no_nula.skew()

    # Creamos la figura y ejes
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 8))

    # Ajusta el espacio entre los subplots e imprime titulo con fontweight='bold', fontsize=18
    fig.suptitle(
        f"{titulo}\nKurtosis={kurt:.2f} - Skewness={skew:.2f}",
        fontweight='bold',
        fontsize=18,
        y=1.02
    )

    # 1) Histograma + KDE (arriba-izquierda)
    sns.histplot(
        data=df, 
        x=columna, 
        kde=True, 
        color='skyblue', 
        ax=axes[0, 0]
    )
    axes[0, 0].set_title(f"Histograma + KDE de '{columna}'", fontweight='bold', fontsize=16)
    
    # Ajuste de etiquetas del eje X e Y (tamaño de fuente de los ticks)
    axes[0, 0].tick_params(axis='both', labelsize=14)
    # Ajuste del label del eje X (si deseas uno específico)
    axes[0, 0].set_xlabel(columna, fontsize=14)
    axes[0, 0].set_ylabel("Frecuencia", fontsize=14)

    # 2) Boxplot (arriba-derecha)
    sns.boxplot(
        data=df, 
        x=columna, 
        color='lightgreen', 
        ax=axes[0, 1]
    )
    axes[0, 1].set_title(f"Boxplot de '{columna}'", fontweight='bold', fontsize=16)
    axes[0, 1].tick_params(axis='both', labelsize=14)
    axes[0, 1].set_xlabel(columna, fontsize=14)

    # 3) Q-Q Plot (abajo-izquierda)
    (osm, osr), (slope, intercept, r) = stats.probplot(serie_no_nula, dist="norm")

    axes[1, 0].scatter(
        osm,
        osr,
        alpha=0.5,          # Transparencia en el relleno
        c='b',              # Color de relleno de los puntos
        edgecolors='none',  # Quita los bordes de los puntos
        label='Data'
    )

    xx = np.linspace(min(osm), max(osm), 100)
    yy = slope * xx + intercept
    axes[1, 0].plot(xx, yy, 'r--', label='Recta Ajuste')
    axes[1, 0].set_title(f"Q-Q Plot de '{columna}' vs Normal", fontweight='bold', fontsize=16)
    axes[1, 0].tick_params(axis='both', labelsize=14)
    axes[1, 0].legend(fontsize=14)

    # 4) Violin Plot (abajo-derecha)
    sns.violinplot(
        data=df, 
        x=columna, 
        color='pink', 
        ax=axes[1, 1]
    )
    axes[1, 1].set_title(f"Violin Plot de '{columna}'", fontweight='bold', fontsize=16)
    axes[1, 1].tick_params(axis='both', labelsize=14)
    axes[1, 1].set_xlabel(columna, fontsize=14)

    # Ajuste de espacios para evitar solapamientos
    plt.tight_layout(rect=[0, 0, 1, 1.03])
    plt.show()

def imputar_valor(df, campos, metodo="media"):
    """
    Imputa los valores nulos de las columnas especificadas en 'campos' 
    siguiendo la estrategia indicada en 'metodo'.

    Parámetros:
    -----------
    df : pd.DataFrame
        El DataFrame en el que se realizará la imputación.
    campos : list
        Lista de nombres de columnas a imputar.
    metodo : str, int o float
        Puede tomar los siguientes valores:
            - "media": Imputa con la media aritmética.
            - "mediana": Imputa con la mediana.
            - "moda": Imputa con la moda (el valor más frecuente).
            - "minimo": Imputa con el valor mínimo de la columna.
            - "maximo": Imputa con el valor máximo de la columna.
            - Si se proporciona un número (int o float), se utilizará 
              ese valor fijo para la imputación.
        Por defecto es "media".

    Retorna:
    --------
    pd.DataFrame
        El DataFrame con las columnas especificadas imputadas.
    """
    for campo in campos:
        if campo not in df.columns:
            print(f"El campo '{campo}' no se encontró en el DataFrame.")
            continue
        
        # Determinamos el valor de imputación según 'metodo'
        if metodo == "media":
            valor_imputacion = df[campo].mean()
        elif metodo == "mediana":
            valor_imputacion = df[campo].median()
        elif metodo == "moda":
            # Si hay más de una moda, se toma la primera
            valor_imputacion = df[campo].mode(dropna=True)
            if not valor_imputacion.empty:
                valor_imputacion = valor_imputacion.iloc[0]
            else:
                # En caso de que la columna sea completamente nula o no haya moda válida
                valor_imputacion = None  
        elif metodo == "minimo":
            valor_imputacion = df[campo].min()
        elif metodo == "maximo":
            valor_imputacion = df[campo].max()
        elif isinstance(metodo, (int, float)):
            # Si es un número, lo usamos directamente
            valor_imputacion = metodo
        else:
            print(f"Advertencia: método '{metodo}' no reconocido. Se omite la imputación en '{campo}'.")
            continue
        
        # Imputamos si obtuvimos un valor válido
        if valor_imputacion is not None:
            df[campo] = df[campo].fillna(valor_imputacion)
        else:
            print(f"No se pudo imputar la columna '{campo}' con el método '{metodo}'.")
    
    return df

#######################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def transformar_y_visualizar(df, campo, log_transform=False, sqrt_transform=False,
                             mostrar_hist=True, mostrar_box=True, mostrar_qq=True, c=1):
    """
    Aplica una transformación al campo indicado y visualiza la comparación antes y después.
    
    Parámetros:
      - df (DataFrame): El DataFrame que contiene la columna a transformar.
      - campo (str): Nombre de la columna a transformar (debe ser numérica).
      - log_transform (bool): Si es True, aplica transformación logarítmica: log(x + c).
      - sqrt_transform (bool): Si es True, aplica transformación raíz cuadrada: sqrt(x).
          Nota: Si ambas son True, primero se aplica la logarítmica y luego la raíz cuadrada.
      - mostrar_hist (bool): Si True, muestra histogramas.
      - mostrar_box (bool): Si True, muestra boxplots.
      - mostrar_qq (bool): Si True, muestra Q-Q plots.
      - c (float): Constante a sumar para evitar problemas con valores cero en la transformación logarítmica.
    
    Retorna:
      DataFrame: Una copia del DataFrame con una nueva columna llamada campo_transf que contiene la variable transformada.
    """
    # Aseguramos que la columna existe y es numérica
    if campo not in df.columns:
        raise KeyError(f"La columna '{campo}' no se encuentra en el DataFrame.")
    if not pd.api.types.is_numeric_dtype(df[campo]):
        raise TypeError(f"La columna '{campo}' no es numérica, no se puede transformar.")

    # Copiamos el DataFrame para no modificar el original
    df_mod = df.copy()
    
    # Guardamos la serie original
    original = df_mod[campo]
    
    # Aplicamos la transformación solicitada
    transformada = original.copy()
    if log_transform:
        # Para evitar problemas con ceros, sumamos una constante c
        transformada = np.log(transformada + c)
    if sqrt_transform:
        transformada = np.sqrt(transformada)
    
    # Agregamos la columna transformada con un sufijo
    nuevo_campo = campo + "_transf"
    df_mod[nuevo_campo] = transformada

    # Creamos una figura con tres subplots (histograma, boxplot, Q-Q plot) comparando original y transformada
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12, 7))
    fig.suptitle(f"Comparación antes y después de la transformación en '{campo}'", fontsize=16)
    
    # Histogramas
    if mostrar_hist:
        axes[0,0].hist(original.dropna(), bins=20, color='skyblue', edgecolor='black')
        axes[0,0].set_title(f"Histograma Original: {campo}")
        axes[0,1].hist(transformada.dropna(), bins=20, color='salmon', edgecolor='black')
        axes[0,1].set_title(f"Histograma Transformado: {nuevo_campo}")
    else:
        axes[0,0].axis('off')
        axes[0,1].axis('off')
        
    # Boxplots
    if mostrar_box:
        axes[1,0].boxplot(original.dropna())
        axes[1,0].set_title(f"Boxplot Original: {campo}")
        axes[1,1].boxplot(transformada.dropna())
        axes[1,1].set_title(f"Boxplot Transformado: {nuevo_campo}")
    else:
        axes[1,0].axis('off')
        axes[1,1].axis('off')
        
    # Q-Q Plots
    if mostrar_qq:
        # Q-Q plot para datos originales
        stats.probplot(original.dropna(), dist="norm", plot=axes[2,0])
        axes[2,0].set_title(f"Q-Q Plot Original: {campo}")
        # Q-Q plot para datos transformados
        stats.probplot(transformada.dropna(), dist="norm", plot=axes[2,1])
        axes[2,1].set_title(f"Q-Q Plot Transformado: {nuevo_campo}")
    else:
        axes[2,0].axis('off')
        axes[2,1].axis('off')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
    
    return df_mod

#######################################################

import pandas as pd

def crear_fecha_trimestral_df(df, anio_col="Año", trimestre_col="Trimestre"):
    """
    A partir de las columnas 'Año' y 'Trimestre' de un DataFrame, crea una nueva columna 'Fecha' que
    representa el primer día del trimestre correspondiente. Se asume que 'Trimestre' toma valores de 1 a 4,
    con la siguiente correspondencia:
      - 1 -> 01/01/Año
      - 2 -> 01/04/Año
      - 3 -> 01/07/Año
      - 4 -> 01/10/Año

    Luego, el DataFrame se ordena cronológicamente por 'Fecha', se reinician los índices y se reordena
    de modo que 'Fecha' quede en la primera posición.

    Parámetros:
      - df (DataFrame): El DataFrame que contiene las columnas de año y trimestre.
      - anio_col (str): Nombre de la columna que contiene el año (por defecto "Año").
      - trimestre_col (str): Nombre de la columna que contiene el número de trimestre (por defecto "Trimestre").

    Retorna:
      DataFrame: Una copia del DataFrame con la nueva columna 'Fecha' en la primera posición y ordenado por ella.
    """
    df_mod = df.copy()

    def asignar_fecha(row):
        try:
            anio = int(row[anio_col])
            trimestre = int(row[trimestre_col])
        except Exception:
            return pd.NaT
        
        if trimestre == 1:
            return pd.Timestamp(year=anio, month=1, day=1)
        elif trimestre == 2:
            return pd.Timestamp(year=anio, month=4, day=1)
        elif trimestre == 3:
            return pd.Timestamp(year=anio, month=7, day=1)
        elif trimestre == 4:
            return pd.Timestamp(year=anio, month=10, day=1)
        else:
            return pd.NaT

    # Crear la columna "Fecha"
    df_mod["Fecha"] = df_mod.apply(asignar_fecha, axis=1)
    # Ordenar el DataFrame por la nueva columna "Fecha"
    df_mod.sort_values("Fecha", inplace=True)
    df_mod.reset_index(drop=True, inplace=True)
    # Reordenar las columnas para que "Fecha" quede en la primera posición
    cols = df_mod.columns.tolist()
    cols.remove("Fecha")
    df_mod = df_mod[["Fecha"] + cols]
    
    return df_mod

#######################################################

import matplotlib.pyplot as plt
import pandas as pd

def graficar_listas_a_doble_eje(
    eje,                                # Subplot donde se graficará
    df,                                 # DataFrame con los datos (debe contener col_x, cols_izq y cols_der)
    col_x,                              # Nombre de la columna en df para el eje X (ej. 'Fecha')
    cols_izq,                           # Listas de columnas para el eje izquierdo (pueden ser varias series)
    labels_izq,                         # Etiquetas para las series del eje izquierdo (misma longitud que cols_izq)
    cols_der,                           # Listas de columnas para el eje derecho (pueden ser varias series)
    labels_der,                         # Etiquetas para las series del eje derecho (misma longitud que cols_der)
    label_eje_izq="Eje Izquierdo",      # Etiqueta general del eje izquierdo (lo que va en eje.set_ylabel())
    label_eje_der="Eje Derecho",        # Etiqueta general del eje derecho (lo que va en eje_derecho.set_ylabel())
    titulo="",                          # Título del subplot
    ncol_leyenda=4,                     # Número de columnas en la leyenda combinada
    rotar_x=90,                         # Grados de rotación de las etiquetas del eje X
    colores_izq=None,                   # Lista de colores para las series del eje izquierdo
    colores_der=None                    # Lista de colores para las series del eje derecho
):
    """
    Dibuja en 'eje' un gráfico de líneas con un eje izquierdo (varias series) y
    un eje derecho (varias series).

    Parámetros:
    -----------
    eje : matplotlib.axes.Axes
        Subplot donde se graficará.
    df : pd.DataFrame
        DataFrame con los datos (debe contener col_x, cols_izq y cols_der).
    col_x : str
        Nombre de la columna en df para el eje X (ej. 'Fecha').
    cols_izq : list[str]
        Columnas para el eje izquierdo (varias series).
    labels_izq : list[str]
        Etiquetas para las series del eje izquierdo (misma longitud que cols_izq).
    label_eje_izq : str
        Etiqueta que describe globalmente al eje izquierdo (p.ej. "Penetración x100 Hogares").
    cols_der : list[str]
        Columnas para el eje derecho (varias series).
    labels_der : list[str]
        Etiquetas para las series del eje derecho (misma longitud que cols_der).
    label_eje_der : str
        Etiqueta global del eje derecho (p.ej. "Accesos").
    titulo : str (opcional)
        Título para este subplot.
    ncol_leyenda : int (opcional)
        Número de columnas en la leyenda combinada.
    rotar_x : int (opcional)
        Grados de rotación de las etiquetas del eje X (por defecto 90).
    colores_izq : list[str] o None
        Lista de colores para las series del eje izquierdo.
        Si es None, se usa la paleta por defecto de matplotlib.
    colores_der : list[str] o None
        Lista de colores para las series del eje derecho.
        Si es None, se usa la paleta por defecto de matplotlib.

    Retorna:
    --------
    None. Dibuja en el eje provisto.
    """

    # Eje derecho gemelo
    eje_derecho = eje.twinx()

    # Título y configuraciones
    eje.set_title(titulo)
    eje.set_xlabel(col_x)

    # Si no hay colores_izq, los dejamos en None
    if colores_izq is None:
        colores_izq = [None]*len(cols_izq)
    # Si no hay colores_der, los dejamos en None
    if colores_der is None:
        colores_der = [None]*len(cols_der)

    # ===================== EJE IZQUIERDO =====================
    lineas_izq = []
    # Graficar las series del eje izquierdo
    for i, (col, lab) in enumerate(zip(cols_izq, labels_izq)):
        color_linea = colores_izq[i % len(colores_izq)]
        l, = eje.plot(
            df[col_x],
            df[col],
            marker='.',
            linewidth=3,
            color=color_linea,
            label=lab
        )
        lineas_izq.append(l)

    # Elegimos el color para el nombre del eje izquierdo:
    # Si la primera serie no tiene color definido (None), usamos 'black'.
    # De lo contrario, usamos el color de la primera serie.
    if len(colores_izq) > 0 and colores_izq[0] is not None:
        eje_izq_color = colores_izq[0]
    else:
        eje_izq_color = 'black'

    eje.set_ylabel(label_eje_izq, color=eje_izq_color)
    eje.tick_params(axis='y', labelcolor=eje_izq_color)

    # ===================== EJE DERECHO =====================
    lineas_der_plot = []
    # Graficar las series del eje derecho
    for j, (col, lab) in enumerate(zip(cols_der, labels_der)):
        color_linea = colores_der[j % len(colores_der)]
        l2, = eje_derecho.plot(
            df[col_x],
            df[col],
            marker='s',
            linewidth=2,
            color=color_linea,
            label=lab
        )
        lineas_der_plot.append(l2)

    # Elegimos el color para el nombre del eje derecho (análogo al izquierdo).
    if len(colores_der) > 0 and colores_der[0] is not None:
        eje_der_color = colores_der[0]
    else:
        eje_der_color = 'blue'

    eje_derecho.set_ylabel(label_eje_der, color=eje_der_color)
    eje_derecho.tick_params(axis='y', labelcolor=eje_der_color)

    # ===================== LEYENDA COMBINADA =====================
    # Recuperar líneas y etiquetas de ambos ejes
    lineas_izq_, etiquetas_izq_ = eje.get_legend_handles_labels()
    lineas_der_, etiquetas_der_ = eje_derecho.get_legend_handles_labels()

    # Unimos todo
    lineas_combinadas = lineas_izq_ + lineas_der_
    etiquetas_combinadas = etiquetas_izq_ + etiquetas_der_

    # Ubicar la leyenda debajo del subplot
    eje.legend(
        lineas_combinadas,
        etiquetas_combinadas,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.25),
        ncol=ncol_leyenda
    )

    # ===================== EJE X =====================
    eje.set_xticks(df[col_x])
    if pd.api.types.is_datetime64_any_dtype(df[col_x]):
        eje.set_xticklabels(df[col_x].dt.strftime("%Y-%m"), rotation=rotar_x)
    else:
        eje.set_xticklabels(df[col_x], rotation=rotar_x)

    # ===================== CUADRÍCULA =====================
    eje.grid(True, which='both', linestyle='--', alpha=0.3)