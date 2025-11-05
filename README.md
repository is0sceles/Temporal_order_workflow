# Temporal Workflow: **Function Stubs Only** (Python) with DB Read/Write Notes

## Goal

Use [Temporal’s open‑source SDK](https://github.com/temporalio/temporal) and dev server to orchestrate an **Order Lifecycle**. You will design the **workflows** and **activities**. This doc supplies **function implementations** that simulate failures and timeouts, plus assignment requirements. Your **activities** should call these functions and handle database persistence.

## Why Use Temporal

Coordinates long-running, stateful operations where reliability and clear audit trails matter (e.g., multi-step data workflows, vendor calls, human approvals). Temporal gives:

- **Durability & fault tolerance.** Workflow state is persisted, so workers can crash or be redeployed without losing progress. Retries, backoffs and timeouts are first-class—not bolted on.
- **Deterministic orchestration.** We encode the _control plane_ (timers, signals, child workflows, compensation) once; Temporal replays history to guarantee consistent decisions across retries and restarts.
- **Idempotent side effects.** Activities are retried safely; we implement idempotency keys in our own DB to make external calls (payments, notifications, writes) safe to repeat.
- **Human-in-the-loop.** Signals and timers make manual review/approvals and SLAs natural, without custom schedulers or cron drift.
- **Observability by design.** The event history is a truthful source for debugging, auditing, and support. We can expose live status and recent errors without inventing bespoke tracking.

### Why an “Order” workflow?

An **Order → Payment → Shipping** model because it’s simple and self-contained while still exercising the core Temporal primitives we care about in real work:

- **Signals & timers:** Manual review before payment is a realistic human gate with a deadline.
- **Retries, timeouts, compensation:** Payments and dispatch are classic side-effects that must be idempotent and safely retried.
- **Child workflows & task-queue isolation:** Shipping runs on its own queue, showing how we scale teams/services independently.
- **End-to-end state & auditing:** Orders, payments, and shipping events provide a clean domain to persist to SQL and query live status.

An order domain avoids domain-specific baggage and lets you focus on orchestration quality—determinism, resilience, and observability in production workflows.

### Parent Workflow: `OrderWorkflow`

- **Steps (activities):** `ReceiveOrder → ValidateOrder → (Timer: ManualReview) → ChargePayment → ShippingWorkflow`.
- **Signals:**
  - `CancelOrder` — cancels order before shipment.
  - `UpdateAddress` — updates shipping address prior to dispatch.
- **Timer:** Insert a delay between validation and payment (simulated manual review). Only goes onto the next part of the temporal workflow once a human manually approves the order, which then hits the ChargePayment activity.
- **Child Workflow:** After successful payment, start `ShippingWorkflow` on a **separate task queue**.
- **Cancellations/Failures:** Handle gracefully; propagate or compensate as appropriate.
- **Time Constraint:** The Entire Workflow Must Complete Within 15 seconds.

### Child Workflow: `ShippingWorkflow`

- **Activities:** `PreparePackage`, `DispatchCarrier`.
- **Parent Notification:** If dispatch fails, **signal back** to parent (e.g., `DispatchFailed(reason)`) and ask the Parent to retry .
- **Own task queue** (e.g., `"shipping-tq"`) to demonstrate queue isolation.

| Method & Path                                | Description                                                 |
| -------------------------------------------- | ----------------------------------------------------------- |
| **POST** `/orders/{order_id}/start`          | Starts `OrderWorkflow` with a provided `payment_id`.        |
| **POST** `/orders/{order_id}/signals/cancel` | Sends the `CancelOrder` signal.                             |
| **GET** `/orders/{order_id}/status`          | Queries `OrderWorkflow.status()` to retrieve current state. |

## How to start Temporal server and database.

#### 1. Run Docker in project root:

```
docker compose down -v
docker compose up -d
```

This will:

- Stop all containers

- Remove attached volumes (clearing MySQL + Temporal state)

- Recreate a fresh environment

Then, after containers are back up:

```
docker ps
```

Ensure you see both mysql and temporal running.

#### 2. Re/start Python worker:

```
python src/worker.py
```

#### 3. And API server:

```
uvicorn src.api.server:app --reload

```

#### 4. Start workflow

```
curl -X POST "http://127.0.0.1:8000/orders/123/start?payment_id=abc123"
```

## How to run workers and trigger workflow.

#### Start order

```
curl -X POST "http://127.0.0.1:8000/orders/123/start?payment_id=abc123"
```

#### Update address

```
curl -X POST "http://localhost:8000/orders/123/signals/update-address" \
 -H "Content-Type: application/json" \
 -d '{"new_address": "742 Evergreen Terrace"}'
```

## How to send signals and query/inspect state.

#### Cancel workflow

```
curl -X POST "http://localhost:8000/orders/123/signals/cancel"
```

#### Query workflow state

```
curl http://localhost:8000/orders/123/state
```

#### Check current Temporal status

```
curl http://localhost:8000/orders/123/status
```

####

## Schema/migrations and persistence.

src/db/migrate.py

## Tests and how to run them.

TODO

## DEV NOTES

##### local env:

```
source venv/bin/activate
```

#### docker:

```
docker compose up (-d detached)
docker compose down (-v volumes)
docker compose config : docker yml
docker compose ps : containers
docker compose logs -f temporal
```

#### if sql permission errors:

- run docker in detached mode
- exec into sql and give root permission

```
docker compose up -d

docker exec -it temporal_order_workflow-mysql-1 mysql -u root -ptemporal

CREATE DATABASE IF NOT EXISTS temporal;
CREATE DATABASE IF NOT EXISTS temporal_visibility;

CREATE USER IF NOT EXISTS 'temporal'@'%' IDENTIFIED BY 'temporal';

GRANT ALL PRIVILEGES ON temporal.* TO 'temporal'@'%';
GRANT ALL PRIVILEGES ON temporal_visibility.* TO 'temporal'@'%';
GRANT ALL PRIVILEGES ON order_app.* TO 'temporal'@'%';

FLUSH PRIVILEGES;
EXIT;


docker compose restart temporal
```

#### if still permissions error check inside mysql:

```
SHOW GRANTS FOR 'temporal'@'%';
```

#### check worker status

```
ps aux | grep worker
```

#### exit:

```
docker compose down -v
deactivate
```

#### test

```
curl http://localhost:7233
```

##### postgres (not using)

##### inside docker -psql:

```
docker exec -it temporal_order_workflow-postgres-1 psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
psql -h localhost -p 5432 -U [PWD] -d [DB]
```
