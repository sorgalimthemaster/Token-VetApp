from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import aioredis
from fastapi_limiter import FastAPILimiter

from app.routes import auth_routes, token_routes
from app.async_db import engine
from app.models import Base
from app.config import settings
from app.logger import logger
from app.utils import init_async_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar pool de Redis para rate limiting
    redis = await aioredis.create_redis_pool(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf8",
        decode_responses=True
    )
    await FastAPILimiter.init(redis)
    # Inicializar nuestro cliente asíncrono para operaciones propias
    await init_async_redis()
    yield
    redis.close()
    await redis.wait_closed()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Configurar CORS (en producción, restringir los orígenes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador global para HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Manejador global para excepciones no controladas
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception occurred", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# Incluir routers
app.include_router(auth_routes.router)
app.include_router(token_routes.router)
