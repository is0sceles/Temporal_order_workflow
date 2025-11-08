import sys
import os
import asyncio
from temporalio.worker import Worker
from temporalio.client import Client

# Ensure src/ is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflows.order.workflow import OrderWorkflow
from src.workflows.shipping.workflow import ShippingWorkflow
from src.activities import order_activities
from src.db.db import init_db_pool, close_db_pool
from src import setup_logging

setup_logging()

async def main():
    client = await Client.connect("localhost:7233")
    db_pool = await init_db_pool()

    # Get activity functions directly — no partials yet
    activities = [
        order_activities.order_received,
        order_activities.validated,
        order_activities.payment_charged,
        order_activities.package_prepared,
        order_activities.carrier_dispatched,
    ]

    print("\n🔍 Activity registration check:")
    for act in activities:
        print(f"{act.__name__}: has _temporal_activity_defn →", hasattr(act, "_temporal_activity_defn"))

    worker = Worker(
        client,
        task_queue="order-tq",
        workflows=[OrderWorkflow, ShippingWorkflow],
        activities=activities,
    )

    try:
        await worker.run()
    finally:
        await close_db_pool()
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
