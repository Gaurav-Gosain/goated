#!/usr/bin/env python3
"""Benchmarks for goated concurrency primitives.

Compares:
- GoGroup vs manual threading
- ErrGroup vs concurrent.futures
- parallel_map vs ThreadPoolExecutor.map
- Channels vs queue.Queue
- Mutex vs threading.Lock

Run with: python benchmarks/bench_concurrency.py
"""

import queue
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from goated.std.goroutine import (
    Chan,
    ErrGroup,
    GoGroup,
    Mutex,
    WaitGroup,
    go,
    parallel_map,
)


class BenchmarkResult:
    def __init__(self, name: str, goated_time: float, baseline_time: float, unit: str = "ms"):
        self.name = name
        self.goated_time = goated_time
        self.baseline_time = baseline_time
        self.unit = unit
        self.speedup = baseline_time / goated_time if goated_time > 0 else 0

    def __str__(self):
        winner = "GOATED" if self.speedup >= 1 else "BASELINE"
        speedup_str = (
            f"{self.speedup:.2f}x" if self.speedup >= 1 else f"{1 / self.speedup:.2f}x slower"
        )
        return (
            f"{self.name:<40} {self.goated_time:>8.2f}{self.unit}  "
            f"{self.baseline_time:>8.2f}{self.unit}  {speedup_str:>12} ({winner})"
        )


def benchmark(func: Callable, iterations: int = 1) -> float:
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    return (time.perf_counter() - start) * 1000 / iterations


def work_unit(duration: float = 0.001):
    time.sleep(duration)
    return 42


def cpu_work(n: int = 1000) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total


def bench_gogroup_vs_threadpool():
    print("\n" + "=" * 80)
    print("BENCHMARK: GoGroup vs ThreadPoolExecutor")
    print("=" * 80)

    results = []

    for num_tasks in [10, 50, 100, 500]:

        def goated_version(n=num_tasks):
            with GoGroup() as g:
                for _ in range(n):
                    g.go(cpu_work, 100)

        def baseline_version(n=num_tasks):
            with ThreadPoolExecutor(max_workers=32) as executor:
                futures = [executor.submit(cpu_work, 100) for _ in range(n)]
                for f in as_completed(futures):
                    f.result()

        goated_time = benchmark(goated_version, 3)
        baseline_time = benchmark(baseline_version, 3)

        results.append(
            BenchmarkResult(f"Spawn {num_tasks} tasks (CPU work)", goated_time, baseline_time)
        )

    print(f"\n{'Operation':<40} {'Goated':>10}  {'Baseline':>10}  {'Speedup':>12}")
    print("-" * 80)
    for r in results:
        print(r)


def bench_parallel_map_vs_executor_map():
    print("\n" + "=" * 80)
    print("BENCHMARK: parallel_map vs ThreadPoolExecutor.map")
    print("=" * 80)

    results = []

    for size in [100, 500, 1000]:
        items = list(range(size))

        def goated_version(it=items):
            return parallel_map(cpu_work, it)

        def baseline_version(it=items):
            with ThreadPoolExecutor(max_workers=32) as executor:
                return list(executor.map(cpu_work, it))

        goated_time = benchmark(goated_version, 3)
        baseline_time = benchmark(baseline_version, 3)

        results.append(BenchmarkResult(f"parallel_map {size} items", goated_time, baseline_time))

    print(f"\n{'Operation':<40} {'Goated':>10}  {'Baseline':>10}  {'Speedup':>12}")
    print("-" * 80)
    for r in results:
        print(r)


def bench_errgroup_vs_futures():
    print("\n" + "=" * 80)
    print("BENCHMARK: ErrGroup vs concurrent.futures (with error handling)")
    print("=" * 80)

    results = []

    for num_tasks in [10, 50, 100]:

        def goated_version(n=num_tasks):
            with ErrGroup() as g:
                for _ in range(n):
                    g.go(cpu_work, 100)

        def baseline_version(n=num_tasks):
            with ThreadPoolExecutor(max_workers=32) as executor:
                futures = [executor.submit(cpu_work, 100) for _ in range(n)]
                for f in as_completed(futures):
                    f.result()

        goated_time = benchmark(goated_version, 3)
        baseline_time = benchmark(baseline_version, 3)

        results.append(BenchmarkResult(f"ErrGroup {num_tasks} tasks", goated_time, baseline_time))

    print(f"\n{'Operation':<40} {'Goated':>10}  {'Baseline':>10}  {'Speedup':>12}")
    print("-" * 80)
    for r in results:
        print(r)


def bench_channel_vs_queue():
    print("\n" + "=" * 80)
    print("BENCHMARK: Chan vs queue.Queue")
    print("=" * 80)

    results = []

    for num_items in [100, 1000, 10000]:

        def goated_version(n=num_items):
            ch: Chan[int] = Chan[int](buffer=100)

            def producer():
                for i in range(n):
                    ch.Send(i)
                ch.Close()

            go(producer)
            count = 0
            for _ in ch:
                count += 1
            return count

        def baseline_version(n=num_items):
            q: queue.Queue = queue.Queue(maxsize=100)
            done = threading.Event()

            def producer():
                for i in range(n):
                    q.put(i)
                done.set()

            t = threading.Thread(target=producer)
            t.start()

            count = 0
            while not (done.is_set() and q.empty()):
                try:
                    q.get(timeout=0.01)
                    count += 1
                except queue.Empty:
                    pass
            t.join()
            return count

        goated_time = benchmark(goated_version, 3)
        baseline_time = benchmark(baseline_version, 3)

        results.append(BenchmarkResult(f"Send/Recv {num_items} items", goated_time, baseline_time))

    print(f"\n{'Operation':<40} {'Goated':>10}  {'Baseline':>10}  {'Speedup':>12}")
    print("-" * 80)
    for r in results:
        print(r)


