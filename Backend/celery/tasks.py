"""
Task Definitions — 5 progressively complex examples

Each task demonstrates a different Celery concept.
Run these via run_tasks.py or manually in a Python shell.
"""

import time
import random

import requests
from celery import shared_task
from celery_app import app


# ---------------------------------------------------------------------------
# 1. Basic Task — simplest possible task
# ---------------------------------------------------------------------------
@app.task
def add(x, y):
    """Returns x + y. Demonstrates @app.task and .delay()."""
    return x + y


# ---------------------------------------------------------------------------
# 2. Long-Running Task — async execution & state tracking
# ---------------------------------------------------------------------------
@app.task(bind=True)
def long_running_task(self, seconds):
    """
    Simulates a long-running job by sleeping in 1-second increments.
    Updates task metadata so you can poll progress from run_tasks.py.
    
    `bind=True` gives us `self` — the task instance — so we can call
    self.update_state() to report progress.
    """
    for i in range(seconds):
        time.sleep(1)
        self.update_state(
            state="PROGRESS",
            meta={"current": i + 1, "total": seconds}
        )
    return {"status": "complete", "seconds_elapsed": seconds}


# ---------------------------------------------------------------------------
# 3. Unreliable Task — retry with exponential backoff
# ---------------------------------------------------------------------------
@app.task(
    bind=True,
    autoretry_for=(RuntimeError,),
    retry_backoff=True,          # 1s, 2s, 4s, 8s...
    retry_backoff_max=30,        # cap backoff at 30s
    retry_jitter=True,           # add randomness to prevent thundering herd
    max_retries=3,
)
def unreliable_task(self):
    """
    Randomly fails ~60% of the time to demonstrate automatic retries.
    Watch the worker logs to see retry attempts with increasing delays.
    """
    if random.random() < 0.6:
        raise RuntimeError(f"Random failure on attempt {self.request.retries + 1}")
    return f"Succeeded on attempt {self.request.retries + 1}"


# ---------------------------------------------------------------------------
# 4. Fetch URL — realistic I/O-bound task
# ---------------------------------------------------------------------------
@app.task(
    bind=True,
    autoretry_for=(requests.ConnectionError, requests.Timeout),
    retry_backoff=True,
    max_retries=3,
    soft_time_limit=10,          # raises SoftTimeLimitExceeded after 10s
)
def fetch_url(self, url):
    """
    Makes an HTTP GET request — a realistic I/O-bound task.
    This is the type of work where gevent shines: while one green thread
    waits on the HTTP response, others can execute.
    """
    response = requests.get(url, timeout=5)
    return {
        "url": url,
        "status_code": response.status_code,
        "content_length": len(response.content),
    }


# ---------------------------------------------------------------------------
# 5. Process Data — used in group/chord demos
# ---------------------------------------------------------------------------
@app.task
def process_data(item):
    """
    Simulates processing a single item (e.g., resize one image, index one doc).
    Sleeps briefly to mimic work. Used in group/chord demos in run_tasks.py.
    """
    time.sleep(0.5)
    return {"item": item, "result": item * 2}


@app.task
def aggregate_results(results):
    """
    Callback for chord — receives a list of all results from a group.
    Sums up the processed values.
    """
    total = sum(r["result"] for r in results)
    return {"total": total, "count": len(results)}
