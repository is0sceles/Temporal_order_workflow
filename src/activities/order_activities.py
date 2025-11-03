from typing import Dict, Any
from utils.flaky_call import flaky_call

async def order_received(order_id: str) -> Dict[str, Any]:
    await flaky_call()
    # TODO: DB write
    return {"order_id": order_id, "items": [{"sku": "ABC", "qty": 1}]}

async def order_validated(order: Dict[str, Any]) -> bool:
    await flaky_call()
    if not order.get("items"):
        raise ValueError("No items to validate")
    # TODO: update validation status in DB
    return True
