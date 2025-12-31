#!/usr/bin/env python3
"""Batch operation benchmarks - where Go FFI really shines.

Single operations = Python wins (FFI overhead dominates)
Batch operations = Go wins (parallel execution, amortized overhead)

Run with: python benchmarks/bench_batch.py
"""

import hashlib
import time
from concurrent.futures import ThreadPoolExecutor

from goated._core import is_library_available
from goated.std import parallel


def bench(func, iterations: int = 10) -> float:
    """Run benchmark, return ms per operation."""
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    elapsed = time.perf_counter() - start
    return (elapsed / iterations) * 1000  # ms


def format_result(goated_ms: float, native_ms: float) -> str:
    """Format benchmark result with speedup."""
    speedup = native_ms / goated_ms if goated_ms > 0 else float("inf")
    if speedup > 1.1:
        return f"✓ {goated_ms:>8.2f}ms vs {native_ms:>8.2f}ms ({speedup:.1f}x faster)"
    elif speedup < 0.9:
        return f"✗ {goated_ms:>8.2f}ms vs {native_ms:>8.2f}ms ({1 / speedup:.1f}x slower)"
    else:
        return f"≈ {goated_ms:>8.2f}ms vs {native_ms:>8.2f}ms (similar)"


def run_batch_hash_benchmarks():
    """Batch hashing - Go goroutines vs Python threads."""
    print("\n" + "=" * 74)
    print("BATCH HASHING - Go goroutines vs Python sequential/threaded")
    print("=" * 74)
    print(f"{'Batch Size':<15} {'Data Size':<12} {'Goated vs Sequential':<30} {'vs ThreadPool'}")
    print("-" * 74)

    configs = [
        (100, 1024, "100 × 1KB"),
        (1000, 1024, "1000 × 1KB"),
        (100, 10240, "100 × 10KB"),
        (1000, 10240, "1000 × 10KB"),
        (100, 102400, "100 × 100KB"),
    ]

    for batch_size, data_size, label in configs:
        # Generate test data
        data_list = [f"data_{i}_".encode() * (data_size // 10) for i in range(batch_size)]

        # Goated parallel
        goated_ms = bench(lambda d=data_list: parallel.parallel_hash_sha256(d), iterations=5)

        # Python sequential
        def py_sequential(d=data_list):
            return [hashlib.sha256(x).hexdigest() for x in d]

        seq_ms = bench(py_sequential, iterations=5)

        # Python ThreadPoolExecutor
        def py_threaded(d=data_list):
            with ThreadPoolExecutor(max_workers=8) as ex:
                return list(ex.map(lambda x: hashlib.sha256(x).hexdigest(), d))

        thread_ms = bench(py_threaded, iterations=5)

        seq_result = format_result(goated_ms, seq_ms)

        # Just show speedup for threaded
        thread_speedup = thread_ms / goated_ms if goated_ms > 0 else 0
        if thread_speedup > 1.1:
            thread_indicator = f"✓ {thread_speedup:.1f}x"
        elif thread_speedup > 0.9:
            thread_indicator = "≈"
        else:
            thread_indicator = f"✗ {1 / thread_speedup:.1f}x"

        print(f"{label:<15} {'':<12} {seq_result:<50} {thread_indicator}")


def run_batch_string_benchmarks():
    """Batch string operations - Go parallel vs Python."""
    print("\n" + "=" * 74)
    print("BATCH STRING OPS - Go goroutines vs Python list comprehension")
    print("=" * 74)
    print(f"{'Operation':<20} {'Batch Size':<15} {'Result'}")
    print("-" * 74)

    # ToUpper batch
    for batch_size in [100, 1000, 10000]:
        strings = [f"Hello World {i}!" for i in range(batch_size)]

        goated_ms = bench(lambda s=strings: parallel.parallel_map_upper(s), iterations=10)
        native_ms = bench(lambda s=strings: [x.upper() for x in s], iterations=10)

        print(f"{'ToUpper':<20} {batch_size:<15} {format_result(goated_ms, native_ms)}")

    print()

    # Contains batch
    for batch_size in [100, 1000, 10000]:
        texts = [f"The quick brown fox jumps over the lazy dog {i}" for i in range(batch_size)]

        goated_ms = bench(lambda t=texts: parallel.parallel_contains(t, "fox"), iterations=10)
        native_ms = bench(lambda t=texts: ["fox" in x for x in t], iterations=10)

        print(f"{'Contains':<20} {batch_size:<15} {format_result(goated_ms, native_ms)}")


def run_batch_md5_benchmarks():
    """MD5 batch - common use case for file checksums."""
    print("\n" + "=" * 74)
    print("BATCH MD5 - Simulating file checksum verification")
    print("=" * 74)
    print(f"{'Scenario':<30} {'Result'}")
    print("-" * 74)

    scenarios = [
        ("100 small files (1KB)", 100, 1024),
        ("1000 small files (1KB)", 1000, 1024),
        ("100 medium files (100KB)", 100, 102400),
        ("50 large files (1MB)", 50, 1048576),
    ]

    for scenario_name, count, size in scenarios:
        data_list = [b"x" * size for _ in range(count)]

        goated_ms = bench(lambda d=data_list: parallel.parallel_hash_md5(d), iterations=3)
        native_ms = bench(lambda d=data_list: [hashlib.md5(x).hexdigest() for x in d], iterations=3)

        print(f"{scenario_name:<30} {format_result(goated_ms, native_ms)}")


def run_throughput_comparison():
    """Show raw throughput numbers."""
    print("\n" + "=" * 74)
    print("THROUGHPUT COMPARISON - Operations per second")
    print("=" * 74)

    # SHA256 throughput
    data_list = [b"x" * 10240 for _ in range(1000)]  # 1000 × 10KB

    # Goated
    start = time.perf_counter()
    for _ in range(10):
        parallel.parallel_hash_sha256(data_list)
    goated_time = time.perf_counter() - start
    goated_ops = (10 * 1000) / goated_time

    # Python sequential
    start = time.perf_counter()
    for _ in range(10):
        [hashlib.sha256(x).hexdigest() for x in data_list]
    native_time = time.perf_counter() - start
    native_ops = (10 * 1000) / native_time

    print("\nSHA256 (10KB blocks):")
    print(f"  Goated:    {goated_ops:,.0f} hashes/sec")
    print(f"  Python:    {native_ops:,.0f} hashes/sec")
    print(f"  Speedup:   {goated_ops / native_ops:.1f}x")


def main():
    print("=" * 74)
    print("  GOATED BATCH BENCHMARKS - Parallel Processing with Go")
    print("=" * 74)
    print(f"\nGo FFI Available: {is_library_available()}")
    print(f"CPU Count: {parallel.num_cpus()}")
    print("\nKey insight: Batch operations amortize FFI overhead across many items,")
    print("            and Go's goroutines provide true parallelism (bypass GIL)")

    run_batch_hash_benchmarks()
    run_batch_string_benchmarks()
    run_batch_md5_benchmarks()
    run_throughput_comparison()

    print("\n" + "=" * 74)
    print("  RECOMMENDATION")
    print("=" * 74)
    print("""
Use goated batch operations when:
- Processing 100+ items
- CPU-bound work (hashing, compression, encoding)
- Need to bypass Python's GIL

Use Python for:
- Single items or small batches (<100)
- I/O-bound work (network, disk)
- Simple string operations
""")


if __name__ == "__main__":
    main()
