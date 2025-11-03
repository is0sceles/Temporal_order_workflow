from typing import Dict, Any
from utils.flaky_call import flaky_call
from temporalio import activity

@activity.defn
async def order_received(order_id: str) -> Dict[str, Any]:
    await flaky_call()
    # TODO: DB write
    return {"order_id": order_id, "items": [{"sku": "ABC", "qty": 1}]}

@activity.defn
async def validated(order: Dict[str, Any]) -> bool:
    await flaky_call()
    if not order.get("items"):
        raise ValueError("No items to validate")
    # TODO: update validation status in DB
    return True

@activity.defn
async def package_prepared(order: dict[str, any]) -> str:
    await flaky_call()
    # TODO: Implement DB write: mark package prepared in DB
    return "Package ready"

@activity.defn
async def carrier_dispatched(order: dict[str, any]) -> str:
    await flaky_call()
    # TODO: Implement DB write: record carrier dispatch status
    return "Dispatched"

@activity.defn
async def payment_charged(order: dict[str, any], payment_id: str, db) -> dict[str, any]:
    """Charge payment after simulating an error/timeout first.
    You must implement your own idempotency logic in the activity or here.
    """
    await flaky_call()
    # TODO: Implement DB read/write: check payment record, insert/update payment status
    amount = sum(i.get("qty", 1) for i in order.get("items", []))
    return {"status": "charged", "amount": amount}