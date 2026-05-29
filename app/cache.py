import json
from app.redis import redis_client

async def get_cache(key: str, ttl: int = 300):
    print("CACHE GET:", key)
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None


async def set_cache(key: str, value, ttl: int = 300):
    print("CACHE SET:", key, value)
    await redis_client.set(
        key,
        json.dumps(value),
        ex=ttl
    )


async def delete_cache(key: str):
    await redis_client.delete(key)