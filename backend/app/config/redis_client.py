import redis
from settings import settings

redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

def get_redis_client():
    """Trả về một Redis client từ connection pool."""
    return redis.Redis(connection_pool=redis_pool)