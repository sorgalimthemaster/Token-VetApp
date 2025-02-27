import aioredis
from app.config import settings

async_redis = None

async def init_async_redis():
    global async_redis
    async_redis = await aioredis.create_redis_pool(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf8",
        decode_responses=True
    )
