from pydantic import BaseSettings

class Settings(BaseSettings):
    # Configuración de la aplicación
    app_name: str = "Token Service API"
    secret_key: str = "clave_super_segura_cambia_esto"  # Cambiar en producción
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # Token de autenticación
    onetime_token_expire_seconds: int = 10  # Token de un solo uso

    # Configuración de la base de datos PostgreSQL
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "db"
    db_port: str = "5432"
    db_name: str = "token_service"

    # Configuración de Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    class Config:
        env_file = ".env"

settings = Settings()
