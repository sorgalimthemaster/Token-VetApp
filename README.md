# Token Service API

## Descripción

Token Service API es un servicio REST diseñado para la creación y validación de tokens de un solo uso, desarrollado con **FastAPI** y optimizado para un rendimiento y seguridad de nivel empresarial. El servicio incluye:

- **Registro y autenticación de usuarios** (almacenados en PostgreSQL).
- **Generación de tokens JWT** para autenticación.
- **Generación y validación de tokens de un solo uso** (gestionados en Redis con un tiempo de expiración corto).
- **Rate limiting** para prevenir abusos.
- **Logging** centralizado y manejo global de errores para facilitar la auditoría y el monitoreo.
- **Soporte CORS** y otras configuraciones de seguridad.

El servicio sigue los principios SOLID, está migrado a SQLAlchemy asíncrono y utiliza Python 3.11.9 para maximizar la eficiencia tanto en el consumo de recursos como en la velocidad de respuesta.

## Arquitectura del Proyecto

La estructura del proyecto es la siguiente:

```
project/
├── app/
│   ├── __init__.py
│   ├── async_db.py          # Configuración de SQLAlchemy asíncrono
│   ├── auth.py              # Lógica de autenticación y gestión de tokens
│   ├── config.py            # Configuración de la aplicación (variables de entorno)
│   ├── dependencies.py      # Dependencias (sesiones asíncronas, usuario actual, etc.)
│   ├── logger.py            # Configuración centralizada de logging
│   ├── models.py            # Definición de modelos (usuarios)
│   ├── routes/
│   │   ├── auth_routes.py   # Endpoints para registro y login
│   │   └── token_routes.py  # Endpoints para creación y validación de tokens de un solo uso
│   ├── schemas.py           # Esquemas de validación con Pydantic
│   ├── security.py          # Funciones para manejo de contraseñas y JWT
│   └── utils.py             # Utilidades (cliente Redis asíncrono, etc.)
├── Dockerfile               # Imagen para Python 3.11.9-slim y despliegue de la aplicación
├── docker-compose.yml       # Orquestación de servicios (app, PostgreSQL y Redis)
└── requirements.txt         # Dependencias del proyecto
```

## Tecnologías y Dependencias

- **Python 3.11.9**
- **FastAPI** para la creación de la API.
- **SQLAlchemy (asíncrono)** con **asyncpg** para la gestión de PostgreSQL.
- **Redis** para la gestión de tokens de un solo uso.
- **JWT (python-jose)** para la generación y verificación de tokens.
- **Rate Limiting** con **fastapi-limiter**.
- **Passlib** para el hash de contraseñas.
- **Docker** y **docker-compose** (o **podman-compose**) para el despliegue.

## Requisitos

- Docker o Podman instalado en el sistema.
- Podman-compose (si utilizas Podman).
- Acceso a Internet para descargar las imágenes y dependencias.

## Configuración de Variables de Entorno

El archivo `app/config.py` utiliza Pydantic para gestionar las variables de entorno. Puedes crear un archivo `.env` en la raíz del proyecto para sobreescribir las siguientes variables si es necesario:

```env
app_name=Token Service API
secret_key=clave_super_segura_cambia_esto
access_token_expire_minutes=15
onetime_token_expire_seconds=10

db_user=postgres
db_password=postgres
db_host=db
db_port=5432
db_name=token_service

redis_host=redis
redis_port=6379
redis_db=0
```

## Despliegue y Ejecución

### Usando Docker Compose (o Podman Compose)

1. **Clonar el repositorio** y ubicarse en la raíz del proyecto.

2. **Construir y levantar los servicios**:
   ```bash
   podman-compose up --build -d
   ```
   *(Si utilizas Docker, reemplaza `podman-compose` por `docker-compose`.)*

3. **Verificar el estado de los contenedores**:
   ```bash
   podman ps
   ```
   Para ver los logs en tiempo real:
   ```bash
   podman-compose logs -f
   ```

4. **Acceso a la API**:  
   La API se ejecutará en el puerto **8000**. Puedes acceder a la documentación interactiva de la API en:  
   [http://localhost:8000/docs](http://localhost:8000/docs)

5. **Detener los servicios**:
   ```bash
   podman-compose down
   ```

### Construcción y Ejecución Manual con Dockerfile

Si deseas construir solo la imagen de la aplicación, puedes ejecutar:
```bash
podman build -t token_service_app .
podman run -p 8000:8000 token_service_app
```

## Endpoints Principales

### Autenticación y Registro
- **POST /auth/register**  
  Registra un nuevo usuario.  
  **Campos**: `nombre`, `correo`, `password`

- **POST /auth/login**  
  Autentica al usuario y devuelve un token JWT.  
  **Campos**: `correo`, `password`

### Gestión de Tokens de Un Solo Uso
- **POST /token/create**  
  Genera un token de un solo uso. *(Requiere autenticación via JWT)*

- **POST /token/validate**  
  Valida y consume un token de un solo uso. *(Requiere autenticación via JWT)*

## Logging y Manejo de Errores

El servicio cuenta con:
- **Logging centralizado**: Todas las acciones y errores importantes se registran mediante el módulo `app/logger.py`.
- **Manejo global de errores**: Se han definido controladores de excepciones para capturar errores HTTP y excepciones inesperadas, retornando respuestas estandarizadas y facilitando la auditoría.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un _issue_ o envía un _pull request_ para discutir cualquier cambio o mejora.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
