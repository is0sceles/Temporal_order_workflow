async def order_shipped(order: Dict[str, Any]) -> str:
    await flaky_call()
    # TODO: Implement DB write: update order status to shipped
    return "Shipped"

async def package_prepared(order: Dict[str, Any]) -> str:
    await flaky_call()
    # TODO: Implement DB write: mark package prepared in DB
    return "Package ready"

async def carrier_dispatched(order: Dict[str, Any]) -> str:
    await flaky_call()
    # TODO: Implement DB write: record carrier dispatch status
    return "Dispatched"