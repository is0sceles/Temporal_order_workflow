import aiomysql
import asyncio
import os

async def check_db():
    conn = await aiomysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3360)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        db=os.getenv("DB_NAME", "order_app")
    )
    async with conn.cursor() as cur:
        await cur.execute("SELECT DATABASE();")
        db = await cur.fetchone()
        print("Connected to DB:", db[0])
    conn.close()

asyncio.run(check_db())
