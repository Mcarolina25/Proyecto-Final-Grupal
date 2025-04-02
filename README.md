# 💻 Organización de la Información en el Repositorio 🤖

PROYECTO-FINAL-GRUPAL/
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

PowerBI estará en Local conectado a la DB PostgreSQL y API del Recomendador.

# 1. Visión general de la Arquitectura propuesta

### Almacenamiento de datos crudos (Data Lake - Google Cloud Stora)
<p align="justify">

</p>

### Base de datos relacional (mySQL - Google Cloud SQL)
<p align="justify">

</p>

### Orquestador Apache Airflow (Google Cloud Composer - AirFlow)
<p align="justify">

</p>

### Recomendador de restaurantes (Google CLoud Vertex AI)
<p align="justify">

</p>

### API (FastAPI - Vertex AI)
<p align="justify">

</p>

### Dashboard (PowerBI en conexion con API y CloudSQL)
<p align="justify">

</p>
 
- **Power BI** (externo en local) se enlaza directamente con la DB y/o con un endpoint de FastAPI para refrescar datos y mostrar todo lo visual.

> **Clave**: Todos los contenedores que requieran datos se conectarían a la **DB PostgreSQL** alojada en uno de los contenedores desde donde igualmente extraemos la data de interes almacendad en **GCP**. Tanto la base de datos como los datos crudos y los modelos se manejarían con volúmenes persistentes (o servicios de almacenamiento en la nube), de modo que no los perderíamos si un contenedor se elimina o reinicia.

---

# 2. Flujo de datos resumido

### Ingesta
<p align="justify">
Recibiríamos archivos JSON/CSV/PKL/Parquet de Google y Yelp (Data Lake del CLiente), ubicándolos en Google Cloud Storage (GCP). Cloud Composer con Apache Airflow se encargaría de orquestar y automatizar el flujo de tareas los scripts de ETL, reentrenamiento de modelos de ML y actualización de Base de datos mySQL en CloudSQL.
</p>

### Transformación
<p align="justify">
Realizaríamos la limpieza, validación y normalización de los datos. Después, actualizaríamos CloudSQL. Opcionalmente, crearíamos tablas analíticas o un data warehouse adicional para consultas más especializadas.
</p>

### Entrenamiento
<p align="justify">
Lanzaríamos un DAG de Airflow que entrenaría o reentrenaría nuestros modelos. Leeríamos los datos de CloudSQL y guardaríamos el modelo final en un volumen en GCS por seguridad.
</p>

### Consumo
<p align="justify">
Con FastAPI hariamos las consultas al modelo entrenado para generar recomendaciones de restaurantes y las visulaizariamos sobre el Dashboard en PowerBI.
</p>

### Reentrenamiento continuo
<p align="justify">
Periódicamente bajo eventos de nuevos archivos depositados en Cloud Storage, programaríamos en Airflow la re-ejecución del DAG para incorporar nuevos datos y reentrenar el modelo.
</p>

---

# 3. Almacenamiento de datos procesados y persistencia

### Data cruda (local y nube)
<p align="justify">

</p>

### Base de datos
<p align="justify">

</p>

### Modelos entrenados
<p align="justify">

</p>

# 🧠 Distribución de Tareas y Configuración del Proyecto 🤓
<p align="justify">

</p>
---

## 1. ETL y Preprocesamiento de Datos  
**Responsable:** **Delia y Alejandro**  

**Tareas clave:**
- **Desarrollo en Notebooks:**
  - Crear y probar scripts en notebooks para la carga, limpieza y transformación de archivos (JSON, CSV, pkl, parquetetc.) provenientes de Google y Yelp.
  - Validar el proceso de ingesta de datos en un entorno local (sin contenedores) para asegurar que la lógica ETL funcione correctamente.
- **Gestión del Data Lake Local:**
  - Definir la organización y versionado de los datos en la carpeta `./data` y planificar la sincronización con el bucket en GCS (si es necesario).
  - Proporcionar la estructura de datos depurada al equipo desarrollador para la implementacion de cada servicio.
  - Integrar al README principal toda la documentación de esta fase.

## 2. Desarrollo de Modelos de Machine Learning  
**Responsable:** **Ariel**  

**Tareas clave:**
- **Desarrollo en Notebooks:**
  - Desarrollar y validar los scripts de preprocesamiento, entrenamiento y validación de modelos de ML.
  - Generar y probar la persistencia del modelo (por ejemplo, generar el archivo ``).
- **Documentación y Pruebas:**
  - Documentar el proceso de entrenamiento y validación, estableciendo los pasos para la integración en el entorno de producción.
  - Integrar al README principal toda la documentación de esta fase.

## 3. Desarrollo de la API con FastAPI  
**Responsable:** **Delia y Alejandro**  

**Tareas clave:**
- **Desarrollo en Notebooks y Scripts:**
  - Diseñar y probar los endpoints de FastAPI para exponer funciones de predicción o recomendaciones.
  - Realizar pruebas de conexión a la base de datos y de carga del modelo entrenado.
  - Integrar al README principal toda la documentación de esta fase.
- **Preparación para despliegue sobre GCP:**
  - Proveer el código final en un formato fácilmente integrable, para que el responsable de la orquestacion y automatización lo implemente con Cloud Composer.

## 4. Desarrollo de Visualizaciones y Dashboards con Streamlit y/o PowerBI 
**Responsable:** **Carolina**  

**Tareas clave:**
- **Desarrollo en Dashboard:**
  - Crear dashboards interactivos y visualizaciones de datos utilizando Streamlit o PowerBI en un entorno local.
  - Conectar y probar el acceso a los datos (directamente o vía la API) para mostrar KPIs y métricas relevantes.
- **Preparación para despliegue sobre GCP:**
  - Organizar el código e implementación final para que pueda ser fácilmente integrado y conectado con GCP.
  - Integrar al README principal toda la documentación de esta fase.

## 5. Integración en GCP y Orquestación con Cloud Composer-Airflow  
**Responsable:** **Sergio**  

**Tareas clave:**
- **Unificación y Dockerización:**
  - Encapsular los notebooks y módulos desarrollados por el equipo en los lenguages como python y SQL segun herramienta de GCP utilizada (para Airflow, FastAPI y ML).
  - Crear y mantener el archivo `docker-compose.yml` para orquestar los distintos servicios.
- **Orquestación con Airflow:**
  - Diseñar y configurar el entorno de Airflow, definiendo los DAGs que orquesten la ejecución de las tareas (ingesta, transformación, entrenamiento, reentrenamiento).
  - Asegurar la integración correcta entre Airflow y los demás servicios a través de las herramientas de implementación de GCP.
  - Integrar al README principal toda la documentación de esta fase.

## Coordinación y Flujo de Trabajo Global

- **Integración de Scripts y microservicios sobre GCP:**
  - Cada integrante desarrollará y validará sus respectivas partes en notebooks preliminarmente.
  - Una vez que el código esté probado, se centralizará en el repositorio y se entregará a el responsable de la orquestación y automatización.

- **Orquestación y Automatización:**
  - Sergio se encargará de orquestar la ejecución de las tareas (ingesta, transformación, entrenamiento y actualización) mediante Airflow, configurando los DAGs y asegurando la comunicación entre los contenedores.
  
- **Reuniones de Coordinación:**
  - Se programarán reuniones semanales para revisar avances, aclarar dudas y coordinar la integración de los módulos desarrollados en notebooks al entorno GCP.
  - Se mantendrá actualizada la documentación y el README, detallando tanto la lógica de negocio en notebooks como el proceso de implementación sobre GCP y despliegue.

---

