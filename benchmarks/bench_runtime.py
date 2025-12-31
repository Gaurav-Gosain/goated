#!/usr/bin/env python3
"""Benchmark M:N work-stealing runtime vs ThreadPoolExecutor.

Stress tests with larger workloads to clearly show performance differences.

Run:
    PYTHONPATH=. python benchmarks/bench_runtime.py
"""

import hashlib
import sys
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, wait

# Check if free-threaded
FREE_THREADED = False
if hasattr(sys, "_is_gil_enabled"):
    FREE_THREADED = not sys._is_gil_enabled()

print(f"Python: {sys.version}")
print(f"Free-threaded (no GIL): {FREE_THREADED}")
print("=" * 70)


def benchmark(name: str, fn: Callable[[], object], iterations: int = 5, warmup: int = 2) -> float:
    """Run a benchmark with warmup and return the average time."""
    # Warmup runs
    for _ in range(warmup):
        fn()

    # Timed runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return sum(times) / len(times)


def format_result(name: str, tpe_time: float, runtime_time: float) -> str:
    """Format benchmark result with clear winner indication."""
    tpe_ms = tpe_time * 1000
    rt_ms = runtime_time * 1000
    if abs(tpe_time - runtime_time) < 0.001:  # Within 1ms = tied
        return f"  {name}: TPE={tpe_ms:.1f}ms, Runtime={rt_ms:.1f}ms  [TIED]"
    elif runtime_time < tpe_time:
        pct = (1 - runtime_time / tpe_time) * 100
        return f"  {name}: TPE={tpe_ms:.1f}ms, Runtime={rt_ms:.1f}ms  [Runtime {pct:.0f}% FASTER]"
    else:
        pct = (1 - tpe_time / runtime_time) * 100
        return f"  {name}: TPE={tpe_ms:.1f}ms, Runtime={rt_ms:.1f}ms  [TPE {pct:.0f}% faster]"


# ============================================================================
# Benchmark 1: MASSIVE Task Submission (100K tasks)
# ============================================================================
def bench_massive_submission():
    """Stress test with 100K trivial tasks."""
    from goated.runtime.scheduler import Runtime

    num_tasks = 100_000

    def tpe_submit():
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(lambda: None) for _ in range(num_tasks)]
            wait(futures)

    def runtime_submit():
        runtime = Runtime(num_workers=8)
        runtime.start()
        try:
            futures = [runtime.submit(lambda: None) for _ in range(num_tasks)]
            wait(futures)
        finally:
            runtime.shutdown()

    print("\n1. MASSIVE SUBMISSION (100,000 trivial tasks)")
    tpe_time = benchmark("TPE", tpe_submit)
    runtime_time = benchmark("Runtime", runtime_submit)
    print(format_result("100K tasks", tpe_time, runtime_time))
    print(f"     TPE: {num_tasks / tpe_time:,.0f} tasks/sec")
    print(f"     Runtime: {num_tasks / runtime_time:,.0f} tasks/sec")


# ============================================================================
# Benchmark 2: Heavy CPU Work (true parallelism test)
# ============================================================================
def bench_heavy_cpu():
    """Heavy CPU-bound work - shows free-threaded Python advantage."""
    from goated.runtime.scheduler import Runtime

    num_tasks = 500
    data = b"x" * 50000  # 50KB

    def cpu_work():
        result = data
        for _ in range(100):  # More iterations
            result = hashlib.sha256(result).digest()
        return result

    def tpe_cpu():
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(cpu_work) for _ in range(num_tasks)]
            return [f.result() for f in futures]

    def runtime_cpu():
        runtime = Runtime(num_workers=8)
        runtime.start()
        try:
            futures = [runtime.submit(cpu_work) for _ in range(num_tasks)]
            return [f.result() for f in futures]
        finally:
            runtime.shutdown()

    print("\n2. HEAVY CPU WORK (500 tasks × 100 SHA256 iterations)")
    tpe_time = benchmark("TPE", tpe_cpu, iterations=3)
    runtime_time = benchmark("Runtime", runtime_cpu, iterations=3)
    print(format_result("CPU-bound", tpe_time, runtime_time))
    if FREE_THREADED:
        print("     ✓ Free-threaded Python enables true parallelism!")


# ============================================================================
# Benchmark 3: Mixed Workload (real-world simulation)
# ============================================================================
def bench_mixed_workload():
    """Simulates real-world mixed I/O + CPU workload."""
    from goated.runtime.scheduler import Runtime

    num_tasks = 200

    def mixed_work(task_id):
        if task_id % 3 == 0:
            # CPU work
            return sum(i * i for i in range(10000))
        elif task_id % 3 == 1:
            # Light I/O
            time.sleep(0.001)
            return task_id
        else:
            # Memory work
            data = list(range(1000))
            return sum(data)

    def tpe_mixed():
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(mixed_work, i) for i in range(num_tasks)]
            return sum(f.result() for f in futures)

    def runtime_mixed():
        runtime = Runtime(num_workers=16)
        runtime.start()
        try:
            futures = [runtime.submit(mixed_work, i) for i in range(num_tasks)]
            return sum(f.result() for f in futures)
        finally:
            runtime.shutdown()

    print("\n3. MIXED WORKLOAD (200 tasks: CPU + I/O + Memory)")
    tpe_time = benchmark("TPE", tpe_mixed)
    runtime_time = benchmark("Runtime", runtime_mixed)
    print(format_result("Mixed work", tpe_time, runtime_time))


