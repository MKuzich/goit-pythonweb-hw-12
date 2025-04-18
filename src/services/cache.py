import os
import redis
import json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_cached_user(email: str):
    """
    Retrieve user data from Redis cache.

    :param email: The email of the user.
    :return: User data if found, otherwise None.
    """
    data = r.get(f"user:{email}")
    return json.loads(data) if data else None

def set_cached_user(email: str, user_data: dict):
    """
    Store user data in Redis cache.

    :param email: The email of the user.
    :param user_data: The user data to cache.
    :return: None
    """
    r.set(f"user:{email}", json.dumps(user_data), ex=3600)
