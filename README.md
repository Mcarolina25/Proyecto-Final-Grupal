# 💻 Organización de la Información en el Repositorio 🤖
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

# 1. Visión general de la Arquitectura propuesta

### Almacenamiento de datos crudos (Data Lake)
<p align="justify">
En nuestro proyecto, almacenaríamos los archivos JSON/CSV/PKL/Parquet provenientes de Google y Yelp en un repositorio externo a los contenedores. De esta forma, evitaríamos inflar las imágenes de Docker y depender de contenedores para el resguardo de la data. Haríamos una implemetación misxta del DataLake a traves de recrear una parte en la Nube y otra en Local.  
- **En la nube (Google Cloud Services - GCS)**: Utilizaríamos un bucket como nuestro **Data Lake** para alojar parte de la data de Google (archivos JSON en la carpeta `metadata-google`). Así, recrearíamos un entorno real en la nube y simularíamos la llegada y actualización periódica de sitios registrados en Google Maps.  
- **Entorno local**: Por temas de peso y practicidad, seguiríamos manejando el resto de la data en una carpeta montada como volumen Docker (`./data`).  
- Además, consideraríamos almacenar en la nube los modelos de ML entrenados, allí igualmente mantendríamos una copia de seguridad para evitar perderlos en caso de que los contenedores se caigan.
</p>

### Base de datos relacional (PostgreSQL - Gestor DBaver)
<p align="justify">
Para la arquitectura de la Base de Datos, emplearíamos PostgreSQL para guardar la información **estructurada** y depurada (p. ej., tablas para el entrenamiento de los modelos de ML, reviews normalizadas y unificadas, métricas agregadas para alimentar los Dashboards, etc). Configuraríamos un **volumen persistente** en local y podría ser otroen la Nube para que la base de datos no se pierda si el contenedor se cae.
</p>

