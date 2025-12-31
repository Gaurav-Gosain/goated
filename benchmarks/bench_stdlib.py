#!/usr/bin/env python3
"""Benchmarks for goated stdlib modules vs native Python.

Run with: python benchmarks/bench_stdlib.py
"""

import base64 as py_base64
import gzip as py_gzip
import hashlib
import json as py_json
import re as py_re
import time
from datetime import datetime
from io import BytesIO

from goated.std import (
    base64,
    gzip,
    hash,
    hex,
    json,
    regexp,
    sort,
    strconv,
    strings,
    sync,
)
from goated.std import time as gotime


class Timer:
    def __init__(self, name: str, iterations: int = 1000):
        self.name = name
        self.iterations = iterations
        self.start_time = 0.0
        self.total_time = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.total_time = time.perf_counter() - self.start_time
        ns_per_op = (self.total_time / self.iterations) * 1_000_000_000
        return ns_per_op


class BenchmarkComparison:
    def __init__(self):
        self.results = []

    def compare(self, name: str, goated_func, native_func, iterations: int = 1000):
        # Benchmark goated
        start = time.perf_counter()
        for _ in range(iterations):
            goated_func()
        goated_time = time.perf_counter() - start
        goated_ns = (goated_time / iterations) * 1_000_000_000

        # Benchmark native
        start = time.perf_counter()
        for _ in range(iterations):
            native_func()
        native_time = time.perf_counter() - start
        native_ns = (native_time / iterations) * 1_000_000_000

        overhead = ((goated_ns / native_ns) - 1) * 100 if native_ns > 0 else 0
        self.results.append((name, goated_ns, native_ns, overhead))

    def print_results(self, category: str):
        print(f"\n{category}:")
        print(f"{'Operation':<35} {'Goated':>12} {'Native':>12} {'Overhead':>10}")
        print("-" * 72)
        for name, goated_ns, native_ns, overhead in self.results:
            sign = "+" if overhead >= 0 else ""
            print(f"{name:<35} {goated_ns:>10.0f}ns {native_ns:>10.0f}ns {sign}{overhead:>8.1f}%")
        self.results = []


def run_string_benchmarks(bench: BenchmarkComparison):
    text = "The quick brown fox jumps over the lazy dog"
    parts = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

    bench.compare("Contains", lambda: strings.Contains(text, "fox"), lambda: "fox" in text)

    bench.compare(
        "Split", lambda: strings.Split("a,b,c,d,e", ","), lambda: ["a", "b", "c", "d", "e"]
    )

    bench.compare("Join", lambda: strings.Join(parts, ","), lambda: ",".join(parts))

    bench.compare(
        "Replace",
        lambda: strings.Replace(text, "fox", "cat", -1),
        lambda: text.replace("fox", "cat"),
    )

    bench.compare("ToUpper", lambda: strings.ToUpper(text), lambda: text.upper())

    bench.compare("ToLower", lambda: strings.ToLower(text), lambda: text.lower())

    bench.compare("TrimSpace", lambda: strings.TrimSpace("  hello  "), lambda: "  hello  ".strip())

    bench.print_results("Strings")


def run_sort_benchmarks(bench: BenchmarkComparison):
    bench.compare(
        "Sort Ints (10 elements)",
        lambda: sort.Ints([64, 34, 25, 12, 22, 11, 90, 1, 100, 50]),
        lambda: sorted([64, 34, 25, 12, 22, 11, 90, 1, 100, 50]),
        iterations=100,
    )

    bench.compare(
        "Sort Strings (5 elements)",
        lambda: sort.Strings(["banana", "apple", "cherry", "date", "elderberry"]),
        lambda: sorted(["banana", "apple", "cherry", "date", "elderberry"]),
        iterations=100,
    )

    data = list(range(1000))
    bench.compare(
        "Binary Search (1000 elements)",
        lambda: sort.SearchInts(data, 500),
        lambda: data.index(500) if 500 in data else -1,
    )

    bench.print_results("Sorting")


def run_encoding_benchmarks(bench: BenchmarkComparison):
    data = b"Hello, World! " * 10
    b64_encoded = "SGVsbG8sIFdvcmxkISA=" * 10
    hex_data = b"Hello, Hex!"
    hex_encoded = "48656c6c6f2c2048657821"

    bench.compare(
        "Base64 Encode",
        lambda: base64.StdEncoding.EncodeToString(data),
        lambda: py_base64.b64encode(data).decode(),
    )

    bench.compare(
        "Base64 Decode",
        lambda: base64.StdEncoding.DecodeString(b64_encoded),
        lambda: py_base64.b64decode(b64_encoded),
    )

    bench.compare("Hex Encode", lambda: hex.EncodeToString(hex_data), lambda: hex_data.hex())

    bench.compare(
        "Hex Decode", lambda: hex.DecodeString(hex_encoded), lambda: bytes.fromhex(hex_encoded)
    )

    bench.print_results("Encoding (Base64/Hex)")


def run_json_benchmarks(bench: BenchmarkComparison):
    obj = {"name": "John", "age": 30, "tags": ["a", "b", "c"]}
    json_bytes = b'{"name": "John", "age": 30, "tags": ["a", "b", "c"]}'
    json_str = '{"name": "John", "age": 30, "tags": ["a", "b", "c"]}'

    bench.compare("JSON Marshal", lambda: json.Marshal(obj), lambda: py_json.dumps(obj))

    bench.compare(
        "JSON Unmarshal", lambda: json.Unmarshal(json_bytes), lambda: py_json.loads(json_str)
    )

    bench.compare(
        "JSON Valid", lambda: json.Valid(json_bytes), lambda: _json_valid_native(json_str)
    )

    bench.print_results("JSON")


