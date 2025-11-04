import os
import asyncio
import aiomysql
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT"))
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "order_app")

    print("Connecting to:", host, port, db_name)

    conn = await aiomysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db_name
    )

    async with conn.cursor() as cur:
        await cur.execute("SELECT DATABASE();")
        db = await cur.fetchone()
        print("Connected to DB:", db[0])
    conn.close()

asyncio.run(check_db())
