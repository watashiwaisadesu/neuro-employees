import redis.asyncio as aioredis

from src.core.config import Config

JTI_EXPIRY = Config.REFRESH_TOKEN_EXPIRY_DAYS * 86400

token_blocklist = aioredis.from_url(Config.REDIS_URL)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)

    return jti is not None