FROM python:3.12-slim

# Instala dependencias del sistema si se requiere (por ejemplo libpq-dev para psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc

# Crea un directorio de trabajo
WORKDIR /app

# Copiamos el requirements.txt a la imagen (si lo usas para este contenedor)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiamos el contenido de la carpeta ml (opcional si deseas tener todo en la imagen)
# Pero OJO, si usas 'volumes' en docker-compose, a veces se sobrescribe
# COPY ./services/ml /app

# Comando por defecto (ejecutará un script, un server, etc.)
CMD ["python", "/app/scripts/test_etl.py"]
