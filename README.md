
```
PROYECTO-FINAL-GRUPAL/ (Rama_salopezna)
├── data/
│   └── ... 
├── services/                      # Carpeta para almacenar cada servicio a implementar
│   │                           
│   ├── airflow/                   # Carpeta almacenadora de todo lo requerido para el servicio de Airflow
│   │   ├── Dockerfile             # Contenedor con instrucciones de la imagen de Airflow (el orquestador de tareas)
│   │   └── dags/                  # DAG principal de Airflow, indica el orden (sin ciclos repetitivos) ejecución tareas
│   │                              # (p.ej: 1.cargar archivos JSON, 2.luego transformarlos, 3.luego insertarlos en DB).
│   ├── fastapi/                   # Carpeta almacenadora de todo lo requerido para el servicio de FastApi
│   │   ├── Dockerfile             # Contenedor con instrucciones de la imagen de FastAPI (para crear un microservicio)
│   │   └── main.py                #
│   │                           
│   ├── streamlit/                 # Carpeta almacenadora de todo lo requerido para el servicio de Streamlit (visualización)
│   │   ├── Dockerfile             # Contenedor con instrucciones de la imagen de Streamlit (opcional para Dashboard)
│   │   └── app.py                 #
│   │                           
│   └── ml/                        # Carpeta almacenadora de todo lo referente a ML
│       ├── Dockerfile             #
│       ├── scripts/               #
│       │   └── functions.py       #
│       │   └── test_etl.ipynb     #               
│       └── models/                # Carpeta almacenadora de modelos entrenados de ML
│           └── model.pkl          # Modelo entrenado con ML para predictores y/o recomendadores
│                           
├── docker-compose.yml             # Archivo con instrucciones para Orquestar los contenedores (Postgres, Airflow, etc.)
├── requirements.txt               # Lista de librerías de Python requeridas (por ejemplo pandas, numpy, sqlalchemy, etc.)
├── .gitignore                     # Archivo con lista de darpetas y archivos a ingnorar por GitHub (archivos pesados)
└── README.md
```

# 1. Visión general de nuestra arquitectura

### Almacenamiento de datos crudos (Data Lake)
En nuestro proyecto, almacenaríamos los archivos JSON/CSV/Parquet provenientes de Google y Yelp en un repositorio externo a los contenedores. De esta forma, evitaríamos inflar las imágenes de Docker y depender de contenedores efímeros.  
- **En la nube (GCS)**: Utilizaríamos un bucket como nuestro **Data Lake** para alojar parte de la data de Google (archivos JSON en la carpeta `metadata-google`). Así, recrearíamos un entorno real en la nube y simularíamos la llegada y actualización periódica de sitios registrados en Google Maps.  
- **Entorno local**: Por temas de peso y practicidad, seguiríamos manejando el resto de la data en una carpeta montada como volumen Docker (`./data/raw`).  
- Además, consideraríamos almacenar los modelos de ML entrenados en la nube, para mantenerlos seguros en caso de que los contenedores se caigan.

### Base de datos relacional (PostgreSQL)
En esta arquitectura, emplearíamos PostgreSQL para guardar la información **estructurada** y depurada (p. ej., catálogos de establecimientos, reviews normalizadas, métricas agregadas). Configuraríamos un **volumen persistente** para que la base de datos no se pierda si el contenedor se cae.

### Airflow (contenedor)
Airflow sería nuestro orquestador de tareas ETL y ML.  
- Nuestros DAGs se encargarían de:  
  1. **Extraer** datos del Data Lake (GCS) y de la carpeta local cruda.  
  2. **Transformarlos** y **cargarlos** en la base de datos.  
  3. **Entrenar** o **reentrenar** modelos de ML.  
- Programaríamos reentrenamientos periódicos, limpiezas de datos y cualquier otro flujo de trabajo que quisiéramos automatizar.

