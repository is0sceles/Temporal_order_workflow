# migrate.py
import os
import asyncio
import aiomysql
from dotenv import load_dotenv


load_dotenv() 

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

async def run_migration():
    # Connect to MySQL
    conn = await aiomysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
    )

    async with conn.cursor() as cur:
        with open("schema.sql") as f:
            sql = f.read()
        # Split statements and execute one by one
        for stmt in sql.strip().split(";"):
            if stmt.strip():
                await cur.execute(stmt)
                print(f"Executed: {stmt.strip()[:50]}...")

        await conn.commit()

    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(run_migration())
