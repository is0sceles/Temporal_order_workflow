import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from functools import partial
import inspect
from temporalio.worker import Worker
from temporalio.client import Client

from src.workflows.order.workflow import OrderWorkflow
from src.workflows.shipping.workflow import ShippingWorkflow
from src.activities.order_activities import (
    order_received,
    validated,
    payment_charged,
    package_prepared,
    carrier_dispatched,
)
from src import setup_logging

from src.db.db import init_db_pool, close_db_pool

setup_logging()
from src.activities.order_activities import order_received
from temporalio import activity
print("order_received type:", type(order_received))
print("is Temporal activity:", isinstance(order_received, activity._Definition))
print("Module:", order_received.__module__)
print("File path:", inspect.getfile(order_received))
print(hasattr(order_received, "__temporal_activity_definition__"))
print("sys.path:", sys.path)
print("\nLoaded modules:")
for k in sys.modules.keys():
    if "order_activities" in k:
        print("  -", k)
from src.activities import order_activities, payment_activities, shipping_activities

for mod in [order_activities, payment_activities, shipping_activities]:
    for name in dir(mod):
        obj = getattr(mod, name)
        if callable(obj) and hasattr(obj, "_temporal_activity_defn"):
            print(f"✅ Registered Temporal activity: {mod.__name__}.{name}")
        elif callable(obj) and not name.startswith("__"):
            print(f"⚠️ Not a Temporal activity: {mod.__name__}.{name}")

async def main():
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")

    # Create a single DB pool for all activities (worker-local)
    db_pool = await init_db_pool()

    # Wrap activities with db_pool using functools.partial so signatures remain compatible.
    # We inject db_pool as the last parameter (activities expect db_pool as final arg).
    activities = [
        partial(order_received, db_pool=db_pool),
        partial(validated, db_pool=db_pool),
        partial(payment_charged, db_pool=db_pool),
        partial(package_prepared, db_pool=db_pool),
        partial(carrier_dispatched, db_pool=db_pool),
    ]

    worker = Worker(
        client,
        task_queue="order-tq",
        workflows=[OrderWorkflow, ShippingWorkflow],
        activities=activities,
    )

    try:
        await worker.run()
    finally:
        # graceful shutdown: close DB pool and Temporal client
        await close_db_pool()
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())