### Contenedor de ML
En este contenedor concentraríamos los scripts de preprocesamiento, entrenamiento y validación de modelos.  
- Utilizaríamos la **misma base de datos** (PostgreSQL) para leer la información y, si lo necesitáramos, consultaríamos el Data Lake en GCS o la carpeta local.  
- Al final, generaríamos un **modelo entrenado** (por ejemplo, `model.pkl`) y lo almacenaríamos en una carpeta montada o, de ser necesario, en la nube para no perderlo en caso de reinicio del contenedor.

### FastAPI (contenedor)
FastAPI expondría endpoints de **predicción** o recomendaciones.  
- Cargaría el modelo entrenado desde el volumen persistente (o desde GCS) al arrancar.  
- Se conectaría a la base de datos para obtener datos adicionales cuando fuera necesario (por ejemplo, información de los establecimientos).

### Streamlit o Power BI
Para la parte de visualización y dashboards:  
- **Streamlit** (contenedor) se conectaría a la base de datos o a los endpoints de FastAPI para mostrar KPIs, gráficas y análisis interactivos.  
- **Power BI** (externo) podría enlazarse directamente con nuestra DB o con un endpoint de FastAPI para refrescar datos y presentar informes.

> **Clave**: Todos los contenedores que requirían datos se conectarían a la **DB** o al Data Lake/carpeta local donde los guardaríamos. Tanto la base de datos como los datos crudos y los modelos se manejarían con volúmenes persistentes (o servicios de almacenamiento en la nube), de modo que no los perderíamos si un contenedor se elimina.

---

# 2. Flujo de datos resumido

### Ingesta
Recibiríamos archivos JSON/CSV de Google y Yelp, ubicándolos en `./data/raw` (para la parte local) o en nuestro bucket GCS (para el Data Lake de Google). Airflow se encargaría de detectar o programar la ingesta y, a través de los scripts de ETL, insertaríamos la información en la base de datos.

### Transformación
Realizaríamos la limpieza, validación y normalización de los datos. Después, actualizaríamos PostgreSQL. Opcionalmente, crearíamos tablas analíticas o un warehouse adicional para consultas más especializadas.

### Entrenamiento
Lanzaríamos un DAG de Airflow que entrenaría o reentrenaría nuestros modelos (en el contenedor ML o con PythonOperators). Leeríamos los datos de PostgreSQL (o directamente de la carpeta/bucket crudo) y guardaríamos el modelo final en un volumen, como `./models/`, o en GCS para mayor seguridad.

### Consumo
FastAPI cargaría el modelo entrenado en memoria al iniciarse (o cuando recibiera la primera solicitud). Streamlit, Power BI u otras herramientas consultarían FastAPI para obtener predicciones y visualizaciones, o bien accederían directamente a la base de datos y al modelo.

### Reentrenamiento continuo
Periódicamente, programaríamos en Airflow la re-ejecución del DAG para incorporar nuevos datos y reentrenar el modelo. Si FastAPI utilizara el modelo en memoria, podríamos reiniciar el contenedor para que cargue la versión más reciente.

---

# 3. Almacenamiento y persistencia

### Data cruda (local y nube)
Montaríamos `./data/raw` como un volumen en Docker para parte de la data, y utilizaríamos GCS como Data Lake para la porción correspondiente a Google (simulando un escenario real de llegada y actualización de datos). Evitaríamos incluir decenas de GB dentro de nuestras imágenes de Docker para no inflarlas.

### Base de datos
Configuraríamos un volumen (por ejemplo, `postgres_data:/var/lib/postgresql/data`) en nuestro `docker-compose.yml`, garantizando que, si el contenedor de PostgreSQL se detiene, la información persista.

### Modelos entrenados
Mantendríamos nuestros modelos en `./models/` (o en GCS, S3, etc.). Tanto el contenedor de ML como el de FastAPI compartirían acceso a esa carpeta a través de un volumen. Así, si un contenedor se borra, el modelo persistiría y no tendríamos que reentrenarlo desde cero. Además, consideraríamos la opción de almacenar estos modelos en la nube para mayor seguridad.  