def _json_valid_native(s):
    try:
        py_json.loads(s)
        return True
    except:
        return False


def run_hash_benchmarks(bench: BenchmarkComparison):
    data = b"Hello, World! " * 100

    bench.compare("MD5", lambda: hash.SumMD5(data), lambda: hashlib.md5(data).digest())

    bench.compare("SHA1", lambda: hash.SumSHA1(data), lambda: hashlib.sha1(data).digest())

    bench.compare("SHA256", lambda: hash.SumSHA256(data), lambda: hashlib.sha256(data).digest())

    bench.compare("SHA512", lambda: hash.SumSHA512(data), lambda: hashlib.sha512(data).digest())

    bench.print_results("Hashing")


def run_compression_benchmarks(bench: BenchmarkComparison):
    data = b"Hello, World! " * 100

    def goated_compress():
        buf = BytesIO()
        w = gzip.NewWriter(buf)
        w.Write(data)
        w.Close()
        return buf.getvalue()

    def native_compress():
        return py_gzip.compress(data)

    bench.compare("Gzip Compress", goated_compress, native_compress, iterations=100)

    compressed = py_gzip.compress(data)

    def goated_decompress():
        r = gzip.NewReader(BytesIO(compressed)).unwrap()
        result = r.Read()
        r.Close()
        return result

    def native_decompress():
        return py_gzip.decompress(compressed)

    bench.compare("Gzip Decompress", goated_decompress, native_decompress, iterations=100)

    bench.print_results("Compression")


def run_regexp_benchmarks(bench: BenchmarkComparison):
    pattern = r"\d{3}-\d{3}-\d{4}"
    text = "123-456-7890"

    bench.compare(
        "Regexp Match",
        lambda: regexp.MatchString(pattern, text),
        lambda: bool(py_re.match(pattern, text)),
    )

    # Pre-compiled comparison
    go_re = regexp.MustCompile(r"\d+")
    py_compiled = py_re.compile(r"\d+")
    find_text = "abc123def456ghi789"

    bench.compare(
        "FindAll (compiled)",
        lambda: go_re.FindAllString(find_text, -1),
        lambda: py_compiled.findall(find_text),
    )

    bench.compare(
        "Regexp Compile",
        lambda: regexp.Compile(r"\d+"),
        lambda: py_re.compile(r"\d+"),
        iterations=100,
    )

    bench.print_results("Regular Expressions")


def run_time_benchmarks(bench: BenchmarkComparison):
    bench.compare("Now", lambda: gotime.Now(), lambda: datetime.now())

    t = gotime.Now()
    dt = datetime.now()

    bench.compare("Format (RFC3339)", lambda: t.Format(gotime.RFC3339), lambda: dt.isoformat())

    bench.compare(
        "Parse (RFC3339)",
        lambda: gotime.Parse(gotime.RFC3339, "2024-01-15T10:30:00Z"),
        lambda: datetime.fromisoformat("2024-01-15T10:30:00+00:00"),
    )

    bench.print_results("Time")


def run_strconv_benchmarks(bench: BenchmarkComparison):
    bench.compare("Itoa (int to string)", lambda: strconv.Itoa(123456789), lambda: str(123456789))

    bench.compare(
        "Atoi (string to int)", lambda: strconv.Atoi("123456789"), lambda: int("123456789")
    )

    bench.compare(
        "FormatFloat",
        lambda: strconv.FormatFloat(3.141592653589793, "f", 6, 64),
        lambda: f"{3.141592653589793:.6f}",
    )

    bench.compare(
        "ParseFloat",
        lambda: strconv.ParseFloat("3.141592653589793", 64),
        lambda: float("3.141592653589793"),
    )

    bench.print_results("String Conversion")


def run_sync_benchmarks(bench: BenchmarkComparison):
    import threading

    go_mutex = sync.Mutex()
    py_lock = threading.Lock()

    bench.compare(
        "Mutex Lock/Unlock",
        lambda: (go_mutex.Lock(), go_mutex.Unlock()),
        lambda: (py_lock.acquire(), py_lock.release()),
        iterations=10000,
    )

    go_rw = sync.RWMutex()
    py_rwlock = threading.RLock()

    bench.compare(
        "RWMutex RLock/RUnlock",
        lambda: (go_rw.RLock(), go_rw.RUnlock()),
        lambda: (py_rwlock.acquire(), py_rwlock.release()),
        iterations=10000,
    )

    bench.print_results("Synchronization")


def main():
    print("=" * 72)
    print("  goated stdlib benchmarks - Goated vs Native Python")
    print("=" * 72)
    print("\nLower is better. Overhead shows goated cost vs native Python.")

    bench = BenchmarkComparison()

    run_string_benchmarks(bench)
    run_sort_benchmarks(bench)
    run_encoding_benchmarks(bench)
    run_json_benchmarks(bench)
    run_hash_benchmarks(bench)
    run_compression_benchmarks(bench)
    run_regexp_benchmarks(bench)
    run_time_benchmarks(bench)
    run_strconv_benchmarks(bench)
    run_sync_benchmarks(bench)

    print("\n" + "=" * 72)
    print("  Benchmarks completed!")
    print("=" * 72)


if __name__ == "__main__":
    main()
