"""
Celery Application Configuration

Creates the Celery app instance with Redis as both broker and result backend.
Uses gevent pool for I/O-bound task concurrency.
"""

from celery import Celery

app = Celery("demo")

app.config_from_object({
    # --- Broker & Backend ---
    "broker_url": "redis://localhost:6379/0",
    "result_backend": "redis://localhost:6379/0",

    # --- Serialisation ---
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],

    # --- Worker ---
    "worker_pool": "gevent",             # Use gevent green threads instead of prefork
    "worker_concurrency": 20,            # 20 concurrent green threads per worker
    "worker_prefetch_multiplier": 1,     # Fetch one task at a time (fair scheduling)

    # --- Task behaviour ---
    "task_track_started": True,          # Enables STARTED state (default only has PENDING/SUCCESS/FAILURE)
    "task_acks_late": True,              # ACK after execution (requeue on crash)
    "result_expires": 3600,              # Results expire after 1 hour

    # --- Task discovery ---
    "include": ["tasks"],
})
