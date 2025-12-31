#!/usr/bin/env python3
"""Go-style Concurrency in Python - Made Simple.

This example demonstrates how goated makes Python concurrency as easy as Go.
No more threading boilerplate, no more callback hell.

Run with: python examples/goroutines.py
"""

import random
import time

from goated.std.goroutine import (
    After,
    AfterFunc,
    Await,
    Chan,
    ErrGroup,
    GoGroup,
    Mutex,
    Select,
    SelectCase,
    Ticker,
    go,
    goroutine,
    parallel_map,
)


def example_basic_go():
    """Basic goroutine spawning - fire and forget."""
    print("=" * 60)
    print("1. BASIC GOROUTINES")
    print("=" * 60)

    def worker(id: int, delay: float):
        time.sleep(delay)
        print(f"   Worker {id} completed after {delay:.2f}s")

    print("\nSpawning 5 workers with random delays...")
    futures = []
    for i in range(5):
        f = go(worker, i, random.uniform(0.1, 0.3))
        futures.append(f)

    Await(*futures)
    print("All workers done!\n")


def example_gogroup():
    """GoGroup - the easiest way to manage concurrent tasks."""
    print("=" * 60)
    print("2. GoGroup - SIMPLE CONCURRENT TASKS")
    print("=" * 60)

    results: list[int] = []
    lock = Mutex()

    def compute(x: int) -> int:
        time.sleep(0.05)
        result = x * x
        with lock:
            results.append(result)
        return result

    print("\nComputing squares of 0-9 concurrently...")
    with GoGroup() as g:
        for i in range(10):
            g.go(compute, i)

    print(f"Results: {sorted(results)}\n")


def example_gogroup_with_limit():
    """GoGroup with concurrency limit - like a semaphore."""
    print("=" * 60)
    print("3. GoGroup WITH CONCURRENCY LIMIT")
    print("=" * 60)

    active = [0]
    max_active = [0]
    lock = Mutex()

    def task(id: int):
        with lock:
            active[0] += 1
            max_active[0] = max(max_active[0], active[0])

        time.sleep(0.1)

        with lock:
            active[0] -= 1

    print("\nRunning 20 tasks with limit=5...")
    with GoGroup(limit=5) as g:
        for i in range(20):
            g.go(task, i)

    print(f"Max concurrent tasks: {max_active[0]} (limit was 5)\n")


def example_errgroup():
    """ErrGroup - handle errors in concurrent tasks."""
    print("=" * 60)
    print("4. ErrGroup - ERROR HANDLING")
    print("=" * 60)

    def fetch_user(id: int) -> dict:
        time.sleep(0.05)
        return {"id": id, "name": f"User {id}"}

    def fetch_failing(id: int) -> dict:
        time.sleep(0.05)
        raise ValueError(f"Failed to fetch {id}")

    print("\nSuccessful tasks:")
    with ErrGroup() as g:
        g.go(fetch_user, 1)
        g.go(fetch_user, 2)
        g.go(fetch_user, 3)
    print("   All tasks succeeded!")

    print("\nWith a failing task:")
    try:
        with ErrGroup() as g:
            g.go(fetch_user, 1)
            g.go(fetch_failing, 2)
            g.go(fetch_user, 3)
    except ValueError as e:
        print(f"   Caught error: {e}\n")


def example_goroutine_decorator():
    """@goroutine decorator - make any function async."""
    print("=" * 60)
    print("5. @goroutine DECORATOR")
    print("=" * 60)

    @goroutine
    def slow_computation(x: int) -> int:
        time.sleep(0.1)
        return x * x

    print("\nCalling decorated function returns Future immediately:")
    start = time.perf_counter()

    f1 = slow_computation(10)
    f2 = slow_computation(20)
    f3 = slow_computation(30)

    elapsed = time.perf_counter() - start
    print(f"   Three calls took {elapsed * 1000:.1f}ms (non-blocking)")

    results = Await(f1, f2, f3)
    total = time.perf_counter() - start
    print(f"   Results: {results}")
    print(f"   Total time: {total * 1000:.1f}ms (ran in parallel)\n")