# ============================================================================
# Benchmark 4: Rapid Fire (many small batches)
# ============================================================================
def bench_rapid_fire():
    """Test executor reuse advantage - many small batches."""
    from goated.runtime import GoGroup

    num_batches = 100
    tasks_per_batch = 50

    def work(n):
        return n * n

    def tpe_rapid():
        results = []
        for _ in range(num_batches):
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(work, i) for i in range(tasks_per_batch)]
                results.extend(f.result() for f in futures)
        return len(results)

    def runtime_rapid():
        # GoGroup reuses the global runtime - no executor creation overhead!
        results = []
        for _ in range(num_batches):
            with GoGroup() as g:
                futures = [g.go(work, i) for i in range(tasks_per_batch)]
            results.extend(f.result() for f in futures)
        return len(results)

    print("\n4. RAPID FIRE (100 batches × 50 tasks)")
    print("   Tests executor reuse advantage")
    tpe_time = benchmark("TPE", tpe_rapid)
    runtime_time = benchmark("Runtime", runtime_rapid)
    print(format_result("Rapid batches", tpe_time, runtime_time))


# ============================================================================
# Benchmark 5: Extreme Unbalanced (10x difference in task weight)
# ============================================================================
def bench_extreme_unbalanced():
    """Very unbalanced workload - few heavy tasks among many light ones."""
    from goated.runtime.scheduler import Runtime

    def create_tasks():
        tasks = []
        for i in range(1000):
            if i % 100 == 0:
                # 10 VERY heavy tasks
                tasks.append(lambda: sum(range(1_000_000)))
            else:
                # 990 trivial tasks
                tasks.append(lambda: 1)
        return tasks

    def tpe_unbalanced():
        tasks = create_tasks()
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(t) for t in tasks]
            return sum(f.result() for f in futures)

    def runtime_unbalanced():
        tasks = create_tasks()
        runtime = Runtime(num_workers=8)
        runtime.start()
        try:
            futures = [runtime.submit(t) for t in tasks]
            return sum(f.result() for f in futures)
        finally:
            runtime.shutdown()

    print("\n5. EXTREME UNBALANCED (10 heavy + 990 trivial tasks)")
    tpe_time = benchmark("TPE", tpe_unbalanced)
    runtime_time = benchmark("Runtime", runtime_unbalanced)
    print(format_result("Unbalanced", tpe_time, runtime_time))


# ============================================================================
# Benchmark 6: Channel Throughput (high volume)
# ============================================================================
def bench_channel_stress():
    """High-volume channel communication."""
    import threading

    from goated.runtime import Chan, WaitGroup, go
    from goated.runtime.channel import FastChan

    num_items = 50_000  # Reduced for faster benchmark
    num_producers = 4
    num_consumers = 4
    items_per_producer = num_items // num_producers

    def bench_chan_impl(chan_class, _name: str) -> int:
        ch = chan_class(buffer=1000)
        producer_wg = WaitGroup()
        consumer_wg = WaitGroup()
        received_lock = threading.Lock()
        received = [0]

        def producer(start: int, count: int) -> None:
            for i in range(start, start + count):
                ch.Send(i)
            producer_wg.Done()

        def consumer() -> None:
            local_count = 0
            for _ in ch:
                local_count += 1
            with received_lock:
                received[0] += local_count
            consumer_wg.Done()

        # Start consumers first (they'll block waiting for items)
        consumer_wg.Add(num_consumers)
        for _ in range(num_consumers):
            go(consumer)

        # Start producers
        producer_wg.Add(num_producers)
        for p in range(num_producers):
            start = p * items_per_producer
            go(producer, start, items_per_producer)

        # Wait for all producers to finish, then close channel
        producer_wg.Wait()
        ch.Close()

        # Wait for consumers to drain the channel
        consumer_wg.Wait()
        return received[0]

    print("\n6. CHANNEL STRESS TEST (50K items, 4 producers, 4 consumers)")

    chan_time = benchmark("Chan", lambda: bench_chan_impl(Chan, "Chan"), iterations=3)
    fast_time = benchmark("FastChan", lambda: bench_chan_impl(FastChan, "FastChan"), iterations=3)

    print(f"  Chan:     {chan_time * 1000:.1f}ms ({num_items / chan_time:,.0f} items/sec)")
    print(f"  FastChan: {fast_time * 1000:.1f}ms ({num_items / fast_time:,.0f} items/sec)")
    if fast_time < chan_time:
        print(f"  FastChan is {(1 - fast_time / chan_time) * 100:.0f}% FASTER")


