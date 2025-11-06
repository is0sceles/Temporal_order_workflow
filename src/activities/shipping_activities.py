from typing import Dict, Any
from temporalio import activity
from utils.logger import get_logger
from utils.flaky_call import flaky_call

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



async def order_shipped(order: dict[str, any]) -> str:
    await flaky_call()
    # TODO: Implement DB write: update order status to shipped
    return "Shipped"

@activity.defn
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


@activity.defn
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