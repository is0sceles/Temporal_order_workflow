from temporalio import workflow
from activities.order_activities import package_prepared, carrier_dispatched

@workflow.defn
class ShippingWorkflow:
    @workflow.run
    async def run(self, order: dict) -> str:
        try:
            result = await workflow.execute_activity(
                package_prepared,
                order,
                schedule_to_close_timeout=5,
                retry_policy={"maximum_attempts": 3},
            )

            dispatch_result = await workflow.execute_activity(
                carrier_dispatched,
                order,
                schedule_to_close_timeout=5,
                retry_policy={"maximum_attempts": 3},
            )

            return dispatch_result
        except Exception as e:
            # send a signal back to parent OrderWorkflow
            await workflow.signal_external_workflow(
                workflow.ExternalWorkflowHandle(
                    workflow.info().parent_workflow_id,
                    workflow.info().parent_run_id,
                ),
                "DispatchFailed",
                str(e),
            )
            raise
