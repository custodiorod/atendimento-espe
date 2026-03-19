"""
Rate limiting por contato — protege o WhatsApp de bloqueios.
"""

from app.execution.queue.redis_lock import get_redis


async def check_rate_limit(contact_id: str, max_per_minute: int = 10) -> bool:
    """
    Verifica se o contato está dentro do rate limit.
    Retorna True se pode enviar, False se bloqueado.
    """
    r = get_redis()
    key = f"ratelimit:contact:{contact_id}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, 60)
    return count <= max_per_minute
