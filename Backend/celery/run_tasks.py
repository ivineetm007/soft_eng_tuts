"""
Demo Runner — triggers tasks and prints results

Run this AFTER starting Redis and a worker:
    Terminal 1:  docker compose up -d
    Terminal 2:  celery -A celery_app worker --loglevel=info
    Terminal 3:  python run_tasks.py
"""

import time
from celery import chain, group, chord
from tasks import add, long_running_task, unreliable_task, fetch_url, process_data, aggregate_results


def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Demo 1: Basic Task
# ---------------------------------------------------------------------------
def demo_basic():
    separator("Demo 1: Basic Task — add(4, 6)")

    result = add.delay(4, 6)# AysncResult
    print(result)
    # print(f"Task ID:  {result.id}")
    # print(f"Status:   {result.status}")     # PENDING — hasn't been picked up yet

    value = result.get(timeout=10)           # Block until result is ready
    print(value)# AsyncResult gets value automatically
    # print(f"Status:   {result.status}")      # SUCCESS
    # print(f"Result:   {value}")              # 10


# ---------------------------------------------------------------------------
# Demo 2: Long-Running Task with Progress Polling
# ---------------------------------------------------------------------------
def demo_long_running():
    separator("Demo 2: Long-Running Task — 5 seconds with progress")

    result = long_running_task.delay(5)
    print(f"Task ID: {result.id}")

    while not result.ready():
        meta = result.info
        if isinstance(meta, dict) and "current" in meta:
            print(f"  Progress: {meta['current']}/{meta['total']}")
        else:
            print(f"  Status: {result.status}")
        time.sleep(1)

    print(f"Final status: {result.status}")
    print(f"Result: {result.get()}")


# ---------------------------------------------------------------------------
# Demo 3: Chain — sequential task pipeline
# ---------------------------------------------------------------------------
def demo_chain():
    separator("Demo 3: Chain — add(2,2) then add(result, 10)")

    # chain pipes the result of each task into the next
    # add(2,2) = 4 → add(4, 10) = 14
    pipeline = chain(add.s(2, 2), add.s(10))
    result = pipeline.apply_async()

    value = result.get(timeout=10)
    print(f"Chain result: {value}")   # 14


# ---------------------------------------------------------------------------
# Demo 4: Group — parallel execution
# ---------------------------------------------------------------------------
def demo_group():
    separator("Demo 4: Group — process 5 items in parallel")

    # Runs 5 tasks concurrently, each processing one item
    task_group = group(process_data.s(i) for i in range(1, 6))
    result = task_group.apply_async()

    values = result.get(timeout=30)
    for v in values:
        print(f"  Item {v['item']} → result {v['result']}")


# ---------------------------------------------------------------------------
# Demo 5: Chord — group + callback
# ---------------------------------------------------------------------------
def demo_chord():
    separator("Demo 5: Chord — parallel process + aggregate")

    # Run process_data on items 1-5 in parallel, then aggregate all results
    callback = aggregate_results.s()
    task_chord = chord(
        group(process_data.s(i) for i in range(1, 6)),
        callback
    )
    result = task_chord.apply_async()

    value = result.get(timeout=30)
    print(f"Aggregated: {value}")
    # Expected: total = (1*2 + 2*2 + 3*2 + 4*2 + 5*2) = 30, count = 5


# ---------------------------------------------------------------------------
# Demo 6: Error Handling & Retries
# ---------------------------------------------------------------------------
def demo_retry():
    separator("Demo 6: Unreliable Task — watch retries in worker logs")

    result = unreliable_task.delay()
    print(f"Task ID: {result.id}")
    print("Watch the WORKER terminal for retry attempts...")
    print("Waiting up to 60 seconds for final result...\n")

    try:
        value = result.get(timeout=60)
        print(f"Final status: {result.status}")
        print(f"Result: {value}")
    except Exception as exc:
        print(f"Task failed after all retries: {exc}")


# ---------------------------------------------------------------------------
# Demo 7: Fetch URLs — gevent I/O concurrency in action
# ---------------------------------------------------------------------------
def demo_fetch_urls():
    separator("Demo 7: Fetch URLs — gevent handles concurrent I/O")

    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/200",
        "https://httpbin.org/ip",
    ]

    # Fire all fetch tasks in parallel as a group
    task_group = group(fetch_url.s(url) for url in urls)
    result = task_group.apply_async()

    print(f"Fired {len(urls)} HTTP fetch tasks in parallel...")
    values = result.get(timeout=30)

    for v in values:
        print(f"  {v['url']} → {v['status_code']} ({v['content_length']} bytes)")


# ---------------------------------------------------------------------------
# Run all demos
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n🚀 Celery Demo Runner")
    print("Make sure Redis is running and a worker is started.\n")

    demo_basic()
    # demo_long_running()
    # demo_chain()
    # demo_group()
    # demo_chord()
    # demo_retry()
    # demo_fetch_urls()

    print(f"\n{'='*60}")
    print("  ✅ All demos finished!")
    print(f"{'='*60}\n")