def example_channels():
    """Go-style channels for goroutine communication."""
    print("=" * 60)
    print("6. CHANNELS - GOROUTINE COMMUNICATION")
    print("=" * 60)

    ch: Chan[int] = Chan[int](buffer=5)

    def producer():
        for i in range(5):
            ch.Send(i)
            print(f"   Produced: {i}")
        ch.Close()

    def consumer():
        for val in ch:
            print(f"   Consumed: {val}")

    print("\nProducer-Consumer pattern:")
    go(producer)
    time.sleep(0.1)
    consumer()
    print()


def example_worker_pool():
    """Classic worker pool pattern with channels."""
    print("=" * 60)
    print("7. WORKER POOL PATTERN")
    print("=" * 60)

    jobs: Chan[int] = Chan[int](buffer=100)
    results: Chan[int] = Chan[int](buffer=100)

    def worker(id: int):
        for job in jobs:
            time.sleep(0.01)
            results.Send(job * job)

    num_workers = 4
    num_jobs = 20

    print(f"\nProcessing {num_jobs} jobs with {num_workers} workers...")

    with GoGroup() as g:
        for w in range(num_workers):
            g.go(worker, w)

        for j in range(num_jobs):
            jobs.Send(j)
        jobs.Close()

    results.Close()

    collected = []
    for r in results:
        collected.append(r)

    print(f"Results: {sorted(collected)}\n")


def example_parallel_map():
    """Parallel map - like Go's parallel for loops."""
    print("=" * 60)
    print("8. PARALLEL MAP & FOR")
    print("=" * 60)

    def expensive_compute(x: int) -> int:
        time.sleep(0.02)
        return x * x

    items = list(range(20))

    print("\nSequential processing:")
    start = time.perf_counter()
    [expensive_compute(x) for x in items]
    seq_time = time.perf_counter() - start
    print(f"   Time: {seq_time * 1000:.0f}ms")

    print("\nParallel processing:")
    start = time.perf_counter()
    parallel_map(expensive_compute, items)
    par_time = time.perf_counter() - start
    print(f"   Time: {par_time * 1000:.0f}ms")
    print(f"   Speedup: {seq_time / par_time:.1f}x\n")


def example_timeout():
    """Using After for timeouts."""
    print("=" * 60)
    print("9. TIMEOUTS WITH After")
    print("=" * 60)

    data_ch: Chan[str] = Chan[str](buffer=1)

    def slow_fetch():
        time.sleep(0.3)
        data_ch.TrySend("data arrived")

    go(slow_fetch)

    print("\nWaiting for data with 100ms timeout...")
    timeout = After(0.1)

    idx, val, ok = Select(
        SelectCase(data_ch),
        SelectCase(timeout),
    )

    if idx == 0:
        print(f"   Got data: {val}")
    else:
        print("   Timeout! Data took too long.\n")


def example_ticker():
    """Periodic tasks with Ticker."""
    print("=" * 60)
    print("10. PERIODIC TASKS WITH Ticker")
    print("=" * 60)

    print("\nTicking every 100ms for 5 ticks...")
    ticker = Ticker(0.1)
    count = 0

    for _t in ticker:
        count += 1
        print(f"   Tick {count}")
        if count >= 5:
            ticker.Close()
            break

    print()


def example_afterfunc():
    """Delayed execution with AfterFunc."""
    print("=" * 60)
    print("11. DELAYED EXECUTION WITH AfterFunc")
    print("=" * 60)

    print("\nScheduling task for 200ms later...")
    done = [False]

    def delayed_task():
        done[0] = True
        print("   Delayed task executed!")

    AfterFunc(0.2, delayed_task)

    print("   Waiting...")
    time.sleep(0.3)

    print("\nScheduling another task but cancelling it...")
    cancel2 = AfterFunc(0.5, lambda: print("   This won't print"))
    time.sleep(0.1)
    cancelled = cancel2()
    print(f"   Cancelled: {cancelled}\n")


