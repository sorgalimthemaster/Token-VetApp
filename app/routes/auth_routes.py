from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, models, auth, security
from app.dependencies import get_db
from fastapi_limiter.depends import RateLimiter
from app.logger import logger

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post(
    "/register", 
    response_model=schemas.UserOut,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
async def register(user_create: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Registering user {user_create.correo}")
    from sqlalchemy.future import select
    result = await db.execute(select(models.User).filter(models.User.correo == user_create.correo))
    user_exist = result.scalar_one_or_none()
    if user_exist:
        logger.warning(f"Registration failed: User {user_create.correo} already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está registrado")
    
    hashed_password = security.get_password_hash(user_create.password)
    new_user = models.User(
        nombre=user_create.nombre,
        correo=user_create.correo,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info(f"User {user_create.correo} registered successfully")
    return new_user

@router.post(
    "/login", 
    response_model=schemas.Token,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
async def login(user_login: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    logger.info(f"Login attempt for {user_login.correo}")
    user = await auth.authenticate_user(db, user_login.correo, user_login.password)
    if not user:
        logger.warning(f"Login failed for {user_login.correo}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    access_token = auth.generate_access_token(user.correo)
    logger.info(f"Access token generated for {user_login.correo}")
    return {"access_token": access_token, "token_type": "bearer"}
