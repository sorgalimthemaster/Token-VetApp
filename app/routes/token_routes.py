from fastapi import APIRouter, Depends, HTTPException, status
from app import schemas, auth
from app.dependencies import get_current_user
from fastapi_limiter.depends import RateLimiter
from app.logger import logger

router = APIRouter(prefix="/token", tags=["Token de un solo uso"])

@router.post(
    "/create", 
    response_model=schemas.OneTimeToken,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def create_onetime_token(current_user = Depends(get_current_user)):
    logger.info(f"User {current_user.correo} requested one-time token")
    token = await auth.generate_onetime_token()
    return {"token": token}

@router.post(
    "/validate",
    dependencies=[Depends(RateLimiter(times=20, seconds=60))]
)
async def validate_token(token_data: schemas.OneTimeToken, current_user = Depends(get_current_user)):
    logger.info(f"User {current_user.correo} validating token")
    valid = await auth.validate_onetime_token(token_data.token)
    if not valid:
        logger.warning(f"Token validation failed for user {current_user.correo}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o ya utilizado")
    logger.info(f"Token validated successfully for user {current_user.correo}")
    return {"message": "Token válido y ahora consumido"}
