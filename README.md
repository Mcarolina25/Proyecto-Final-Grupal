
'''
PF_DS/
├── docker/
│   ├── Dockerfile.airflow       # Contenedor con instrucciones de la imagen de Airflow (el orquestador de tareas)
│   ├── Dockerfile.fastapi       # Contenedor con instrucciones de la imagen de FastAPI (para crear un microservicio)
│   ├── Dockerfile.streamlit     # Contenedor con instrucciones de la imagen de Streamlit (opcional para Dashboard)
│   └── docker-compose.yml       # Archivo con instrucciones para Orquestar los contenedores (Postgres, Airflow, etc.)
├── dags/
│   └── etl_dag.py               # DAG principal de Airflow
├── ml/
│   ├── scripts/
│   │   ├── etl.py               # Lógica de ETL
│   │   ├── functions.py         # Funciones auxiliares
│   │   └── ...
│   └── models/
│       └── model.pkl           # Modelo entrenado
├── data/
│   ├── google/
│   │   └── ...                  # Archivos JSON de metadata-sitios, reviews, etc.
│   └── yelp/
│       └── ...                  # Archivos JSON/Pickle de Yelp
├── api/
│   └── main.py                  # Código de FastAPI
├── dashboard/
│   └── app.py                   # Código de Streamlit (si lo usan)
├── requirements.txt             # Dependencias (o uno por servicio, según convenga)
└── README.md
'''