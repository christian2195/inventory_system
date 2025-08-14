# Dockerfile
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/inventory

# Instala las dependencias del sistema operativo
RUN apt-get update && apt-get install -y gcc libpq-dev

# Copia e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el proyecto del host al contenedor.
# Esto incluye la carpeta `inventory_system` y `manage.py`.
COPY . .

# Recopila los archivos estáticos de Django
RUN python manage.py collectstatic --noinput

# Comando para iniciar el servidor Gunicorn
CMD gunicorn --chdir /usr/src/inventory inventory_system.wsgi:application --bind 0.0.0.0:7999