### Contenedor de Airflow
<p align="justify">
Airflow sería nuestro orquestador de tareas para hacer el ETL y ML entre otras.  
- Nuestros DAGs ((Directed Acyclic Graphs) o flujos de trabajo se encargarían de:  
  1. **Extraer** datos del Data Lake ubicado en GCS y de la carpeta local cruda.  
  2. **Transformarlos** y **cargarlos** en la base de datos PostgreSQL.  
  3. **Entrenar** y **reentrenar** los modelos de ML de los recomendadores y predictores.  
- A traves de los DAGs de Airflow programaríamos reentrenamientos periódicos, limpiezas de datos y cualquier otro flujo de trabajo que vayamos a automatizar.
</p>

### Contenedor de ML
<p align="justify">
En este contenedor concentraríamos los scripts de preprocesamiento, entrenamiento y validación de modelos.  
- Utilizaríamos la **misma base de datos** (PostgreSQL) para leer la información y, si lo necesitáramos, consultaríamos el Data Lake en GCS o la carpeta local.  
- Al final, generaríamos un **modelo entrenado** (por ejemplo, `model.pkl`) y lo almacenaríamos en una carpeta montada localmente o, de ser necesario, en la nube para no perderlo en caso de reinicio del contenedor.
</p>

### Contenedr de FastAPI
<p align="justify">
FastAPI expondría endpoints de **predicción** o **recomendaciones**.  
- Cargaría el modelo entrenado desde el volumen persistente (o desde GCS) al arrancar.  
- Se conectaría a la base de datos para obtener datos adicionales cuando fuera necesario (por ejemplo, información de los establecimientos).
</p>

### Contenedor de Streamlit
<p align="justify">
Para la parte de visualización y dashboards:  
- **Streamlit** (contenedor) se conectaría a la base de datos o a los endpoints de FastAPI para mostrar KPIs, gráficas y análisis interactivos.  
- **Power BI** (externo) podría enlazarse directamente con nuestra DB o con un endpoint de FastAPI para refrescar datos y presentar informes.
</p>



> **Clave**: Todos los contenedores que requieran datos se conectarían a la **DB** o al Data Lake/carpeta local o Nube donde los guardaríamos. Tanto la base de datos como los datos crudos y los modelos se manejarían con volúmenes persistentes (o servicios de almacenamiento en la nube), de modo que no los perderíamos si un contenedor se elimina.

---

# 2. Flujo de datos resumido

### Ingesta
<p align="justify">
Recibiríamos archivos JSON/CSV/PKL/Parquet de Google y Yelp (Data Lake del CLiente), ubicándolos en `./data` (para la parte local) o en nuestro bucket GCS (para el Data Lake de Google). Airflow se encargaría de detectar o programar la ingesta y, a través de los scripts de ETL, insertaríamos la información en la base de datos.
</p>

### Transformación
<p align="justify">
Realizaríamos la limpieza, validación y normalización de los datos. Después, actualizaríamos PostgreSQL. Opcionalmente, crearíamos tablas analíticas o un warehouse adicional para consultas más especializadas.
</p>

### Entrenamiento
<p align="justify">
Lanzaríamos un DAG de Airflow que entrenaría o reentrenaría nuestros modelos (en el contenedor ML o con PythonOperators). Leeríamos los datos de PostgreSQL (o directamente de la carpeta/bucket crudo) y guardaríamos el modelo final en un volumen, como `./models`, o en GCS para mayor seguridad.
</p>

### Consumo
<p align="justify">
FastAPI cargaría el modelo entrenado en memoria al iniciarse (o cuando recibiera la primera solicitud). Streamlit, Power BI u otras herramientas consultarían FastAPI para obtener predicciones y visualizaciones, o bien accederían directamente a la base de datos y al modelo.
</p>

### Reentrenamiento continuo
<p align="justify">
Periódicamente, programaríamos en Airflow la re-ejecución del DAG para incorporar nuevos datos y reentrenar el modelo. Si FastAPI utilizara el modelo en memoria, podríamos reiniciar el contenedor para que cargue la versión más reciente.
</p>

---

# 3. Almacenamiento de datos procesados y persistencia

### Data cruda (local y nube)
<p align="justify">
Montaríamos `./data` como un volumen en Docker para parte de la data, y utilizaríamos GCS como Data Lake para la porción correspondiente a Google (simulando un escenario real de llegada y actualización de datos). Evitaríamos incluir decenas de GB dentro de nuestras imágenes de Docker para no inflarlas.
</p>

### Base de datos
<p align="justify">
Configuraríamos un volumen espejo de la data procesada entre lo local y el contenedor de PostgreSQL, garantizando que, si el contenedor de PostgreSQL se detiene, la información persista en local y viceversa. Además, podríamos utilizar igualmente el almacenamiento en la nube como respaldo para mayor seguridad.
</p>

### Modelos entrenados
<p align="justify">
Mantendríamos nuestros modelos en `./models` (o en GCS). Tanto el contenedor de ML como el de FastAPI compartirían acceso a esa carpeta a través de un volumen. Así, si un contenedor se borra, el modelo persistiría y no tendríamos que reentrenarlo desde cero. Además, consideraríamos la opción de almacenar estos modelos en la nube para mayor seguridad.  
</p>

# 🧠 Distribución de Tareas y Configuración del Proyecto 🤓
<p align="justify">
Esta propuesta de distribución de tareas se enfoca en que la mayoría del equipo trabaje en notebooks (ipynb) para el desarrollo de scripts y pruebas, mientras que un integrante se encarga de la integración en contenedores y la orquestación con Airflow.
</p>
---

## 1. ETL y Preprocesamiento de Datos  
**Responsable:** **Integrante 1**  

**Tareas clave:**
- **Desarrollo en Notebooks:**
  - Crear y probar scripts en notebooks para la carga, limpieza y transformación de archivos (JSON, CSV, pkl, parquetetc.) provenientes de Google y Yelp.
  - Validar el proceso de ingesta de datos en un entorno local (sin contenedores) para asegurar que la lógica ETL funcione correctamente.
- **Gestión del Data Lake Local:**
  - Definir la organización y versionado de los datos en la carpeta `./data` y planificar la sincronización con el bucket en GCS (si es necesario).
  - Proporcionar la estructura de datos depurada a l@s compañer@s para el desarrollo de los modelos de ML y parte de la data para el Dashboards.
  - Integrar al README principal toda la documentación de esta fase.

---

## 2. Desarrollo de Modelos de Machine Learning  
**Responsable:** **Integrante 3**  

**Tareas clave:**
- **Desarrollo en Notebooks:**
  - Desarrollar y validar los scripts de preprocesamiento, entrenamiento y validación de modelos de ML.
  - Generar y probar la persistencia del modelo (por ejemplo, generar el archivo `model.pkl`).
- **Documentación y Pruebas:**
  - Documentar el proceso de entrenamiento y validación, estableciendo los pasos para la integración en el entorno de producción.
  - Integrar al README principal toda la documentación de esta fase.

---

## 3. Desarrollo de la API con FastAPI  
**Responsable:** **Integrante 4**  

**Tareas clave:**
- **Desarrollo en Notebooks y Scripts:**
  - Diseñar y probar los endpoints de FastAPI para exponer funciones de predicción o recomendaciones.
  - Realizar pruebas de conexión a la base de datos y de carga del modelo entrenado.
  - Integrar al README principal toda la documentación de esta fase.
- **Preparación para Contenerización:**
  - Proveer el código final en un formato fácilmente integrable, para que el responsable de contenedores (Integrante 2) lo incluya en un Dockerfile.

---

## 4. Desarrollo de Visualizaciones y Dashboards con Streamlit y/o PowerBI 
**Responsable:** **Integrante 5**  

**Tareas clave:**
- **Desarrollo en Dashboard:**
  - Crear dashboards interactivos y visualizaciones de datos utilizando Streamlit o PowerBI en un entorno local.
  - Conectar y probar el acceso a los datos (directamente o vía la API) para mostrar KPIs y métricas relevantes.
- **Preparación para Contenerización:**
  - Organizar el código e implementación final para que pueda ser fácilmente integrado y conectdo con los contenedores y DB del proyecto.
  - Integrar al README principal toda la documentación de esta fase.

---

## 5. Integración en Contenedores y Orquestación con Airflow  
**Responsable:** **Integrante 5 (Especialista en Contenedores y Airflow)**  

**Tareas clave:**
- **Unificación y Dockerización:**
  - Encapsular los notebooks y módulos desarrollados por el equipo en contenedores Docker (para Airflow, FastAPI y Streamlit).
  - Crear y mantener el archivo `docker-compose.yml` para orquestar los distintos servicios.
- **Orquestación con Airflow:**
  - Diseñar y configurar el entorno de Airflow, definiendo los DAGs que orquesten la ejecución de las tareas (ingesta, transformación, entrenamiento, reentrenamiento).
  - Asegurar la integración correcta entre Airflow y los demás servicios a través de los contenedores.
  - Integrar al README principal toda la documentación de esta fase.

---

## Coordinación y Flujo de Trabajo Global

- **Integración de Notebooks y Contenedores:**
  - Cada integrante desarrollará y validará sus respectivas partes en notebooks.
  - Una vez que el código esté probado, se centralizará en el repositorio y se entregará a Integrante 2 para la creación de los contenedores.

- **Orquestación y Automatización:**
  - El Integrante 2 se encargará de orquestar la ejecución de las tareas (ingesta, transformación, entrenamiento y actualización) mediante Airflow, configurando los DAGs y asegurando la comunicación entre los contenedores.
  
- **Reuniones de Coordinación:**
  - Se programarán reuniones semanales para revisar avances, aclarar dudas y coordinar la integración de los módulos desarrollados en notebooks al entorno contenerizado.
  - Se mantendrá actualizada la documentación y el README, detallando tanto la lógica de negocio en notebooks como el proceso de contenedorización y despliegue.

---

