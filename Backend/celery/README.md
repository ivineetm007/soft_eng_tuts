# Celery — Distributed Task Queue

A hands-on project to understand Celery's internals by building and running real tasks.

---

## What is Celery?

Celery is a **distributed task queue** for Python. You write a normal function, decorate it with `@app.task`, and instead of calling it directly, you call `.delay()` — which serialises the function call into a message, publishes it to a **broker**, and a separate **worker** process picks it up and executes it asynchronously.

**One-line summary:** Offload work from your main process to background workers via a message queue.

### When You Need It

| Scenario                       | Why Celery Helps                              |
| ------------------------------ | --------------------------------------------- |
| Sending emails / notifications | Don't block the API response waiting for SMTP |
| Image/video processing         | CPU-heavy work offloaded to dedicated workers |
| Periodic jobs (cron-like)      | Celery Beat scheduler handles recurring tasks |
| ML inference / LLM API calls   | Keep the web server responsive                |
| Fan-out / parallel pipelines   | Groups & chords run tasks concurrently        |

---

## Core Concepts

### 1. Task

A Python function decorated with `@app.task` — the **unit of work**.

```python
@app.task
def add(x, y):
    return x + y

# This doesn't run add() here — it sends a message to the broker
add.delay(2, 3)
```

### 2. Broker (Message Transport)

The **middleman** — a message queue that holds tasks until a worker picks them up.

| Broker       | Pros                                                      | Cons                                         |
| ------------ | --------------------------------------------------------- | -------------------------------------------- |
| **Redis**    | Simple, fast, doubles as result backend                   | No built-in message durability like RabbitMQ |
| **RabbitMQ** | Purpose-built broker, reliable delivery, advanced routing | More operational overhead                    |

### 3. Worker

A separate **long-running process** that connects to the broker, picks up messages, executes the function, and stores the result.

```bash
celery -A celery_app worker --loglevel=info
```

### 4. Result Backend

An **optional** store where task return values and state are written.

- **Without it:** fire-and-forget — you can't check outcomes.
- **With it:** you get an `AsyncResult` to poll status (PENDING → STARTED → SUCCESS/FAILURE) and retrieve return values.

### 5. Celery Beat (Scheduler)

A separate process that publishes tasks on a schedule — like cron, but using Celery's infrastructure.

---

## Architecture — Message Flow

```
┌──────────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Producer       │     │   Broker     │     │   Worker(s)      │
│   (Your App)     │────▶│   (Redis)    │────▶│                  │
│                  │     │              │     │  Executes tasks   │
│  add.delay(2,3)  │     │  Task Queue  │     │  Stores results  │
└──────────────────┘     └──────────────┘     └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  Result Backend  │
                                              │  (Redis)         │
                                              └──────────────────┘
```

### Message Lifecycle

```
Producer calls .delay()
    │
    ▼
Message serialised (JSON by default)
    │
    ▼
Published to broker queue (Redis list "celery")
    │
    ▼
Worker prefetches message from queue
    │
    ▼
Worker deserialises → executes the function
    │
    ├── Success → result stored in backend, state = SUCCESS
    └── Failure → exception stored, state = FAILURE
              └── Retry? → re-publish to broker with countdown
```

### Key Behaviours

- **Acknowledgement**: Worker ACKs a message _after_ execution. If the worker crashes mid-task, the message goes back to the queue (at-least-once delivery).
- **Prefetching**: Workers prefetch messages for throughput. Configurable via `worker_prefetch_multiplier`.
- **Serialisation**: Default is JSON. Pickle allows Python objects but has security risks.

---

## Concurrency Models — Prefork vs Eventlet vs Gevent

Celery's **pool** option controls how a worker runs multiple tasks simultaneously.

| Pool                  | Mechanism                                                          | Best For                                                    | Tradeoff                                                           |
| --------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------- | ------------------------------------------------------------------ |
| **Prefork** (default) | Spawns N **OS processes** via multiprocessing                      | **CPU-bound** — image processing, ML inference, computation | High memory (N processes × Python interpreter)                     |
| **Eventlet**          | Single process, **green threads** (coroutines) via monkey-patching | **I/O-bound** — HTTP calls, DB queries, API requests        | Can't parallelise CPU work. Monkey-patching may break C-extensions |
| **Gevent**            | Single process, green threads via `libev` event loop               | **I/O-bound** — same use case as eventlet                   | Very similar to eventlet, slightly different library compat        |

### Decision Tree

```
Is your task CPU-heavy (computation, image resize, ML)?
  └── Yes → prefork (default), --concurrency=<num_cores>

Is your task I/O-heavy (HTTP calls, DB, waiting on APIs)?
  └── Yes, and need 100s+ concurrent tasks → eventlet or gevent
  └── Yes, but only a handful → prefork is still fine

Debugging?
  └── solo (single-threaded, single-process)
```

### Usage

```bash
# Prefork (default) — 4 worker processes
celery -A celery_app worker --pool=prefork --concurrency=4

# Eventlet — 100 green threads in one process
celery -A celery_app worker --pool=eventlet --concurrency=100

# Solo — for debugging
celery -A celery_app worker --pool=solo
```

**Practical example:** If your tasks call LLM APIs (I/O-bound), prefork with concurrency=4 runs 4 tasks using 4 processes. Eventlet with concurrency=100 runs 100 tasks in one process — they're all just _waiting_ on HTTP responses. For early-stage, prefork with moderate concurrency (4-8) is simpler and sufficient.

---

## Task Primitives — Composing Workflows

