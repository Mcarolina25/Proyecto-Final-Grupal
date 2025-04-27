# 💻 Organización de la Información en el Repositorio 🤖

```
PROYECTO-FINAL-GRUPAL/
├── 
└── README.md

PowerBI estará en Local conectado a la DB PostgreSQL y API del Recomendador.
```

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

# Microservicios de Registro de Archivos

Este repositorio contiene dos microservicios independientes desarrollados en **Python 3.9** para ejecutarse en **Cloud Run**, encargados de registrar archivos encontrados en:

- **Google Cloud Storage (GCS)**
- **Google Drive (Carpeta Compartida)**

Cada microservicio registra los archivos encontrados en un **dataset centralizado en BigQuery** (`Registro_Archivos`), en distintas tablas.

---

# Orquestación - Automatización

## Microservicio 1: `registro-archivos-gcs`

### Descripción

Escanea un bucket de **Google Cloud Storage** bajo un prefijo específico (`Google/`) y registra en BigQuery los archivos nuevos que no hayan sido previamente registrados.

### Tabla de destino

- **Dataset**: `Registro_Archivos`
- **Tabla**: `archivos_en_gcs`

### Estructura de la tabla

| Campo            | Tipo     | Descripción                         |
|------------------|----------|-------------------------------------|
| file_name        | STRING   | Nombre del archivo                  |
| fecha_creacion   | TIMESTAMP| Fecha de creación del archivo       |
| size_bytes       | INTEGER  | Tamaño en bytes                     |
| mime_type        | STRING   | Tipo MIME del archivo               |
| gcs_path         | STRING   | Ruta completa en GCS                |

### Variables importantes

- **PROJECT_ID**: ID del proyecto GCP
- **DATASET_ID**: `Registro_Archivos`
- **TABLE_GCS**: `archivos_en_gcs`
- **BUCKET_NAME**: Nombre del bucket en GCS
- **FOLDER_PREFIX**: Prefijo para buscar archivos (`Google/`)

### Flujo de ejecución

1. Verifica/crea el dataset y la tabla.
2. Lista archivos bajo el prefijo definido.
3. Verifica si ya están registrados.
4. Registra los nuevos en batch de forma concurrente (**async**).

### Requirements.txt

```text
Flask==2.2.5
functions-framework
google-cloud-storage
google-cloud-bigquery
```

### Notas

- No requiere Docker.
- Usa autenticación mediante **Service Account** ya configurada en Cloud Run.

---

## Microservicio 2: `registro-archivos-gdrive`

### Descripción

Escanea una **carpeta compartida en Google Drive** y registra en BigQuery los archivos nuevos detectados, evitando duplicados.

### Tabla de destino

- **Dataset**: `Registro_Archivos`
- **Tabla**: `archivos_en_gdrive`

### Estructura de la tabla

| Campo            | Tipo     | Descripción                         |
|------------------|----------|-------------------------------------|
| file_name        | STRING   | Nombre del archivo                  |
| fecha_creacion   | TIMESTAMP| Fecha de creación del archivo       |
| size_bytes       | INTEGER  | Tamaño en bytes                     |
| mime_type        | STRING   | Tipo MIME del archivo               |
| drive_file_id    | STRING   | ID del archivo en Google Drive      |
| drive_web_link   | STRING   | URL de acceso al archivo            |

### Variables importantes

- **PROJECT_ID**: ID del proyecto GCP
- **DATASET_ID**: `Registro_Archivos`
- **TABLE_DRIVE**: `archivos_en_gdrive`
- **FOLDER_ID**: `111qqmbe37wCIFNKCAjmI7Jk6aZ-Q6QM7`

### Flujo de ejecución

1. Verifica/crea el dataset y la tabla.
2. Se conecta al API de Google Drive.
3. Lista los archivos de la carpeta compartida.
4. Verifica duplicados en BigQuery.
5. Registra los archivos nuevos.

### Requirements.txt

```text
Flask==2.2.5
functions-framework
google-cloud-bigquery
google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib
```

### Notas

- No requiere Docker.
- Usa autenticación de **Service Account** para Google Drive API.
- La carpeta compartida debe tener permisos para `python-service-account@acme-987654.iam.gserviceaccount.com`.

---

# Buenas Prácticas Seguidas

- Código modularizado y limpio.
- Manejo de errores robusto.
- Uso de clientes oficiales de Google Cloud.
- Implementación eficiente (Concurrente para GCS).
- Compatible con despliegue automático en Cloud Run.

# Próximos Pasos (en pruebas)

- Implementar métricas y trazabilidad en BigQuery/Looker Studio.
- Agregar Pub/Sub triggers para escaneo periódico automático.
- Optimizar paralelismo dinámico según cantidad de archivos.

---

