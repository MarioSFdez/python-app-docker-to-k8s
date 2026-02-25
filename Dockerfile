# Utiliza una imagen libera basada en Debian
FROM python:3.12-slim

# Evita creación archivos .pyc y asegura que los logs se emitan en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crea un usuario no privilegiado por seguridad
RUN useradd --create-home --uid 10001 --shell /bin/bash appuser

# Instala dependencias del sistema necesarias (libpq5 para PostgreSQL y Curl para Healthcheck)
# Limpia el caché de apt para reducir tamaño de la imagen
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
     libpq5 \
     curl \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requirements en el contenedor
COPY python-app/requirements.txt .

# Instala las librerias de Python sin guardar archivos temporales de pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia el codigo fuente y cambia los permisos al usuario no-root
COPY --chown=appuser:appuser python-app/ .

# Cambia al usuario con permisos limitados
USER appuser

# Documenta que la aplicación escucha en el puerto 8000 
EXPOSE 8000

# Ejecuta la aplicación usando Gunicorn con workers de Uvicorn para FastAPI
CMD ["gunicorn", "app:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]