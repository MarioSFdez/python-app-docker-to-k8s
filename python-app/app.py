# ./python-app/app.py
import os
import sys
import logging
import time
from typing import Callable
import bcrypt
import psycopg
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager

# ============ CONFIGURACIÓN DE LOGGING ============
# Configurar el nivel del log desde variable de entorno
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Formato estructurado para facilitar la división de datos en Loki
log_format = (
    '%(asctime)s | %(levelname)-8s | %(name)s | '
    '%(funcName)s:%(lineno)d | %(message)s'
)

# Configurar logging básico
logging.basicConfig(
    level=LOG_LEVEL,
    format=log_format,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Crear el logger especifico para la aplicación
logger = logging.getLogger('python-app')

# Silenciar logs muy verbosos de librerías externas
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
logging.getLogger('uvicorn.error').setLevel(logging.INFO)

# ============ VARIABLES DE ENTORNO ================
# Obtener variables de entorno
POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB=os.getenv('POSTGRES_DB')
POSTGRES_HOST=os.getenv('POSTGRES_HOST')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:"
    f"{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

# ============ LIFESPAN ================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando la aplicación...")
    logger.info(f"Conectando a la base de datos: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

    try:
        pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=5,
            timeout=30,
            open=False
        )

        await pool.open()
        app.state.pool = pool
        logger.info("Pool de conexiones a BD iniciado correctamente")
    
    except Exception as e:
        logger.critical(f"Error critico al conectar con la BD: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Cerrando aplicación...")
    await pool.close()
    logger.info("Pool de conexiones cerrado correctamente")

# ============ APLICACIÓN FASTAPI ============
app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ============ MIDDLEWARE DE LOGGING ============
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    # Middleware para loguear todas las peticiones HTTP
    start_time = time.time()

    # Información de la petición
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path

    logger.info(
        f"REQUEST | {method} {path} | IP: {client_ip}"
        f"User-Agent: {request.headers.get('user-agent', 'unknown')[:50]}"
    )

    # Procesar la petición
    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Log segun el código de respuesta
        log_level = logging.INFO
        if response.status_code >= 400:
            log_level = logging.WARNING
        if response.status_code >= 500:
            log_level = logging.ERROR

        logger.log(
            log_level,
            f"RESPONSE | {method} {path} | Status: {response.status_code} | "
            f"Duration: {duration:.3f}s | IP: {client_ip}"
        )

        return response
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"EXCEPTION | {method} {path} | Duration: {duration:.3f}s | "
            f"IP: {client_ip} | Error: {str(e)}",
            exc_info=True
        )
        raise

# ============ FUNCIONES DE UTILIDAD ============
# Funcion para hashear la contraseña
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Funcion para verificar la contraseña
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# ============ RUTAS ============
# Ruta principal
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    logger.debug("Sirviendo página principal")
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para el login
@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...)
):
    # Endpoint de login de usuarios
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Intento de login | Usuario: {username} | IP: {client_ip}")

    try:
        async with request.app.state.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT username, password_hashed FROM users WHERE username = %s", 
                    (username,)
                )
                user = await cur.fetchone()

        # El usuario existe y la contraseña es correcta
        if user and verify_password(password, user[1]):
            logger.info(f"Login exitoso | Usuario: {username} | IP: {client_ip}")
            return templates.TemplateResponse(
                "welcome.html", {
                "request": request, 
                "username": username, 
                "message": "¡Bienvenido de nuevo"
                }
            )
        
        # Si falla el login, muestra un error
        logger.warning(f"Login fallido | Usuario: {username} | IP: {client_ip} | Razón: Credenciales inválidas")
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "login_error": "Usuario o contraseña incorrectos", 
                "register_error": None
            }
        )
    
    except Exception as e:
        logger.error(
            f"Error en login | Usuario: {username} | IP: {client_ip} | Error: {str(e)}", 
            exc_info=True
        )
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "login_error": "Error interno",
                "register_error": None
            }
        )

# Ruta para el registro de usuarios
@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request, 
    username: str = Form(..., alias="register-username"), 
    password: str = Form(..., alias="register-password")
):

    # Endpoint de registro de nuevos usuarios
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Intento de registro | Usuario: {username} | IP: {client_ip}")

    # Hashear la contraseña antes de almacenarla en la bbdd
    hashed_password = hash_password(password)
    
    try:
        async with request.app.state.pool.connection() as conn:
            async with conn.cursor() as cur:
                # Inserta el nuevo usuario y la contraseña cifrada en la bbdd
                await cur.execute("INSERT INTO users (username, password_hashed) values (%s,%s)", (username, hashed_password))
                await conn.commit()

        logger.info(f"Usuario registrado exitosamente | Usuario: {username} | IP: {client_ip}")
        return templates.TemplateResponse(
            "welcome.html", 
            {
                "request": request, 
                "username": username, 
                "message": "¡Bienvenido"
            }
        )
    
    except psycopg.IntegrityError as e:
        logger.warning(f"Registro fallido | Usuario duplicado: {username} | IP: {client_ip}")
        # Si el usuario ya existe, muestra un error específico
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "register_error": "El usuario ya existe. Intenta con otro nombre.", 
                "login_error": None
            }
        )
    
    except Exception as e:
        logger.error(
            f"Error en registro | Usuario: {username} | IP: {client_ip} | Error: {str(e)}", 
            exc_info=True
        )
        # Captura cualquier otro error durante el registro
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request, 
                "register_error": "Error al registrar el usuario. Intenta nuevamente.", 
                "login_error": None
            }
        )

# Ruta para healthcheck
@app.get("/health")
async def health():
    # Endpoint de health check
    try:
        async with app.state.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                await cur.fetchone()

        logger.debug("Health check: OK")
        return {
            "status": "healthy",
            "database": "connected"
        }                
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }