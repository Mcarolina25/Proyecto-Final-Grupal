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

# 📦 Microservicio Fusion GDrive ➔ GCS

Este microservicio se encarga de sincronizar archivos desde una carpeta compartida en **Google Drive** hacia un bucket en **Google Cloud Storage (GCS)**, registrando toda la trazabilidad en **BigQuery**.

## 🚀 Funcionalidad

1. **Validación y creación** de:
   - Dataset en BigQuery (`Registro_Archivos`).
   - Tablas:
     - `archivos_en_gdrive`
     - `archivos_en_gcs`
     - `archivos_transferidos`
2. **Registro** de archivos detectados en:
   - Carpeta de **Google Drive** (`archivos_en_gdrive`).
   - Carpeta en **GCS** (`archivos_en_gcs`).
3. **Transferencia** de archivos:
   - Archivos que existen en GDrive y no en GCS son descargados y subidos al bucket GCS.
   - Se registra cada transferencia exitosa en `archivos_transferidos`.
4. **Actualización final**:
   - Se vuelve a registrar el estado actualizado de la carpeta GCS para reflejar los archivos realmente existentes.

## 🛠️ Tecnologías y Librerías

- **Google Cloud Storage** (`google-cloud-storage`)
- **Google BigQuery** (`google-cloud-bigquery`)
- **Google API Client** (`google-api-python-client`)
- **Google Authentication Libraries** (`google-auth`, `google-auth-httplib2`, `google-auth-oauthlib`)
- **Python 3.9+**
- **Flask** (opcional para servir en Cloud Run)

## 📄 Variables principales

| Variable         | Descripción                                               |
|------------------|------------------------------------------------------------|
| `PROJECT_ID`      | ID del proyecto en Google Cloud                           |
| `DATASET_ID`      | Dataset en BigQuery para registros                         |
| `TABLE_GDRIVE`    | Tabla que registra archivos encontrados en GDrive          |
| `TABLE_GCS`       | Tabla que registra archivos encontrados en GCS             |
| `TABLE_TRANSFERIDOS` | Tabla que registra archivos transferidos exitosamente  |
| `BUCKET_NAME`     | Nombre del bucket de destino en GCS                        |
| `DESTINATION_FOLDER` | Carpeta destino dentro del bucket en GCS               |
| `FOLDER_ID`       | ID de la carpeta compartida en Google Drive                |

## 📝 Flujo de ejecución (`carga_incremental`)

```plaintext
1. Verifica y crea Dataset y Tablas en BigQuery si no existen.
2. Escanea Google Drive y registra archivos nuevos.
3. Escanea GCS y registra archivos nuevos.
4. Compara archivos de GDrive vs. GCS.
5. Transfiere solo los archivos faltantes.
6. Registra transferencias realizadas.
7. Vuelve a registrar el estado actualizado de GCS.
8. Devuelve respuesta de éxito o error.
```

## 🗂️ Estructura de las Tablas

### `archivos_en_gdrive`
- `gdrive_id` (STRING, REQUIRED)
- `file_name` (STRING)
- `mime_type` (STRING)
- `created_time` (TIMESTAMP)
- `web_view_link` (STRING)

### `archivos_en_gcs`
- `file_name` (STRING, REQUIRED)
- `fecha_creacion` (TIMESTAMP)
- `size_bytes` (INTEGER)
- `mime_type` (STRING)
- `gcs_path` (STRING)

### `archivos_transferidos`
- `file_name` (STRING, REQUIRED)
- `gdrive_id` (STRING, REQUIRED)
- `transfer_time` (TIMESTAMP)
- `gcs_path` (STRING)

## 📋 Instalación de dependencias (requirements.txt)

```plaintext
google-cloud-storage
google-cloud-bigquery
google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib
flask
```

## 📦 Despliegue implementado

Se ha desplegado como servicio en **Cloud Run**, para este caso no se han configurado variables de entorno y los permisos de acceso a los servicios de **Drive**, **GCS**, y **BigQuery** se han proporcionado directamete a través de credenciales en formato .json.

## 📢 Notas importantes

- El microservicio se puede ejecutar múltiples veces y no creara duplicados.
- Ignora carpetas o archivos no descargables (e.g., carpetas o documentos de Google).
- El sistema maneja errores comunes como permisos 403 (`fileNotDownloadable`) sin detener el flujo.

---
