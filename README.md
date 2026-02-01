# 🏦 Banca Online - FastAPI + PostgreSQL + Kubernetes
## 📋 Descripción
Este proyecto nace como una **guía práctica** para aprender cómo llevar una **aplicación Python** desde **local**, pasando por su **containerización con Docker**, hasta **producción en Kubernetes**, siguiendo buenas prácticas reales del ámbito profesional.

La aplicación simula **una banca online** desarrollada con **FastAPI y PostgreSQL**, pero el foco principal no es el diseño de la aplicación, sino **todo el ciclo de vida**: despliegue, automatización, operación, escalabilidad y alta disponibilidad.

Incluye de forma progresiva:
- 🧪 Ejecución local con entorno virtual y variables de entorno ✅
- 🐳 Containerización con Docker y buenas prácticas de empaquetado 🚧
- ☸️ Orquestación en Kubernetes (Deployments, Services y health checks) 🚧
- 📦 Preparación para Helm Charts, con despliegues reutilizables y configurables 🚧
- 🔄 Enfoque GitOps con ArgoCD para despliegues declarativos 🚧
- 🔍 Base sólida de logging y observabilidad, pensada para Istio, Loki y Grafana 🚧
## 📥 Clonar el repositorio
```
git clone https://github.com/MarioSFdez/python-app-docker-to-k8s.git
cd python-app-docker-to-k8s
```  
## 🚀 Despliegue Local
### Requisitos
- Python 3.11+
- PostgreSQL
- Docker (opcional)

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

# Crear tabla users
 CREATE TABLE users (
      id INT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
      username VARCHAR(25) NOT NULL UNIQUE,
      password_hashed VARCHAR(255) NOT NULL
 );
```
#### Desplegar Postgresql Docker (opcional)
```
# Levantar el contenedor
cd python-app/docker-postgresql
docker-compose up -d
```
#### Ejecutar aplicación python local
```
# Crear entorno virtual
python3 -m venv .myvenv
source .myvenv/bin/activate

# Instalar dependencias
pip install -r python-app/requirements.txt

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
<div align="center">

### 🚧 PRÓXIMAMENTE 🚧  
👷‍♂️ En construcción — vuelve pronto

</div>

## ☸️ Despliegue en Kubernetes
<div align="center">

### 🚧 PRÓXIMAMENTE 🚧  
👷‍♂️ En construcción — vuelve pronto

</div>
