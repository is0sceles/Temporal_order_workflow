import asyncio
from temporalio.worker import Worker
from temporalio.client import Client
from workflows.order.workflow import OrderWorkflow
from src.workflows.shipping.workflow import ShippingWorkflow
from src.activities import order_activities, payment_activities, shipping_activities

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="order-tq",
        workflows=[OrderWorkflow, ShippingWorkflow],
        activities=[
            order_activities.order_received,
            order_activities.order_validated,
            payment_activities.payment_charged,
            shipping_activities.package_prepared,
            shipping_activities.carrier_dispatched
        ]
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