def example_fan_out_fan_in():
    """Fan-out/Fan-in pattern."""
    print("=" * 60)
    print("12. FAN-OUT / FAN-IN PATTERN")
    print("=" * 60)

    def stage1(x: int) -> int:
        time.sleep(0.02)
        return x * 2

    def stage2(x: int) -> int:
        time.sleep(0.02)
        return x + 10

    inputs = list(range(10))

    print(f"\nProcessing {len(inputs)} items through 2-stage pipeline...")

    start = time.perf_counter()

    stage1_results = parallel_map(stage1, inputs)
    stage2_results = parallel_map(stage2, stage1_results)

    elapsed = time.perf_counter() - start

    print(f"   Input:  {inputs}")
    print(f"   Stage1: {stage1_results}")
    print(f"   Stage2: {stage2_results}")
    print(f"   Time:   {elapsed * 1000:.0f}ms\n")


def example_mutex_protected_counter():
    """Thread-safe counter with Mutex."""
    print("=" * 60)
    print("13. MUTEX-PROTECTED COUNTER")
    print("=" * 60)

    counter = [0]
    mu = Mutex()

    def increment(n: int):
        for _ in range(n):
            with mu:
                counter[0] += 1

    print("\n10 goroutines incrementing counter 1000 times each...")

    with GoGroup() as g:
        for _ in range(10):
            g.go(increment, 1000)

    print(f"   Final counter: {counter[0]} (expected: 10000)\n")


def example_real_world_api_fetch():
    """Real-world example: parallel API fetching."""
    print("=" * 60)
    print("14. REAL-WORLD: PARALLEL API FETCHING")
    print("=" * 60)

    def fetch_user(id: int) -> dict:
        time.sleep(random.uniform(0.05, 0.15))
        return {"id": id, "name": f"User {id}", "email": f"user{id}@example.com"}

    def fetch_posts(user_id: int) -> list:
        time.sleep(random.uniform(0.05, 0.15))
        return [{"id": i, "title": f"Post {i}"} for i in range(3)]

    def fetch_comments(post_id: int) -> list:
        time.sleep(random.uniform(0.02, 0.08))
        return [{"id": i, "text": f"Comment {i}"} for i in range(2)]

    user_ids = [1, 2, 3, 4, 5]

    print(f"\nFetching data for {len(user_ids)} users in parallel...")
    start = time.perf_counter()

    with GoGroup(limit=10) as g:
        user_futures = [g.go(fetch_user, uid) for uid in user_ids]
        post_futures = [g.go(fetch_posts, uid) for uid in user_ids]

    users = [f.result() for f in user_futures]
    all_posts = [f.result() for f in post_futures]

    elapsed = time.perf_counter() - start

    print(f"   Fetched {len(users)} users")
    print(f"   Fetched {sum(len(p) for p in all_posts)} posts")
    print(f"   Time: {elapsed * 1000:.0f}ms\n")


def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  GO-STYLE CONCURRENCY IN PYTHON  ".center(58) + "║")
    print("║" + "  goated.std.goroutine examples  ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    example_basic_go()
    example_gogroup()
    example_gogroup_with_limit()
    example_errgroup()
    example_goroutine_decorator()
    example_channels()
    example_worker_pool()
    example_parallel_map()
    example_timeout()
    example_ticker()
    example_afterfunc()
    example_fan_out_fan_in()
    example_mutex_protected_counter()
    example_real_world_api_fetch()

    print("=" * 60)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 60)
    print()
    print("Key takeaways:")
    print("  • GoGroup() - simplest way to run concurrent tasks")
    print("  • ErrGroup() - when you need error handling")
    print("  • @goroutine - decorator for async functions")
    print("  • Chan[] - typed channels for communication")
    print("  • parallel_map() - parallel list processing")
    print()


if __name__ == "__main__":
    main()
