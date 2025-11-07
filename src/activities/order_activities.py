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



@activity.defn(name="order_received")
async def order_received(order_id: str, db_pool) -> Dict[str, Any]:
    logger.info(f"Received order {order_id}")
    try:
        await flaky_call()
        await write_db(
            db_pool,
            """
            INSERT INTO orders (order_id, status)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE status=%s
            """,
            (order_id, "received", "received"),
        )
        logger.info(f"Order {order_id} recorded in DB")
        return {"order_id": order_id, "items": [{"sku": "ABC", "qty": 1}]}
    except Exception as e:
        logger.error(f"order_received failed for {order_id}: {e}")
        raise


@activity.defn(name="validated")
async def validated(order: Dict[str, Any], db_pool) -> bool:
    order_id = order.get("order_id")
    logger.info(f"Validating order {order_id}")
    await flaky_call()
    if not order.get("items"):
        logger.warning(f"Validation failed — no items in order {order_id}")
        raise ValueError("No items to validate")

    await write_db(
        db_pool,
        "UPDATE orders SET status=%s WHERE order_id=%s",
        ("validated", order_id),
    )
    logger.info(f"Order {order_id} marked as validated")
    return True


@activity.defn(name="package_prepared")
async def package_prepared(order: Dict[str, Any], db_pool) -> str:
    order_id = order.get("order_id")
    logger.info(f"Preparing package for order {order_id}")
    await flaky_call()
    await write_db(
        db_pool,
        "UPDATE orders SET status=%s WHERE order_id=%s",
        ("package_prepared", order_id),
    )
    logger.info(f"Order {order_id} package prepared")
    return "Package ready"


@activity.defn(name="carrier_dispatched")
async def carrier_dispatched(order: Dict[str, Any], db_pool) -> str:
    order_id = order.get("order_id")
    logger.info(f"Dispatching carrier for order {order_id}")
    await flaky_call()
    await write_db(
        db_pool,
        "UPDATE orders SET status=%s WHERE order_id=%s",
        ("dispatched", order_id),
    )
    logger.info(f"Carrier dispatched for order {order_id}")
    return "Dispatched"

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