def bench_mutex_vs_lock():
    print("\n" + "=" * 80)
    print("BENCHMARK: Mutex vs threading.Lock")
    print("=" * 80)

    results = []
    iterations = 100000

    def goated_version():
        mu = Mutex()
        counter = [0]
        for _ in range(iterations):
            with mu:
                counter[0] += 1
        return counter[0]

    def baseline_version():
        lock = threading.Lock()
        counter = [0]
        for _ in range(iterations):
            with lock:
                counter[0] += 1
        return counter[0]

    goated_time = benchmark(goated_version, 3)
    baseline_time = benchmark(baseline_version, 3)

    results.append(BenchmarkResult(f"Lock/Unlock {iterations} times", goated_time, baseline_time))

    print(f"\n{'Operation':<40} {'Goated':>10}  {'Baseline':>10}  {'Speedup':>12}")
    print("-" * 80)
    for r in results:
        print(r)


def bench_waitgroup_vs_threading():
    print("\n" + "=" * 80)
    print("BENCHMARK: WaitGroup vs threading (manual)")
    print("=" * 80)

    results = []

    for num_workers in [10, 50, 100]:

        def goated_version(n=num_workers):
            wg = WaitGroup()
            for _ in range(n):
                wg.Add(1)
                go(lambda: (cpu_work(50), wg.Done()))
            wg.Wait()

        def baseline_version(n=num_workers):
            threads = []
            for _ in range(n):
                t = threading.Thread(target=lambda: cpu_work(50))
                t.start()
                threads.append(t)
            for t in threads:
                t.join()

        goated_time = benchmark(goated_version, 3)
        baseline_time = benchmark(baseline_version, 3)

        results.append(
            BenchmarkResult(f"Wait for {num_workers} workers", goated_time, baseline_time)
        )

    print(f"\n{'Operation':<40} {'Goated':>10}  {'Baseline':>10}  {'Speedup':>12}")
    print("-" * 80)
    for r in results:
        print(r)


def bench_real_world_scenario():
    print("\n" + "=" * 80)
    print("BENCHMARK: Real-World Scenario - Parallel API Simulation")
    print("=" * 80)

    def simulate_api_call(id: int) -> dict:
        time.sleep(0.01)
        return {"id": id, "data": f"response_{id}"}

    results = []
    num_calls = 100

    def goated_version():
        with GoGroup(limit=20) as g:
            futures = [g.go(simulate_api_call, i) for i in range(num_calls)]
        return [f.result() for f in futures]

    def baseline_version():
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(simulate_api_call, i) for i in range(num_calls)]
            return [f.result() for f in as_completed(futures)]

    goated_time = benchmark(goated_version, 3)
    baseline_time = benchmark(baseline_version, 3)

    results.append(
        BenchmarkResult(
            f"Parallel API calls ({num_calls} reqs, limit=20)", goated_time, baseline_time
        )
    )

    print(f"\n{'Operation':<40} {'Goated':>10}  {'Baseline':>10}  {'Speedup':>12}")
    print("-" * 80)
    for r in results:
        print(r)


def bench_spawn_overhead():
    print("\n" + "=" * 80)
    print("BENCHMARK: Spawn Overhead (minimal work)")
    print("=" * 80)

    results = []

    def noop():
        pass

    for num_tasks in [100, 1000, 5000]:

        def goated_version(n=num_tasks):
            with GoGroup() as g:
                for _ in range(n):
                    g.go(noop)

        def baseline_version(n=num_tasks):
            with ThreadPoolExecutor(max_workers=32) as executor:
                futures = [executor.submit(noop) for _ in range(n)]
                for f in futures:
                    f.result()

        goated_time = benchmark(goated_version, 3)
        baseline_time = benchmark(baseline_version, 3)

        results.append(
            BenchmarkResult(f"Spawn {num_tasks} no-op tasks", goated_time, baseline_time)
        )

    print(f"\n{'Operation':<40} {'Goated':>10}  {'Baseline':>10}  {'Speedup':>12}")
    print("-" * 80)
    for r in results:
        print(r)


def main():
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + "  GOATED CONCURRENCY BENCHMARKS  ".center(78) + "║")
    print("║" + "  goated.std.goroutine vs Python threading/concurrent.futures  ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")

    bench_spawn_overhead()
    bench_gogroup_vs_threadpool()
    bench_parallel_map_vs_executor_map()
    bench_errgroup_vs_futures()
    bench_channel_vs_queue()
    bench_mutex_vs_lock()
    bench_waitgroup_vs_threading()
    bench_real_world_scenario()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
Key findings:
  • GoGroup uses a shared ThreadPoolExecutor (reuses threads)
  • Baseline creates new ThreadPoolExecutor each time (overhead)
  • For real workloads, performance is comparable
  • GoGroup wins on ergonomics - much cleaner API

Recommendations:
  • Use GoGroup for simple concurrent tasks
  • Use ErrGroup when error handling matters
  • Use parallel_map for list transformations
  • Chan is great for producer-consumer patterns
    """)


if __name__ == "__main__":
    main()
