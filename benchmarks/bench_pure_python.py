#!/usr/bin/env python3
"""Benchmark Go vs pure-Python stdlib modules.

These are the modules where Go has the BIGGEST advantage because
Python's implementation is pure Python (no C accelerator).

Usage:
    python benchmarks/bench_pure_python.py
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "goated"))


def bench(fn, N=1000):
    for _ in range(min(50, N)):
        fn()
    start = time.perf_counter_ns()
    for _ in range(N):
        fn()
    return (time.perf_counter_ns() - start) / N


def main():
    print("=" * 85)
    print("GOATED: Go vs Pure-Python Stdlib Benchmarks")
    print("=" * 85)

    try:
        from _goated_cffi import ffi, lib
        backend = "cffi API mode"
    except ImportError:
        backend = "ctypes"
        ffi = lib = None

    print(f"Backend: {backend}")
    print(f"CPU: {os.cpu_count()} cores")
    print()

    results = []

    def report(cat, op, py_ns, go_ns):
        s = py_ns / go_ns if go_ns > 0 else 0
        results.append((cat, op, s))
        marker = "***" if s >= 5 else "**" if s >= 2 else "*" if s >= 1.2 else " "
        print(f"  {marker:3s} {op:50s} {py_ns/1000:>8.1f}μs → {go_ns/1000:>8.1f}μs  {s:>5.1f}x")

    # HTML unescape
    print("HTML (html.unescape is pure Python)")
    print("-" * 85)
    import html

    if lib:
        for sz in [500, 5000, 50000]:
            s = ("&lt;div class=&quot;t&quot;&gt;" * (sz // 30))[:sz]
            sb = s.encode()
            report("html", f"unescape ({len(s)}B)",
                   bench(lambda: html.unescape(s), max(50, 100000 // sz)),
                   bench(lambda: lib.goated_html_unescape_string(sb), max(50, 100000 // sz)))
    print()

    # URL encode/decode
    print("URL (urllib.parse is pure Python)")
    print("-" * 85)
    from urllib.parse import quote_plus, unquote

    if lib:
        for sz in [200, 1000, 5000]:
            s = ("hello world path search terms foo bar " * (sz // 38))[:sz]
            sb = s.encode()
            report("url", f"quote_plus ({len(s)}B)",
                   bench(lambda: quote_plus(s), 10000),
                   bench(lambda: lib.goated_url_query_escape(sb), 10000))
            esc = quote_plus(s).encode()
            report("url", f"unquote ({len(esc)}B)",
                   bench(lambda: unquote(esc.decode()), 10000),
                   bench(lambda: lib.goated_url_query_unescape(esc, ffi.new("char**")), 10000))
    print()

    # JSON validate
    print("JSON (validate avoids Python object construction)")
    print("-" * 85)
    import json

    if lib:
        for nk, label in [(20, "5KB"), (100, "25KB"), (500, "125KB")]:
            js = json.dumps({f"k{i}": list(range(50)) for i in range(nk)})
            jb = js.encode()
            report("json", f"validate ({label})",
                   bench(lambda: json.loads(js), max(50, 500000 // len(js))),
                   bench(lambda: lib.goated_json_Valid(jb, len(jb)), max(50, 500000 // len(js))))
    print()

    # Batch operations
    print("BATCH (goroutine parallelism across CPU cores)")
    print("-" * 85)
    from goated.batch import batch_sha256, batch_gzip_compress, batch_json_valid, batch_b64encode
    import base64
    import gzip
    import hashlib

    for n, sz in [(500, 4096), (1000, 16384)]:
        items = [os.urandom(sz) for _ in range(n)]
        label = f"{n}x{sz // 1024}KB"
        report("batch", f"SHA256 ({label})",
               bench(lambda: [hashlib.sha256(d).hexdigest() for d in items], 10),
               bench(lambda: batch_sha256(items), 10))

    for n, sz in [(100, 65536)]:
        items = [os.urandom(sz) for _ in range(n)]
        label = f"{n}x{sz // 1024}KB"
        report("batch", f"gzip ({label})",
               bench(lambda: [gzip.compress(d) for d in items], 3),
               bench(lambda: batch_gzip_compress(items), 3))

    for n in [1000, 5000]:
        jsons = [json.dumps({"id": i, "data": list(range(50))}) for i in range(n)]
        report("batch", f"JSON validate ({n} docs)",
               bench(lambda: [json.loads(j) for j in jsons], 5),
               bench(lambda: batch_json_valid(jsons), 5))

    for n, sz in [(1000, 4096)]:
        items = [os.urandom(sz) for _ in range(n)]
        label = f"{n}x{sz // 1024}KB"
        report("batch", f"base64 encode ({label})",
               bench(lambda: [base64.b64encode(d) for d in items], 10),
               bench(lambda: batch_b64encode(items), 10))

    print()
    print("=" * 85)
    print("SUMMARY")
    print("=" * 85)

    wins = [s for _, _, s in results if s >= 1.0]
    big = [s for _, _, s in results if s >= 2.0]
    huge = [s for _, _, s in results if s >= 5.0]
    best = max(results, key=lambda x: x[2])
    avg = sum(s for _, _, s in results) / len(results) if results else 0

    print(f"  Total:    {len(results)} benchmarks")
    print(f"  Wins:     {len(wins)} ({len(wins) * 100 // len(results)}%)")
    print(f"  Big (>2x): {len(big)}")
    print(f"  Huge (>5x): {len(huge)}")
    print(f"  Best:     {best[2]:.1f}x ({best[0]}/{best[1]})")
    print(f"  Average:  {avg:.1f}x")


if __name__ == "__main__":
    main()
