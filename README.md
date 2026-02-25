# 🏦 Banca Online - FastAPI + PostgreSQL + Kubernetes
## 📋 Descripción
Este proyecto nace como una **guía práctica** para aprender cómo llevar una **aplicación Python** desde **local**, pasando por su **containerización con Docker**, hasta **producción en Kubernetes**, siguiendo buenas prácticas reales del ámbito profesional.

La aplicación simula **una banca online** desarrollada con **FastAPI y PostgreSQL**, pero el foco principal no es el diseño de la aplicación, sino **todo el ciclo de vida**: despliegue, automatización, operación, escalabilidad y alta disponibilidad.

Incluye de forma progresiva:
- 🧪 **Ejecución local** con entorno virtual y variables de entorno ✅
- 🐳 **Containerización con Docker** y buenas prácticas de empaquetado ✅
- ☸️ **Orquestación en Kubernetes** (Deployments, Services y health checks) 🚧
- 📦 **Helm Charts**, con despliegues reutilizables y configurables 🚧
- 🔄 **GitOps con ArgoCD** para despliegues declarativos 🚧
- 🔍 **Logging y observabilidad**, pensada para Istio, Loki y Grafana 🚧

## 🖼️ Vista Previa de la Aplicación
### Página de Login y Registro
La interfaz de autenticación permite tanto el acceso de usuarios existentes como el registro de nuevos usuarios.
<div align="center">
<img width="700" alt="image" src="https://github.com/user-attachments/assets/2cc7787f-83e9-455c-82a4-23e177a7bfa7" />
</div>

### Dashboard de Usuario
Una vez autenticado, el usuario accede a un dashboard con las funcionalidades principales de la banca online.
<div align="center">
<img width="700" alt="Captura de pantalla 2026-02-02 203721" src="https://github.com/user-attachments/assets/6d01237d-c97a-4449-9773-00e5535ef671" />
</div>

## 📥 Clonar el repositorio
```
git clone https://github.com/MarioSFdez/python-app-docker-to-k8s.git
cd python-app-docker-to-k8s
```
  
## 🚀 Despliegue Local
### Requisitos
- Python 3.11+
- PostgreSQL
- Docker

### Instalación
#### Instalar PostgreSQL
```
sudo apt update
sudo apt install postgresql 
sudo -u postgres psql

# Crear usuario y darle todos los permisos en la bbdd
CREATE USER <your-username> WITH PASSWORD '<your-password>';
CREATE DATABASE <your-database> OWNER <your-username>;
GRANT ALL PRIVILEGES ON DATABASE <your-database> TO <your-username>;

# Accede con el usuario creado
psql -U <your-username> -d <your-database> -h localhost

# Crear tabla users
CREATE TABLE users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(25) NOT NULL UNIQUE,
    password_hashed VARCHAR(255) NOT NULL
);
```
#### Ejecutar la Aplicación Python en Local
```
# Crear entorno virtual
cd python-app
python3 -m venv .myvenv
source .myvenv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export POSTGRES_USER='<your-username>'
export POSTGRES_PASSWORD='<your-password>'
export POSTGRES_DB='<your-database>'
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# Ejecutar app
gunicorn app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
## 🐳 Despliegue con Docker
### Requisitos
- Docker y Docker Compose
- Cuenta en Docker Hub (solo para modo producción con imagen remota)
### Configuración inicial
Modifica el `archivo env/.env.docker` con las siguientes variables:
```
POSTGRES_USER='<your-username>'
POSTGRES_PASSWORD='<your-password>'
POSTGRES_DB='<your-database>'
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```
---
### Opción 1: Desarrollo Local (Build en local)
Construye la imagen directamente en tu máquina y despliega con Docker Compose:
#### docker-compose.local.yml
```
  banca-online:
    image: banca-online:local
    build:
      context: ..
```
#### Despliegue de los servicios
```
cd compose

# Construir y levantar servicios
docker-compose --env-file ../env/.env.docker -f docker-compose.local.yml up --build -d
```
**Accede a la aplicación:** http://localhost:8000
### Opción 2: Producción (Imagen desde Docker Hub)
Usa una imagen ya construida y publicada en Docker Hub.
#### 1. Build y Push a Docker Hub
```
# Login en Docker Hub
docker login

# Construir imagen con tag
docker build -t <user-docker-hub>/banca-online:1.0.0 .

# Subir al registro
docker push <user-docker-hub>/banca-online:1.0.0
```
#### 2. Configurar docker-compose.prod.yml
Modifica el archivo `compose/docker-compose.prod.yml`:
```
  banca-online:
    image: <user-docker-hub>/banca-online:1.0.0   
```
**Usar mi imagen pública (opcional):**
```
    image: mariosfdez/banca-online:1.0.0
```
#### 3. Desplegar
```
cd compose

# Descargar imagen y levantar servicios
docker-compose --env-file ../env/.env.docker -f docker-compose.prod.yml up -d
```
---
### Verificación
```
# Healthcheck de la aplicación
curl http://localhost:8000/health

# Respuesta esperada:
# {"status":"healthy","database":"connected"}
```

## ☸️ Despliegue en Kubernetes
<div align="center">

### 🚧 PRÓXIMAMENTE 🚧  
👷‍♂️ En construcción — vuelve pronto

</div>
