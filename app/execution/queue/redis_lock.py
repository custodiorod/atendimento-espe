"""
Redis — locks de concorrência por contato, rate limit e cooldown de mensagens.
"""

import os
import redis.asyncio as redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

_client = None


def get_redis():
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client


async def acquire_lock(contact_id: str, ttl: int = 30) -> bool:
    """Tenta adquirir lock para um contato. Retorna True se conseguiu."""
    r = get_redis()
    key = f"lock:contact:{contact_id}"
    return await r.set(key, "1", nx=True, ex=ttl)


async def release_lock(contact_id: str):
    """Libera o lock de um contato."""
    r = get_redis()
    key = f"lock:contact:{contact_id}"
    await r.delete(key)
