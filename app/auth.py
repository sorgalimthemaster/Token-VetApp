import uuid
from datetime import timedelta
from app import security
from app.config import settings
from app.logger import logger
from app.utils import async_redis
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

async def authenticate_user(db: AsyncSession, correo: str, password: str):
    logger.info(f"Authenticating user {correo}")
    result = await db.execute(select(User).filter(User.correo == correo))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning(f"User {correo} not found")
        return False
    if not security.verify_password(password, user.hashed_password):
        logger.warning(f"Password mismatch for user {correo}")
        return False
    logger.info(f"User {correo} authenticated successfully")
    return user

def generate_access_token(correo: str):
    logger.info(f"Generating access token for {correo}")
    data = {"sub": correo}
    access_token = security.create_access_token(
        data=data, 
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return access_token

async def generate_onetime_token():
    logger.info("Generating one-time token")
    token_id = str(uuid.uuid4())
    data = {"jti": token_id}
    token = security.create_onetime_token(data)
    await async_redis.set(token_id, "valid", expire=settings.onetime_token_expire_seconds)
    logger.info(f"One-time token {token_id} stored in Redis")
    return token

async def validate_onetime_token(token: str):
    logger.info("Validating one-time token")
    payload = security.verify_token(token)
    if payload is None or "jti" not in payload:
        logger.warning("Token payload invalid or missing jti")
        return False
    token_id = payload["jti"]
    exists = await async_redis.get(token_id)
    if exists:
        await async_redis.delete(token_id)
        logger.info(f"Token {token_id} validated and deleted")
        return True
    logger.warning(f"Token {token_id} not found or already used")
    return False
