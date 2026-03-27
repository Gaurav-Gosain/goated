"""Advanced concurrency: pipelines, fan-out, semaphores.

Demonstrates the new concurrency primitives added in v0.2.0:
pipe(), merge(), fan_out(), and Semaphore.
"""

import time

from goated.runtime import Chan, GoGroup, Semaphore, fan_out, go, merge, pipe

# ---------------------------------------------------------------------------
# 1. Pipeline: transform values through stages
# ---------------------------------------------------------------------------
print("=== Pipeline with pipe() ===")

src = Chan[int](buffer=10)

# Build a pipeline: src -> double -> to_string -> output
doubled = pipe(src, lambda x: x * 2, buffer=10)
stringed = pipe(doubled, lambda x: f"value={x}", buffer=10)

# Feed the source
def feed():
    for i in range(5):
        src.Send(i)
    src.Close()

go(feed)

# Consume the pipeline output
for item in stringed:
    print(f"  {item}")

# ---------------------------------------------------------------------------
# 2. Fan-out: distribute work across N workers
# ---------------------------------------------------------------------------
print("\n=== Fan-out ===")

src2 = Chan[int](buffer=20)
outputs = fan_out(src2, n=3, buffer=10)

# Feed work items
def feed_work():
    for i in range(9):
        src2.Send(i)
    src2.Close()

go(feed_work)

# Each output channel gets a round-robin share of values
for idx, out_ch in enumerate(outputs):
    values = list(out_ch)
    print(f"  Worker {idx} received: {values}")

# ---------------------------------------------------------------------------
# 3. Merge: combine multiple channels into one
# ---------------------------------------------------------------------------
print("\n=== Merge (fan-in) ===")

ch1 = Chan[str](buffer=5)
ch2 = Chan[str](buffer=5)
ch3 = Chan[str](buffer=5)

def send_and_close(ch, prefix, count):
    for i in range(count):
        ch.Send(f"{prefix}-{i}")
    ch.Close()

go(send_and_close, ch1, "alpha", 3)
go(send_and_close, ch2, "beta", 3)
go(send_and_close, ch3, "gamma", 3)

combined = merge(ch1, ch2, ch3, buffer=10)
results = sorted(list(combined))
print(f"  Merged {len(results)} values: {results}")

# ---------------------------------------------------------------------------
# 4. Semaphore: limit concurrent operations
# ---------------------------------------------------------------------------
print("\n=== Semaphore (concurrency limiter) ===")

sem = Semaphore(3)  # Allow only 3 concurrent operations
active = []
max_concurrent = [0]
lock = __import__("threading").Lock()

def rate_limited_task(task_id):
    with sem:
        with lock:
            active.append(task_id)
            if len(active) > max_concurrent[0]:
                max_concurrent[0] = len(active)
        time.sleep(0.05)  # Simulate work
        with lock:
            active.remove(task_id)

with GoGroup() as g:
    for i in range(12):
        g.go(rate_limited_task, i)

print(f"  Ran 12 tasks with max concurrency = {max_concurrent[0]} (limit was 3)")

# ---------------------------------------------------------------------------
# 5. Putting it all together: pipeline with bounded concurrency
# ---------------------------------------------------------------------------
print("\n=== Combined: bounded pipeline ===")

src3 = Chan[int](buffer=20)
sem2 = Semaphore(4)
results_ch = Chan[str](buffer=20)

def bounded_worker(x):
    with sem2:
        time.sleep(0.01)  # Simulate I/O
        return f"processed-{x}"

processed = pipe(src3, bounded_worker, buffer=20, workers=4)

def feed_pipeline():
    for i in range(10):
        src3.Send(i)
    src3.Close()

go(feed_pipeline)

output = list(processed)
print(f"  Processed {len(output)} items: {output[:5]}...")
print("  Done.")