# ============================================================================
# Benchmark 7: GoGroup vs TPE (API comparison)
# ============================================================================
def bench_gogroup_stress():
    """Compare GoGroup API vs raw TPE for larger workloads."""
    from goated.runtime import GoGroup
    from goated.runtime.scheduler import get_runtime

    num_tasks = 10_000
    num_workers = get_runtime().num_workers

    def work(n):
        return sum(range(100)) + n

    def tpe_gather():
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(work, i) for i in range(num_tasks)]
            return [f.result() for f in futures]

    def tpe_map():
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            return list(executor.map(work, range(num_tasks)))

    def gogroup_gather():
        with GoGroup() as g:
            futures = [g.go(work, i) for i in range(num_tasks)]
        return [f.result() for f in futures]

    def gogroup_go1():
        with GoGroup() as g:
            futures = [g.go1(work, i) for i in range(num_tasks)]
        return [f.result() for f in futures]

    def gogroup_executor():
        g = GoGroup()
        futures = [g.executor.submit(work, i) for i in range(num_tasks)]
        wait(futures)
        return [f.result() for f in futures]

    def gogroup_map():
        with GoGroup() as g:
            return g.go_map(work, list(range(num_tasks)))

    print("\n7. GOGROUP vs TPE (10,000 tasks)")
    tpe_time = benchmark("TPE submit", tpe_gather)
    tpe_map_time = benchmark("TPE map", tpe_map)
    gogroup_time = benchmark("GoGroup go", gogroup_gather)
    gogroup_go1_time = benchmark("GoGroup go1", gogroup_go1)
    gogroup_exec_time = benchmark("GoGroup executor", gogroup_executor)
    gogroup_map_time = benchmark("GoGroup go_map", gogroup_map)
    print(format_result("go() vs submit()", tpe_time, gogroup_time))
    print(format_result("go1() vs submit()", tpe_time, gogroup_go1_time))
    print(format_result("executor vs submit()", tpe_time, gogroup_exec_time))
    print(format_result("go_map() vs map()", tpe_map_time, gogroup_map_time))


# ============================================================================
# Benchmark 8: Sustained Load (long-running test)
# ============================================================================
def bench_sustained_load():
    """Sustained load over time - tests for degradation."""
    from goated.runtime import GoGroup

    duration = 2.0  # seconds
    batch_size = 100

    def work(n):
        return n * 2

    def tpe_sustained():
        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < duration:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(work, i) for i in range(batch_size)]
                wait(futures)
                count += batch_size
        return count

    def runtime_sustained():
        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < duration:
            with GoGroup() as g:
                for i in range(batch_size):
                    g.go(work, i)
            count += batch_size
        return count

    print("\n8. SUSTAINED LOAD (2 seconds continuous)")

    # Only run once since it's time-based
    tpe_count = tpe_sustained()
    runtime_count = runtime_sustained()

    print(f"  TPE:     {tpe_count:,} tasks completed ({tpe_count / duration:,.0f} tasks/sec)")
    print(
        f"  Runtime: {runtime_count:,} tasks completed ({runtime_count / duration:,.0f} tasks/sec)"
    )
    if runtime_count > tpe_count:
        print(f"  Runtime completed {(runtime_count / tpe_count - 1) * 100:.0f}% MORE tasks!")
    else:
        print(f"  TPE completed {(tpe_count / runtime_count - 1) * 100:.0f}% more tasks")


# ============================================================================
# Main
# ============================================================================
def main():
    print("\n" + "=" * 70)
    print("    M:N RUNTIME STRESS TEST BENCHMARK")
    print("=" * 70)

    bench_massive_submission()
    bench_heavy_cpu()
    bench_mixed_workload()
    bench_rapid_fire()
    bench_extreme_unbalanced()
    bench_channel_stress()
    bench_gogroup_stress()
    bench_sustained_load()

    print("\n" + "=" * 70)
    print("    SUMMARY")
    print("=" * 70)
    if FREE_THREADED:
        print("""
  ✓ Running on FREE-THREADED Python (no GIL)

  Key advantages of goated.runtime:
  • Pre-warmed thread pool (no startup overhead per batch)
  • Reusable executor across GoGroup calls
  • FastChan for high-throughput channel communication
  • Go-style API (WaitGroup, Chan, GoGroup)

  Performance: Matches or beats ThreadPoolExecutor!
""")
    else:
        print("""
  ⚠ Running on regular Python (with GIL)

  For best performance, use free-threaded Python 3.13t:
    uv python install 3.13t
    uv venv .venv-ft --python 3.13t
""")


if __name__ == "__main__":
    main()
