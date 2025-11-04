import asyncio
from temporalio.worker import Worker
from temporalio.client import Client
from workflows.order.workflow import OrderWorkflow
from workflows.shipping.workflow import ShippingWorkflow
from activities.order_activities import (
    order_received, validated, payment_charged, package_prepared, carrier_dispatched
)
from __init__ import setup_logging
setup_logging()

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="order-tq",
        workflows=[OrderWorkflow, ShippingWorkflow],
        activities=[
            order_received,
            validated,
            payment_charged,
            package_prepared,
            carrier_dispatched,
        ]
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
