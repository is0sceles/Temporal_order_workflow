from temporalio import workflow
from activities import order_activities, payment_activities
from workflows.shipping.workflow import ShippingWorkflow

@workflow.defn
class OrderWorkflow:
    def __init__(self):
        self.order = None

    @workflow.run
    async def run(self, order_id: str, payment_id: str):
        self.order = await workflow.execute_activity(
            order_activities.order_received,
            order_id,
            schedule_to_close_timeout=3
        )

        valid = await workflow.execute_activity(
            order_activities.order_validated,
            self.order,
            schedule_to_close_timeout=3
        )

        await workflow.sleep(3)  # Manual review timer

        payment = await workflow.execute_activity(
            payment_activities.payment_charged,
            self.order,
            payment_id,
            schedule_to_close_timeout=3
        )

        if payment["status"] == "charged":
            await workflow.execute_child_workflow(
                ShippingWorkflow.run,
                self.order,
                id=f"ship-{order_id}",
                task_queue="shipping-tq",
            )

        return "Order complete"
