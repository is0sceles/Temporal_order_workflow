# src/db/db.py
import os
import aiomysql
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

_pool: Optional[aiomysql.Pool] = None


async def init_db_pool():
    """
    Initialize the global aiomysql connection pool.
    """
    global _pool
    if _pool is not None:
        return _pool  # already initialized

    _pool = await aiomysql.create_pool(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER",),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME", "order_app"),
        minsize=1,
        maxsize=10,
        autocommit=True,
    )
    print("DB connection pool created")
    return _pool


async def get_conn():
    """
    Acquire a single connection from the pool.
    Usage: async with (await get_conn()).cursor() as cur:
    """
    if _pool is None:
        await init_db_pool()
    return _pool


async def close_db_pool():
    """
    Close pool cleanly at shutdown.
    """
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()
        print("DB connection pool closed")
        _pool = None
