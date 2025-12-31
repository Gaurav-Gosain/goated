#!/usr/bin/env python3
"""Concurrency patterns using goated stdlib packages.

Demonstrates:
- Mutex and RWMutex
- WaitGroup
- Once
- Cond (condition variable)
- sync.Map
- Context for cancellation
- Queue-based channels (thread-safe)
"""

import queue
import threading
import time
from typing import Any

from goated.std import context, sync


def demo_mutex():
    """Demonstrate Mutex for mutual exclusion."""
    print("=== Mutex ===\n")

    counter = [0]
    mu = sync.Mutex()

    def increment():
        for _ in range(1000):
            mu.Lock()
            try:
                counter[0] += 1
            finally:
                mu.Unlock()

    # Run multiple threads
    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Counter after 10 threads x 1000 increments: {counter[0]}")
    print("Expected: 10000")
    print()


def demo_rwmutex():
    """Demonstrate RWMutex for read-write locking."""
    print("=== RWMutex ===\n")

    data = {"value": 0}
    rw = sync.RWMutex()
    read_count = [0]
    write_count = [0]

    def reader():
        for _ in range(100):
            rw.RLock()
            try:
                _ = data["value"]
                read_count[0] += 1
            finally:
                rw.RUnlock()
            time.sleep(0.001)

    def writer():
        for _ in range(10):
            rw.Lock()
            try:
                data["value"] += 1
                write_count[0] += 1
            finally:
                rw.Unlock()
            time.sleep(0.01)

    # Start readers and writers
    readers = [threading.Thread(target=reader) for _ in range(5)]
    writers = [threading.Thread(target=writer) for _ in range(2)]

    for t in readers + writers:
        t.start()
    for t in readers + writers:
        t.join()

    print(f"Read operations: {read_count[0]}")
    print(f"Write operations: {write_count[0]}")
    print(f"Final value: {data['value']}")
    print()


def demo_waitgroup():
    """Demonstrate WaitGroup for waiting on goroutines."""
    print("=== WaitGroup ===\n")

    wg = sync.WaitGroup()
    results = []

    def worker(id, delay):
        time.sleep(delay)
        results.append(f"Worker {id} done")
        wg.Done()

    # Start workers
    for i in range(5):
        wg.Add(1)
        t = threading.Thread(target=worker, args=(i, (5 - i) * 0.1))
        t.start()

    print("Waiting for workers...")
    wg.Wait()
    print("All workers done!")

    for result in results:
        print(f"  {result}")
    print()


