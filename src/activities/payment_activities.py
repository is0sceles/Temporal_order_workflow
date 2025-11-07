from typing import Dict, Any
from temporalio import activity
from src.utils.logger import get_logger
from src.utils.flaky_call import flaky_call

logger = get_logger("activities.order")

# ---- Database helpers ----
async def write_db(pool, query: str, params: tuple = ()):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params)
            await conn.commit()


async def fetch_one(pool, query: str, params: tuple = ()):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, params)
            return await cur.fetchone()


@activity.defn(name="payment_charged")
async def payment_charged(order: Dict[str, Any], payment_id: str, db_pool) -> Dict[str, Any]:
    """Charge payment after simulating an error/timeout first.
    Demonstrates idempotency by checking existing records before reprocessing.
    """
    order_id = order.get("order_id")
    logger.info(f"Charging payment {payment_id} for order {order_id}")
    await flaky_call()

    # Idempotency check
    existing = await fetch_one(
        db_pool,
        "SELECT status FROM payments WHERE payment_id=%s AND order_id=%s",
        (payment_id, order_id),
    )
    if existing and existing[0] == "charged":
        logger.info(f"Payment {payment_id} already charged (idempotent skip)")
        return {"status": "charged", "amount": sum(i.get("qty", 1) for i in order.get("items", []))}

    amount = sum(i.get("qty", 1) for i in order.get("items", []))
    await write_db(
        db_pool,
        """
        INSERT INTO payments (payment_id, order_id, amount, status)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE amount=%s, status=%s
        """,
        (payment_id, order_id, amount, "charged", amount, "charged"),
    )
    logger.info(f"Payment {payment_id} charged for order {order_id} (amount={amount})")
    return {"status": "charged", "amount": amount}