
```
PROYECTO-FINAL-GRUPAL/ (Rama_salopezna)
├── data/
│   └── ... 
├── services/                   # Carpeta para almacenar cada servicio a implementar
│   │                           
│   ├── airflow/
│   │   ├── Dockerfile          # Contenedor con instrucciones de la imagen de Airflow (el orquestador de tareas)
│   │   └── dags/               # DAG principal de Airflow, indica el orden (sin ciclos repetitivos) ejecución tareas
│   │                           # (p.ej: 1.cargar archivos JSON, 2.luego transformarlos, 3.luego insertarlos en DB).
│   ├── fastapi/
│   │   ├── Dockerfile          # Contenedor con instrucciones de la imagen de FastAPI (para crear un microservicio)
│   │   └── main.py
│   │                           
│   ├── streamlit/
│   │   ├── Dockerfile          # Contenedor con instrucciones de la imagen de Streamlit (opcional para Dashboard)
│   │   └── app.py
│   │                           
│   └── ml/
│       ├── Dockerfile
│       ├── scripts/
│       └── models/
│                           
├── docker-compose.yml          # Archivo con instrucciones para Orquestar los contenedores (Postgres, Airflow, etc.)
├── requirements.txt            # Lista de librerías de Python requeridas (por ejemplo pandas, numpy, sqlalchemy, etc.)
└── README.md


PF_DS/
├── docker/
│   ├── Dockerfile.airflow       # Contenedor con instrucciones de la imagen de Airflow (el orquestador de tareas)
│   ├── Dockerfile.fastapi       # Contenedor con instrucciones de la imagen de FastAPI (para crear un microservicio)
│   ├── Dockerfile.streamlit     # Contenedor con instrucciones de la imagen de Streamlit (opcional para Dashboard)
│   └── docker-compose.yml       # Archivo con instrucciones para Orquestar los contenedores (Postgres, Airflow, etc.)
├── dags/
│   └── etl_dag.py               # DAG principal de Airflow, indica el orden (sin ciclos repetitivos) en que se ejecutan las tareas del pipeline de datos (p.ej: 1.cargar archivos JSON, 2.luego transformarlos, 3.luego insertarlos en DB).
├── ml/
│   ├── scripts/
│   │   ├── etl.py               # Lógica de ETL
│   │   ├── functions.py         # Funciones de python usadas a lo largo del ETL y EDA
│   │   └── ...
│   └── models/
│       └── model.pkl           # Modelo entrenado con ML para predictores y/o recomendadores
├── data/
│   ├── google/
│   │   └── ...                  # Archivos crudos de Google en formato JSON
│   └── yelp/
│       └── ...                  # Archivos crudos de Yelp en formatos JSON/Pickle/parquet
├── api/
│   └── main.py                  # Código FastAPI para exponer servicio web que entregue recomendaciones y/o predicciones 
├── dashboard/
│   └── app.py                   # Código de Streamlit (opcional para Dashboar)
├── requirements.txt             # Lista de librerías de Python requeridas (por ejemplo pandas, numpy, sqlalchemy, etc.)
└── README.md
```
