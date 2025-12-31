#!/usr/bin/env python3
"""Scaled benchmarks showing FFI crossover points.

Small data = Python wins (ctypes overhead dominates)
Large data = Go FFI wins (actual computation dominates)

Run with: python benchmarks/bench_scaled.py
"""

import base64 as py_base64
import gzip as py_gzip
import hashlib
import json as py_json
import re as py_re
import time

from goated._core import is_library_available
from goated.std import base64, gzip, hash, json, regexp, strings


def bench(func, iterations: int = 100) -> float:
    """Run benchmark, return ns per operation."""
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    elapsed = time.perf_counter() - start
    return (elapsed / iterations) * 1_000_000_000


def format_result(goated_ns: float, native_ns: float) -> str:
    """Format benchmark result with winner indicator."""
    ratio = goated_ns / native_ns if native_ns > 0 else float("inf")
    if ratio < 0.9:
        return f"✓ {goated_ns:>10,.0f}ns vs {native_ns:>10,.0f}ns ({ratio:.2f}x faster)"
    elif ratio > 1.1:
        return f"✗ {goated_ns:>10,.0f}ns vs {native_ns:>10,.0f}ns ({ratio:.2f}x slower)"
    else:
        return f"≈ {goated_ns:>10,.0f}ns vs {native_ns:>10,.0f}ns (similar)"


def run_scaled_string_benchmarks():
    """String operations at various sizes."""
    print("\n" + "=" * 70)
    print("STRING OPERATIONS - Scaled by data size")
    print("=" * 70)
    print(f"{'Size':<20} {'Operation':<20} {'Result'}")
    print("-" * 70)

    sizes = [
        ("Tiny (43B)", "x" * 43),
        ("Small (1KB)", "x" * 1024),
        ("Medium (10KB)", "x" * 10240),
        ("Large (100KB)", "x" * 102400),
        ("XL (1MB)", "x" * 1048576),
    ]

    for size_name, text in sizes:
        # Contains
        goated_ns = bench(lambda t=text: strings.Contains(t, "xxx"), iterations=100)
        native_ns = bench(lambda t=text: "xxx" in t, iterations=100)
        print(f"{size_name:<20} {'Contains':<20} {format_result(goated_ns, native_ns)}")

        # ToUpper
        goated_ns = bench(lambda t=text: strings.ToUpper(t), iterations=50)
        native_ns = bench(lambda t=text: t.upper(), iterations=50)
        print(f"{'':<20} {'ToUpper':<20} {format_result(goated_ns, native_ns)}")

        # Replace
        goated_ns = bench(lambda t=text: strings.Replace(t, "x", "y", -1), iterations=20)
        native_ns = bench(lambda t=text: t.replace("x", "y"), iterations=20)
        print(f"{'':<20} {'Replace':<20} {format_result(goated_ns, native_ns)}")
        print()


def run_scaled_json_benchmarks():
    """JSON operations at various sizes."""
    print("\n" + "=" * 70)
    print("JSON OPERATIONS - Scaled by data size")
    print("=" * 70)
    print(f"{'Size':<20} {'Operation':<20} {'Result'}")
    print("-" * 70)

    # Different sized objects
    sizes = [
        ("Tiny (3 fields)", {"a": 1, "b": 2, "c": 3}),
        ("Small (10 fields)", {f"key{i}": i for i in range(10)}),
        ("Medium (100 fields)", {f"key{i}": f"value{i}" for i in range(100)}),
        ("Large (1000 fields)", {f"key{i}": f"value{i}" * 10 for i in range(1000)}),
        ("Nested", {"level1": {"level2": {"level3": {"data": list(range(100))}}}}),
    ]

    for size_name, obj in sizes:
        json_str = py_json.dumps(obj)
        json_bytes = json_str.encode()

        # Marshal
        goated_ns = bench(lambda o=obj: json.Marshal(o), iterations=100)
        native_ns = bench(lambda o=obj: py_json.dumps(o), iterations=100)
        print(f"{size_name:<20} {'Marshal':<20} {format_result(goated_ns, native_ns)}")

        # Unmarshal
        goated_ns = bench(lambda b=json_bytes: json.Unmarshal(b), iterations=100)
        native_ns = bench(lambda s=json_str: py_json.loads(s), iterations=100)
        print(f"{'':<20} {'Unmarshal':<20} {format_result(goated_ns, native_ns)}")
        print()


def run_scaled_hash_benchmarks():
    """Hash operations at various sizes."""
    print("\n" + "=" * 70)
    print("HASH OPERATIONS - Scaled by data size")
    print("=" * 70)
    print(f"{'Size':<20} {'Algorithm':<20} {'Result'}")
    print("-" * 70)

    sizes = [
        ("Tiny (100B)", b"x" * 100),
        ("Small (1KB)", b"x" * 1024),
        ("Medium (10KB)", b"x" * 10240),
        ("Large (100KB)", b"x" * 102400),
        ("XL (1MB)", b"x" * 1048576),
    ]

    for size_name, data in sizes:
        iters = 100 if len(data) < 100000 else 10

        # SHA256
        goated_ns = bench(lambda d=data: hash.SumSHA256(d), iterations=iters)
        native_ns = bench(lambda d=data: hashlib.sha256(d).digest(), iterations=iters)
        print(f"{size_name:<20} {'SHA256':<20} {format_result(goated_ns, native_ns)}")

        # SHA512
        goated_ns = bench(lambda d=data: hash.SumSHA512(d), iterations=iters)
        native_ns = bench(lambda d=data: hashlib.sha512(d).digest(), iterations=iters)
        print(f"{'':<20} {'SHA512':<20} {format_result(goated_ns, native_ns)}")

        # MD5
        goated_ns = bench(lambda d=data: hash.SumMD5(d), iterations=iters)
        native_ns = bench(lambda d=data: hashlib.md5(d).digest(), iterations=iters)
        print(f"{'':<20} {'MD5':<20} {format_result(goated_ns, native_ns)}")
        print()


