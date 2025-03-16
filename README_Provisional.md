

PF_DS/
├── docker/
│   ├── Dockerfile.airflow       # Para la imagen de Airflow
│   ├── Dockerfile.fastapi       # Para la imagen de FastAPI (opcional si vas a crear un microservicio)
│   ├── Dockerfile.streamlit     # Para la imagen de Streamlit (si vas a usarlo)
│   └── docker-compose.yml       # Orquesta todos los contenedores (Postgres, Airflow, etc.)
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
