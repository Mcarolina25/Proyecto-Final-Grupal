
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