def demo_once():
    """Demonstrate Once for one-time initialization."""
    print("=== Once ===\n")

    once = sync.Once()
    initialized = [False]
    init_count = [0]

    def initialize():
        init_count[0] += 1
        initialized[0] = True
        print("  Initialization function called!")

    # Call from multiple threads
    def try_init():
        once.Do(initialize)

    threads = [threading.Thread(target=try_init) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Initialized: {initialized[0]}")
    print(f"Init function call count: {init_count[0]}")
    print()


def demo_cond():
    """Demonstrate Cond (condition variable)."""
    print("=== Cond ===\n")

    mu = sync.Mutex()
    cond = sync.Cond(mu)
    ready = [False]
    data: list = [""]

    def producer():
        time.sleep(0.1)  # Simulate work
        cond.L.Lock()
        try:
            data[0] = "Hello from producer!"
            ready[0] = True
            print("  Producer: data ready, signaling...")
            cond.Signal()
        finally:
            cond.L.Unlock()

    def consumer():
        cond.L.Lock()
        try:
            while not ready[0]:
                print("  Consumer: waiting for data...")
                cond.Wait()
            print(f"  Consumer: got data: {data[0]}")
        finally:
            cond.L.Unlock()

    consumer_thread = threading.Thread(target=consumer)
    producer_thread = threading.Thread(target=producer)

    consumer_thread.start()
    time.sleep(0.05)  # Let consumer start waiting
    producer_thread.start()

    consumer_thread.join()
    producer_thread.join()
    print()


def demo_sync_map():
    """Demonstrate sync.Map for concurrent map access."""
    print("=== sync.Map ===\n")

    m = sync.Map()

    def writer(prefix, count):
        for i in range(count):
            m.Store(f"{prefix}_{i}", i * 10)

    def reader(prefix, count):
        found = 0
        for i in range(count):
            val, ok = m.Load(f"{prefix}_{i}")
            if ok:
                found += 1
        return found

    # Write from multiple threads
    writers = [
        threading.Thread(target=writer, args=("a", 100)),
        threading.Thread(target=writer, args=("b", 100)),
    ]
    for t in writers:
        t.start()
    for t in writers:
        t.join()

    # Read values
    val, ok = m.Load("a_50")
    print(f"Load('a_50'): {val}, found: {ok}")

    # LoadOrStore
    val, loaded = m.LoadOrStore("new_key", "new_value")
    print(f"LoadOrStore('new_key'): {val}, already existed: {loaded}")

    val, loaded = m.LoadOrStore("new_key", "another_value")
    print(f"LoadOrStore('new_key') again: {val}, already existed: {loaded}")

    # Delete
    m.Delete("a_0")
    val, ok = m.Load("a_0")
    print(f"After Delete - Load('a_0'): {val}, found: {ok}")

    # Range
    print("\nFirst 5 entries:")
    count = [0]

    def print_entry(key, value):
        if count[0] < 5:
            print(f"  {key}: {value}")
            count[0] += 1
            return True
        return False

    m.Range(print_entry)
    print()


def demo_context_cancel():
    """Demonstrate context for cancellation."""
    print("=== Context Cancellation ===\n")

    # Create cancellable context
    ctx, cancel = context.WithCancel(context.Background())

    work_done = [0]
    stopped = [False]

    def worker():
        while not stopped[0]:
            # Check context error
            err = ctx.Err()
            if err:
                print(f"  Worker: context cancelled: {err}")
                return

            work_done[0] += 1
            if work_done[0] >= 5:
                print(f"  Worker: completed {work_done[0]} tasks")
                return
            time.sleep(0.1)

    t = threading.Thread(target=worker)
    t.start()

    time.sleep(0.25)  # Let worker do some work
    print("Main: cancelling context...")
    cancel()
    stopped[0] = True

    t.join()
    print(f"Work completed: {work_done[0]}")
    print()


def demo_context_timeout():
    """Demonstrate context with timeout."""
    print("=== Context Timeout ===\n")

    # Create context with timeout
    ctx, cancel = context.WithTimeout(context.Background(), 0.3)

    def long_operation():
        for i in range(10):
            err = ctx.Err()
            if err:
                print(f"  Operation interrupted at step {i}: {err}")
                return
            print(f"  Step {i}...")
            time.sleep(0.1)
        print("  Operation completed!")

    t = threading.Thread(target=long_operation)
    t.start()
    t.join()

    cancel()  # Clean up
    print()


def demo_context_value():
    """Demonstrate context with values."""
    print("=== Context Values ===\n")

    # Create context with value
    ctx = context.Background()
    ctx = context.WithValue(ctx, "request_id", "req-12345")
    ctx = context.WithValue(ctx, "user_id", "user-42")

    def handler():
        req_id = ctx.Value("request_id")
        user_id = ctx.Value("user_id")
        missing = ctx.Value("missing_key")

        print(f"  Request ID: {req_id}")
        print(f"  User ID: {user_id}")
        print(f"  Missing key: {missing}")

    handler()
    print()


# Simple thread-safe channel using queue.Queue
class Chan:
    """Simple Go-like channel using queue.Queue."""

    def __init__(self, size: int = 0):
        self._queue: queue.Queue = queue.Queue(maxsize=size if size > 0 else 1)
        self._closed = False
        self._unbuffered = size == 0

    def send(self, value: Any) -> None:
        if self._closed:
            raise RuntimeError("send on closed channel")
        self._queue.put(value)

    def recv(self, block: bool = True, timeout: float | None = None) -> Any:
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty:
            raise queue.Empty("channel empty or timeout")

    def close(self) -> None:
        self._closed = True

    @property
    def closed(self) -> bool:
        return self._closed


def make_chan(size: int = 0) -> Chan:
    """Create a new channel."""
    return Chan(size)


def demo_channels():
    """Demonstrate Go-like channels using queue."""
    print("=== Channels (Queue-based) ===\n")

    # Unbuffered-like channel (size=1)
    ch = make_chan(1)

    def sender():
        for i in range(5):
            ch.send(i)
            print(f"  Sent: {i}")
        ch.close()

    def receiver():
        while not ch.closed:
            try:
                val = ch.recv(timeout=0.5)
                print(f"  Received: {val}")
            except queue.Empty:
                if ch.closed:
                    break
        print("  Channel closed")

    t1 = threading.Thread(target=sender)
    t2 = threading.Thread(target=receiver)

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print()


def demo_buffered_channel():
    """Demonstrate buffered channels."""
    print("=== Buffered Channel ===\n")

    # Buffered channel with capacity 3
    ch = make_chan(3)

    # Can send without blocking (up to capacity)
    ch.send("a")
    ch.send("b")
    ch.send("c")
    print("Sent 3 items without blocking")

    # Receive
    for _ in range(3):
        val = ch.recv()
        print(f"  Received: {val}")
    print()


def demo_worker_pool():
    """Demonstrate worker pool pattern."""
    print("=== Worker Pool Pattern ===\n")

    jobs = make_chan(10)
    results = make_chan(10)
    wg = sync.WaitGroup()
    stop_workers = [False]

    def worker(id):
        while not stop_workers[0]:
            try:
                job = jobs.recv(timeout=0.1)
                print(f"  Worker {id} processing job {job}")
                time.sleep(0.05)
                results.send(f"Result of job {job}")
                wg.Done()
            except queue.Empty:
                if jobs.closed:
                    break
        print(f"  Worker {id} stopping")

    # Start workers
    num_workers = 3
    worker_threads = []
    for i in range(num_workers):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        worker_threads.append(t)

    # Send jobs
    num_jobs = 9
    for j in range(num_jobs):
        wg.Add(1)
        jobs.send(j)

    # Wait for completion
    wg.Wait()
    jobs.close()
    stop_workers[0] = True

    for t in worker_threads:
        t.join()

    # Collect results
    print("\nResults:")
    for _ in range(num_jobs):
        try:
            result = results.recv(block=False)
            print(f"  {result}")
        except queue.Empty:
            break
    print()


def demo_fan_out_fan_in():
    """Demonstrate fan-out/fan-in pattern."""
    print("=== Fan-Out / Fan-In Pattern ===\n")

    # Input channel
    input_ch = make_chan(10)

    # Output channels from workers
    output_chs = [make_chan(10) for _ in range(3)]

    # Merged output
    merged = make_chan(30)

    def producer():
        for i in range(9):
            input_ch.send(i)
        input_ch.close()

    def worker(id, out_ch):
        while True:
            try:
                val = input_ch.recv(timeout=0.1)
                result = f"Worker {id} processed {val}"
                out_ch.send(result)
            except queue.Empty:
                if input_ch.closed:
                    break
        out_ch.close()

    def merger():
        for ch in output_chs:
            while True:
                try:
                    val = ch.recv(timeout=0.1)
                    merged.send(val)
                except queue.Empty:
                    if ch.closed:
                        break

    # Start producer
    producer_t = threading.Thread(target=producer)
    producer_t.start()

    # Start workers (fan-out)
    worker_threads = []
    for i, ch in enumerate(output_chs):
        t = threading.Thread(target=worker, args=(i, ch))
        t.start()
        worker_threads.append(t)

    producer_t.join()
    for t in worker_threads:
        t.join()

    # Merge results (fan-in)
    merger()

    # Print results
    print("Merged results:")
    while True:
        try:
            result = merged.recv(block=False)
            print(f"  {result}")
        except queue.Empty:
            break
    print()


def main():
    print("=" * 60)
    print("  goated - Concurrency Patterns")
    print("=" * 60)
    print()

    demo_mutex()
    demo_rwmutex()
    demo_waitgroup()
    demo_once()
    demo_cond()
    demo_sync_map()
    demo_context_cancel()
    demo_context_timeout()
    demo_context_value()
    demo_channels()
    demo_buffered_channel()
    demo_worker_pool()
    demo_fan_out_fan_in()

    print("=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
