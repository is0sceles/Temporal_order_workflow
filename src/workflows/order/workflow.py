from datetime import timedelta
from temporalio import workflow
from src.activities import order_activities
from src.workflows.shipping.workflow import ShippingWorkflow

@workflow.defn
class OrderWorkflow:
    def __init__(self):
        self.order = None
        self.payment = None
        self.status = "initialized"
        self.address = None
        self.error = None

    @workflow.run
    async def run(self, order_id: str, payment_id: str):
        self.status = "started"

        try:
            self.order = await workflow.execute_activity(
                order_activities.order_received,
                order_id,
                schedule_to_close_timeout=timedelta(minutes=10),
            )

            valid = await workflow.execute_activity(
                order_activities.order_validated,
                self.order,
                schedule_to_close_timeout=timedelta(minutes=10),
            )

            await workflow.sleep(3)  # Manual review delay
            self.status = "validated"

            self.payment = await workflow.execute_activity(
                order_activities.payment_charged,
                self.order,
                payment_id,
                schedule_to_close_timeout=timedelta(minutes=10),
            )

            if self.payment.get("status") == "charged":
                self.status = "shipping_started"
                await workflow.execute_child_workflow(
                    ShippingWorkflow.run,
                    self.order,
                    id=f"ship-{order_id}",
                    task_queue="shipping-tq",
                )
                self.status = "completed"

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            raise

        return "Order complete"

    # --- Signals ---
    @workflow.signal
    async def CancelOrder(self):
        """Cancel this order mid-flight."""
        self.status = "cancelled"
        workflow.logger.info(f"Order {self.order} cancelled")
        workflow.exit("Order cancelled")

    @workflow.signal
    async def UpdateAddress(self, new_address: str):
        """Update the shipping address."""
        self.address = new_address
        workflow.logger.info(f"Address updated: {new_address}")

    # --- Query ---
    @workflow.query
    def GetState(self) -> dict:
        """Inspect workflow live state."""
        return {
            "status": self.status,
            "order": self.order,
            "payment": self.payment,
            "address": self.address,
            "error": self.error,
        }