Celery provides **canvas primitives** to build complex workflows from simple tasks:

| Primitive     | What It Does                           | Example                                               |
| ------------- | -------------------------------------- | ----------------------------------------------------- |
| **`chain`**   | Run tasks sequentially, piping results | `chain(add.s(2,2), multiply.s(10))` → `(2+2)*10 = 40` |
| **`group`**   | Run tasks in parallel                  | `group(add.s(i,i) for i in range(5))` → 5 results     |
| **`chord`**   | Group + callback when all finish       | `chord(group(...))(aggregate.s())`                    |
| **`starmap`** | Map a task over argument tuples        | `add.starmap([(2,2), (4,4)])`                         |

### Signatures

- `task.s(arg)` — **signature** (partial). Receives extra args from previous task in chain.
- `task.si(arg)` — **immutable signature**. Ignores result from previous task.

---

## Error Handling & Retries

```python
@app.task(
    bind=True,
    autoretry_for=(ConnectionError,),
    retry_backoff=True,       # exponential: 1s, 2s, 4s...
    retry_jitter=True,        # randomness to prevent thundering herd
    max_retries=3
)
def fetch_url(self, url):
    response = requests.get(url)
    return response.status_code
```

Manual retry:

```python
@app.task(bind=True, max_retries=3)
def risky_task(self, data):
    try:
        process(data)
    except TransientError as exc:
        self.retry(exc=exc, countdown=60)
```

---

## Monitoring — Flower

[Flower](https://flower.readthedocs.io/) is a real-time web UI for Celery:

```bash
celery -A celery_app flower --port=5555
```

Shows: active/completed tasks per worker, execution times, success/failure rates, worker status and memory.

---

## Celery vs AWS SQS

They operate at **different levels of the stack**:

|                             | Celery                                                                           | AWS SQS                                              |
| --------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **What it is**              | Python **task framework** (workers + routing + retries + workflows + monitoring) | Managed **message queue service** (just the pipe)    |
| **Workers included?**       | Yes — `celery worker` runs your tasks                                            | No — you build consumers (Lambda, ECS, polling loop) |
| **Workflows**               | Built-in: chain, group, chord, retry with backoff                                | Build yourself, or pay for Step Functions            |
| **Broker**                  | Pluggable — Redis, RabbitMQ, or even SQS itself                                  | SQS _is_ the broker                                  |
| **Monitoring**              | Flower (free, real-time)                                                         | CloudWatch (delayed, costs at scale)                 |
| **Infra ownership**         | You manage Redis/RabbitMQ + workers                                              | AWS manages the queue, you manage consumers          |
| **Vendor lock-in**          | None — runs anywhere                                                             | AWS-locked                                           |
| **Can they work together?** | Yes — Celery supports SQS as a broker                                            | —                                                    |

### Early-Stage Recommendation: Celery + Redis

1. **Single Redis instance** = broker + result backend + cache + pub/sub (already in your stack)
2. **Zero AWS cost** — runs locally and on any VPS
3. **Batteries included** — retries, chaining, monitoring out of the box
4. **Simple deploy** — one `celery worker` process alongside your API
5. **Migration path** — swap broker to RabbitMQ or move workers to K8s later, without rewriting tasks

SQS makes sense when you're deep in AWS, want zero-ops on the queue, and are okay building workflow logic yourself.

---

## Project Structure

```
backend/celery/
├── docker-compose.yml      # Redis broker
├── requirements.txt        # celery, redis, flower, requests
├── celery_app.py           # App config + broker/backend URLs
├── tasks.py                # Example tasks (5 progressively complex)
├── run_tasks.py            # Script to trigger tasks and observe results
└── README.md               # This file
```

## Quick Start

### 1. Start Redis

```bash
docker compose up -d
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start a worker (uses gevent pool — configured in celery_app.py)

```bash
celery -A celery_app worker --loglevel=info -P gevent
```

### 4. Run the demo script

```bash
python run_tasks.py
```

### 5. (Optional) Start Flower for monitoring

```bash
celery -A celery_app flower --port=5555
```

## What Each Terminal Shows

| Terminal         | What You See                                      |
| ---------------- | ------------------------------------------------- |
| **Worker**       | Task received → executing → succeeded/failed logs |
| **run_tasks.py** | AsyncResult status changes, return values printed |
| **Flower**       | Live dashboard — task throughput, worker state    |

## Tasks in This Project

| Task                         | Concept Demonstrated                                          |
| ---------------------------- | ------------------------------------------------------------- |
| `add(x, y)`                  | Basic `@app.task`, `.delay()`, `AsyncResult`                  |
| `long_running_task(seconds)` | Async execution, state tracking (PENDING → STARTED → SUCCESS) |
| `unreliable_task()`          | `autoretry_for`, `retry_backoff`, `max_retries`               |
| `fetch_url(url)`             | Realistic I/O-bound task with error handling                  |
| `process_data(items)`        | Used in group/chord demos for parallel processing             |

## Demo Scenarios in `run_tasks.py`

1. **Basic** — `add.delay(4, 6)`, poll status, get result
2. **Long-running** — fire task, poll PENDING → STARTED → SUCCESS in a loop
3. **Chain** — `chain(add.s(2, 2), add.s(10))` — result piping
4. **Group** — `group(add.s(i, i) for i in range(5))` — parallel execution
5. **Chord** — group + callback that sums all results
6. **Error & Retry** — trigger unreliable task, watch retries in worker logs
7. **Fetch URLs** — parallel HTTP requests showcasing gevent I/O concurrency
