from contextlib import asynccontextmanager
from fastapi import FastAPI
from temporalio.client import Client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to Temporal
    print("Connecting to Temporal...")
    app.state.client = await Client.connect("localhost:7233")
    yield
    # Shutdown: close Temporal connection
    print("Closing Temporal connection...")
    await app.state.client.close()

app = FastAPI(lifespan=lifespan)

@app.post("/orders/{order_id}/start")
async def start_order(order_id: str, payment_id: str):
    handle = await app.state.client.start_workflow(
    workflow="OrderWorkflow",
    args=[order_id, payment_id],
    id=order_id,    
    task_queue="order-tq"
    )
    return {"workflow_id": handle.id}

@app.post("/orders/{order_id}/signals/cancel")
async def cancel_order(order_id: str):
    handle = app.state.client.get_workflow_handle(order_id)
    await handle.signal("CancelOrder")
    return {"status": "cancelled"}

@app.get("/orders/{order_id}/status")
async def get_status(order_id: str):
    handle = app.state.client.get_workflow_handle(order_id)
    desc = await handle.describe()
    return {"status": desc.status.name}

@app.get("/health")
async def health():
    return {"status": "ok"}