#!/usr/bin/env python3
"""Comprehensive benchmarks: Go FFI compat vs Python stdlib.

Measures speedup for every compat module across different payload sizes.

Usage:
    python benchmarks/bench_compat.py
"""

from __future__ import annotations

import base64 as stdlib_base64
import csv as stdlib_csv
import gzip as stdlib_gzip
import hashlib as stdlib_hashlib
import hmac as stdlib_hmac
import html as stdlib_html
import io
import json as stdlib_json
import os
import time
import zlib as stdlib_zlib


def bench(name: str, fn: callable, iterations: int = 100) -> float:
    """Benchmark a function, return average time in microseconds."""
    # Warmup
    for _ in range(min(10, iterations)):
        fn()
    # Measure
    start = time.perf_counter_ns()
    for _ in range(iterations):
        fn()
    elapsed_ns = time.perf_counter_ns() - start
    return elapsed_ns / iterations / 1000  # microseconds


def run_benchmarks():
    print("=" * 80)
    print("GOATED COMPAT vs PYTHON STDLIB BENCHMARKS")
    print("=" * 80)
    print()

    # Import compat modules
    from goated.compat import base64 as go_base64
    from goated.compat import csv as go_csv
    from goated.compat import gzip as go_gzip
    from goated.compat import hashlib as go_hashlib
    from goated.compat import hmac as go_hmac
    from goated.compat import html as go_html
    from goated.compat import json as go_json
    from goated.compat import zlib as go_zlib

    results = []

    def report(category: str, operation: str, py_us: float, go_us: float):
        speedup = py_us / go_us if go_us > 0 else float("inf")
        marker = "✓" if speedup >= 1.0 else "✗"
        results.append((category, operation, py_us, go_us, speedup))
        print(f"  {marker} {operation:40s}  Python: {py_us:10.1f}μs  Go: {go_us:10.1f}μs  {speedup:6.2f}x")

    # =========================================================================
    # JSON
    # =========================================================================
    print("JSON")
    print("-" * 80)

    for size_label, obj in [
        ("small (100B)", {"key": "value", "num": 42}),
        ("medium (10KB)", {"data": list(range(1000))}),
        ("large (100KB)", {"data": [{"id": i, "name": f"item_{i}", "values": list(range(20))} for i in range(200)]}),
    ]:
        s = stdlib_json.dumps(obj)
        report("json", f"dumps {size_label}",
               bench(f"py_json_dumps_{size_label}", lambda: stdlib_json.dumps(obj)),
               bench(f"go_json_dumps_{size_label}", lambda: go_json.dumps(obj)))
        report("json", f"loads {size_label}",
               bench(f"py_json_loads_{size_label}", lambda: stdlib_json.loads(s)),
               bench(f"go_json_loads_{size_label}", lambda: go_json.loads(s)))

    s = stdlib_json.dumps({"valid": True})
    report("json", "valid (small)",
           bench("py_json_valid", lambda: stdlib_json.loads(s)),
           bench("go_json_valid", lambda: go_json.valid(s)))
    print()

    # =========================================================================
    # HASHLIB
    # =========================================================================
    print("HASHLIB (one-shot via go_hexdigest)")
    print("-" * 80)

    for size_label, data in [
        ("1KB", os.urandom(1024)),
        ("10KB", os.urandom(10240)),
        ("1MB", os.urandom(1048576)),
    ]:
        for algo in ("md5", "sha256", "sha512"):
            report("hashlib", f"{algo} {size_label}",
                   bench(f"py_{algo}_{size_label}", lambda: stdlib_hashlib.new(algo, data).hexdigest(), 50),
                   bench(f"go_{algo}_{size_label}", lambda: go_hashlib.go_hexdigest(algo, data), 50))
    print()

    # =========================================================================
    # HMAC
    # =========================================================================
    print("HMAC")
    print("-" * 80)

    key = os.urandom(32)
    for size_label, msg in [
        ("1KB", os.urandom(1024)),
        ("10KB", os.urandom(10240)),
    ]:
        for algo in ("sha256", "sha512"):
            report("hmac", f"{algo} {size_label}",
                   bench(f"py_hmac_{algo}_{size_label}", lambda: stdlib_hmac.digest(key, msg, algo), 200),
                   bench(f"go_hmac_{algo}_{size_label}", lambda: go_hmac.digest(key, msg, algo), 200))
    print()

    # =========================================================================
    # BASE64
    # =========================================================================
    print("BASE64")
    print("-" * 80)

    for size_label, data in [
        ("1KB", os.urandom(1024)),
        ("10KB", os.urandom(10240)),
        ("100KB", os.urandom(102400)),
    ]:
        encoded = stdlib_base64.b64encode(data)
        report("base64", f"encode {size_label}",
               bench(f"py_b64enc_{size_label}", lambda: stdlib_base64.b64encode(data)),
               bench(f"go_b64enc_{size_label}", lambda: go_base64.b64encode(data)))
        report("base64", f"decode {size_label}",
               bench(f"py_b64dec_{size_label}", lambda: stdlib_base64.b64decode(encoded)),
               bench(f"go_b64dec_{size_label}", lambda: go_base64.b64decode(encoded)))
    print()

    # =========================================================================
    # GZIP
    # =========================================================================
    print("GZIP")
    print("-" * 80)

    for size_label, data in [
        ("1KB", b"x" * 1024),
        ("10KB", b"hello world! " * 800),
        ("100KB", os.urandom(102400)),
    ]:
        compressed = stdlib_gzip.compress(data)
        report("gzip", f"compress {size_label}",
               bench(f"py_gzip_comp_{size_label}", lambda: stdlib_gzip.compress(data), 50),
               bench(f"go_gzip_comp_{size_label}", lambda: go_gzip.compress(data), 50))
        report("gzip", f"decompress {size_label}",
               bench(f"py_gzip_decomp_{size_label}", lambda: stdlib_gzip.decompress(compressed), 50),
               bench(f"go_gzip_decomp_{size_label}", lambda: go_gzip.decompress(compressed), 50))
    print()

    # =========================================================================
    # ZLIB
    # =========================================================================
    print("ZLIB")
    print("-" * 80)

    for size_label, data in [
        ("1KB", b"x" * 1024),
        ("10KB", b"hello world! " * 800),
        ("100KB", os.urandom(102400)),
    ]:
        compressed = stdlib_zlib.compress(data)
        report("zlib", f"compress {size_label}",
               bench(f"py_zlib_comp_{size_label}", lambda: stdlib_zlib.compress(data), 50),
               bench(f"go_zlib_comp_{size_label}", lambda: go_zlib.compress(data), 50))
        report("zlib", f"decompress {size_label}",
               bench(f"py_zlib_decomp_{size_label}", lambda: stdlib_zlib.decompress(compressed), 50),
               bench(f"go_zlib_decomp_{size_label}", lambda: go_zlib.decompress(compressed), 50))

    data = os.urandom(100000)
    report("zlib", "crc32 100KB",
           bench("py_crc32", lambda: stdlib_zlib.crc32(data), 200),
           bench("go_crc32", lambda: go_zlib.crc32(data), 200))
    report("zlib", "adler32 100KB",
           bench("py_adler32", lambda: stdlib_zlib.adler32(data), 200),
           bench("go_adler32", lambda: go_zlib.adler32(data), 200))
    print()

    # =========================================================================
    # HTML
    # =========================================================================
    print("HTML")
    print("-" * 80)

    for size_label, s in [
        ("small", '<script>alert("xss")</script>'),
        ("large", '<div class="test" data-x="foo&bar">' * 200),
    ]:
        report("html", f"escape {size_label}",
               bench(f"py_html_esc_{size_label}", lambda: stdlib_html.escape(s), 500),
               bench(f"go_html_esc_{size_label}", lambda: go_html.escape(s), 500))
        escaped = stdlib_html.escape(s)
        report("html", f"unescape {size_label}",
               bench(f"py_html_unesc_{size_label}", lambda: stdlib_html.unescape(escaped), 500),
               bench(f"go_html_unesc_{size_label}", lambda: go_html.unescape(escaped), 500))
    print()

    # =========================================================================
    # CSV
    # =========================================================================
    print("CSV")
    print("-" * 80)

    for nrows, label in [(100, "100 rows"), (1000, "1K rows"), (10000, "10K rows")]:
        csv_data = "name,age,city\n" + "\n".join(f"person_{i},{20+i%50},city_{i%20}" for i in range(nrows))

        def py_csv():
            return list(stdlib_csv.reader(io.StringIO(csv_data)))

        iters = max(10, 500 // nrows)
        report("csv", f"read_all {label}",
               bench(f"py_csv_{label}", py_csv, iters),
               bench(f"go_csv_{label}", lambda: go_csv.read_all(csv_data), iters))
    print()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    wins = sum(1 for _, _, _, _, s in results if s >= 1.0)
    losses = sum(1 for _, _, _, _, s in results if s < 1.0)
    best = max(results, key=lambda x: x[4])
    worst = min(results, key=lambda x: x[4])

    print(f"  Total benchmarks: {len(results)}")
    print(f"  Go wins: {wins}  ({wins*100//len(results)}%)")
    print(f"  Python wins: {losses}  ({losses*100//len(results)}%)")
    print(f"  Best speedup: {best[4]:.2f}x ({best[0]}/{best[1]})")
    print(f"  Worst: {worst[4]:.2f}x ({worst[0]}/{worst[1]})")
    print()

    avg_speedup = sum(s for _, _, _, _, s in results) / len(results)
    print(f"  Average speedup: {avg_speedup:.2f}x")


if __name__ == "__main__":
    run_benchmarks()
