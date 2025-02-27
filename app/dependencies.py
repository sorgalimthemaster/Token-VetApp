from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.async_db import AsyncSessionLocal
from app import models, security
from jose import JWTError
from sqlalchemy.future import select
from app.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_db():
    async with AsyncSessionLocal() as session:
         yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.verify_token(token)
        if payload is None:
            logger.error("Token verification failed: payload is None")
            raise credentials_exception
        correo: str = payload.get("sub")
        if correo is None:
            logger.error("Token payload missing 'sub'")
            raise credentials_exception
    except JWTError:
        logger.error("JWTError during token verification", exc_info=True)
        raise credentials_exception
    result = await db.execute(select(models.User).filter(models.User.correo == correo))
    user = result.scalar_one_or_none()
    if user is None:
        logger.error(f"User {correo} not found in database")
        raise credentials_exception
    return user