def run_scaled_compression_benchmarks():
    """Compression operations at various sizes."""
    print("\n" + "=" * 70)
    print("COMPRESSION OPERATIONS - Scaled by data size")
    print("=" * 70)
    print(f"{'Size':<20} {'Operation':<20} {'Result'}")
    print("-" * 70)

    from io import BytesIO

    # Use compressible data (repeated pattern)
    sizes = [
        ("Small (1KB)", b"Hello World! " * 80),
        ("Medium (10KB)", b"Hello World! " * 800),
        ("Large (100KB)", b"Hello World! " * 8000),
        ("XL (1MB)", b"Hello World! " * 80000),
    ]

    for size_name, data in sizes:
        iters = 20 if len(data) < 100000 else 5

        def goated_compress(d=data):
            buf = BytesIO()
            w = gzip.NewWriter(buf)
            w.Write(d)
            w.Close()
            return buf.getvalue()

        def native_compress(d=data):
            return py_gzip.compress(d)

        goated_ns = bench(goated_compress, iterations=iters)
        native_ns = bench(native_compress, iterations=iters)
        print(f"{size_name:<20} {'Gzip Compress':<20} {format_result(goated_ns, native_ns)}")

        # Decompress
        compressed = py_gzip.compress(data)

        def goated_decompress(c=compressed):
            r = gzip.NewReader(BytesIO(c)).unwrap()
            result = r.Read()
            r.Close()
            return result

        def native_decompress(c=compressed):
            return py_gzip.decompress(c)

        goated_ns = bench(goated_decompress, iterations=iters)
        native_ns = bench(native_decompress, iterations=iters)
        print(f"{'':<20} {'Gzip Decompress':<20} {format_result(goated_ns, native_ns)}")
        print()


def run_scaled_regexp_benchmarks():
    """Regexp operations at various sizes."""
    print("\n" + "=" * 70)
    print("REGEXP OPERATIONS - Scaled by data size")
    print("=" * 70)
    print(f"{'Size':<20} {'Operation':<20} {'Result'}")
    print("-" * 70)

    # Pre-compile patterns
    go_re = regexp.MustCompile(r"\d+")
    py_compiled = py_re.compile(r"\d+")

    sizes = [
        ("Tiny (50B)", "abc123def456" * 4),
        ("Small (1KB)", "abc123def456xyz789" * 60),
        ("Medium (10KB)", "abc123def456xyz789" * 600),
        ("Large (100KB)", "abc123def456xyz789" * 6000),
    ]

    for size_name, text in sizes:
        iters = 100 if len(text) < 10000 else 20

        # FindAll
        goated_ns = bench(lambda t=text: go_re.FindAllString(t, -1), iterations=iters)
        native_ns = bench(lambda t=text: py_compiled.findall(t), iterations=iters)
        print(f"{size_name:<20} {'FindAll':<20} {format_result(goated_ns, native_ns)}")

        # Match
        goated_ns = bench(lambda t=text: go_re.MatchString(t), iterations=iters)
        native_ns = bench(lambda t=text: bool(py_compiled.search(t)), iterations=iters)
        print(f"{'':<20} {'Match':<20} {format_result(goated_ns, native_ns)}")
        print()


def run_scaled_base64_benchmarks():
    """Base64 operations at various sizes."""
    print("\n" + "=" * 70)
    print("BASE64 OPERATIONS - Scaled by data size")
    print("=" * 70)
    print(f"{'Size':<20} {'Operation':<20} {'Result'}")
    print("-" * 70)

    sizes = [
        ("Tiny (100B)", b"x" * 100),
        ("Small (1KB)", b"x" * 1024),
        ("Medium (10KB)", b"x" * 10240),
        ("Large (100KB)", b"x" * 102400),
        ("XL (1MB)", b"x" * 1048576),
    ]

    for size_name, data in sizes:
        iters = 100 if len(data) < 100000 else 10
        encoded = py_base64.b64encode(data).decode()

        # Encode
        goated_ns = bench(lambda d=data: base64.StdEncoding.EncodeToString(d), iterations=iters)
        native_ns = bench(lambda d=data: py_base64.b64encode(d).decode(), iterations=iters)
        print(f"{size_name:<20} {'Encode':<20} {format_result(goated_ns, native_ns)}")

        # Decode
        goated_ns = bench(lambda e=encoded: base64.StdEncoding.DecodeString(e), iterations=iters)
        native_ns = bench(lambda e=encoded: py_base64.b64decode(e), iterations=iters)
        print(f"{'':<20} {'Decode':<20} {format_result(goated_ns, native_ns)}")
        print()


def main():
    print("=" * 70)
    print("  GOATED SCALED BENCHMARKS - Finding the Crossover Point")
    print("=" * 70)
    print(f"\nGo FFI Available: {is_library_available()}")
    print("\nLegend: ✓ = goated faster, ✗ = goated slower, ≈ = similar")
    print("Key insight: FFI overhead is fixed, computation scales with size")
    print("Expected: Small data → Python wins, Large data → Go FFI wins")

    run_scaled_string_benchmarks()
    run_scaled_hash_benchmarks()
    run_scaled_json_benchmarks()
    run_scaled_base64_benchmarks()
    run_scaled_compression_benchmarks()
    run_scaled_regexp_benchmarks()

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print("""
For best performance:
- Use goated for: Large data (>10KB), batch operations, CPU-intensive work
- Use Python for: Small data (<1KB), simple operations, one-off calls
- The crossover point varies by operation type
""")


if __name__ == "__main__":
    main()
