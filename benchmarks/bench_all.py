#!/usr/bin/env python3
"""Comprehensive benchmarks for all goated modules.

Compares goated implementations against native Python equivalents.
Run with: python benchmarks/bench_all.py
"""

import hashlib
import os
import sys
import time
from collections.abc import Callable
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from goated.std import (
    base64,
    filepath,
    gzip,
    hash,
    hex,
    json,
    path,
    rand,
    regexp,
    sort,
    strconv,
    strings,
    sync,
    url,
)
from goated.std import (
    bytes as gobytes,
)


class Bench:
    def __init__(self):
        self.results: list[tuple[str, str, float, float, float]] = []
        self.current_category = ""

    def category(self, name: str):
        self.current_category = name

    def run(
        self,
        name: str,
        goated_fn: Callable,
        native_fn: Callable,
        iterations: int = 1000,
        warmup: int = 10,
    ):
        for _ in range(warmup):
            goated_fn()
            native_fn()

        start = time.perf_counter()
        for _ in range(iterations):
            goated_fn()
        goated_ns = (time.perf_counter() - start) / iterations * 1e9

        start = time.perf_counter()
        for _ in range(iterations):
            native_fn()
        native_ns = (time.perf_counter() - start) / iterations * 1e9

        ratio = goated_ns / native_ns if native_ns > 0 else 0
        self.results.append((self.current_category, name, goated_ns, native_ns, ratio))

    def print_results(self):
        print("\n" + "═" * 85)
        print("  GOATED BENCHMARK RESULTS")
        print("═" * 85)

        current_cat = ""
        for cat, name, goated_ns, native_ns, ratio in self.results:
            if cat != current_cat:
                current_cat = cat
                print(f"\n{cat}")
                print(f"{'  Operation':<40} {'Goated':>12} {'Native':>12} {'Ratio':>10}")
                print("  " + "-" * 78)

            ratio_str = f"{ratio:.2f}x" if ratio >= 1 else f"{1 / ratio:.2f}x faster"
            status = "✓" if ratio <= 1.5 else "○" if ratio <= 3 else "△"
            print(f"{status} {name:<39} {goated_ns:>10.0f}ns {native_ns:>10.0f}ns {ratio_str:>10}")

        print("\n" + "═" * 85)
        print("Legend: ✓ good (≤1.5x) | ○ acceptable (≤3x) | △ needs optimization")
        print("═" * 85)


def bench_strings(b: Bench):
    b.category("STRINGS")
    text = "The quick brown fox jumps over the lazy dog"
    parts = ["hello", "world", "foo", "bar", "baz"]

    b.run("Contains", lambda: strings.Contains(text, "fox"), lambda: "fox" in text)
    b.run("Count", lambda: strings.Count(text, "o"), lambda: text.count("o"))
    b.run("HasPrefix", lambda: strings.HasPrefix(text, "The"), lambda: text.startswith("The"))
    b.run("HasSuffix", lambda: strings.HasSuffix(text, "dog"), lambda: text.endswith("dog"))
    b.run("Index", lambda: strings.Index(text, "fox"), lambda: text.find("fox"))
    b.run("Join", lambda: strings.Join(parts, ","), lambda: ",".join(parts))
    b.run("Split", lambda: strings.Split(text, " "), lambda: text.split(" "))
    b.run("ToLower", lambda: strings.ToLower(text), lambda: text.lower())
    b.run("ToUpper", lambda: strings.ToUpper(text), lambda: text.upper())
    b.run("TrimSpace", lambda: strings.TrimSpace("  hello  "), lambda: "  hello  ".strip())
    b.run(
        "Replace",
        lambda: strings.Replace(text, "fox", "cat", -1),
        lambda: text.replace("fox", "cat"),
    )
    b.run("Repeat", lambda: strings.Repeat("ab", 100), lambda: "ab" * 100)


def bench_bytes(b: Bench):
    b.category("BYTES")
    data = b"The quick brown fox jumps over the lazy dog"
    parts = [b"hello", b"world", b"foo", b"bar", b"baz"]

    b.run("Contains", lambda: gobytes.Contains(data, b"fox"), lambda: b"fox" in data)
    b.run("Count", lambda: gobytes.Count(data, b"o"), lambda: data.count(b"o"))
    b.run("HasPrefix", lambda: gobytes.HasPrefix(data, b"The"), lambda: data.startswith(b"The"))
    b.run("HasSuffix", lambda: gobytes.HasSuffix(data, b"dog"), lambda: data.endswith(b"dog"))
    b.run("Index", lambda: gobytes.Index(data, b"fox"), lambda: data.find(b"fox"))
    b.run("Join", lambda: gobytes.Join(parts, b","), lambda: b",".join(parts))
    b.run("ToLower", lambda: gobytes.ToLower(data), lambda: data.lower())
    b.run("ToUpper", lambda: gobytes.ToUpper(data), lambda: data.upper())


def bench_sort(b: Bench):
    b.category("SORT")
    ints = [64, 34, 25, 12, 22, 11, 90, 1, 100, 50] * 10
    strs = ["banana", "apple", "cherry", "date", "elderberry"] * 10
    sorted_ints = list(range(1000))

    b.run("Ints (100)", lambda: sort.Ints(ints.copy()), lambda: sorted(ints), iterations=100)
    b.run("Strings (50)", lambda: sort.Strings(strs.copy()), lambda: sorted(strs), iterations=100)
    b.run(
        "SearchInts",
        lambda: sort.SearchInts(sorted_ints, 500),
        lambda: sorted_ints.index(500),
        iterations=10000,
    )
    b.run(
        "IsSorted",
        lambda: sort.IntsAreSorted(sorted_ints),
        lambda: all(sorted_ints[i] <= sorted_ints[i + 1] for i in range(len(sorted_ints) - 1)),
        iterations=100,
    )


def bench_encoding(b: Bench):
    b.category("ENCODING")
    import base64 as py_b64

    data = b"Hello, World! This is benchmark data." * 10
    b64_encoded = py_b64.b64encode(data).decode()
    hex_data = b"Hello, Hex World!"
    hex_encoded = hex_data.hex()

    b.run(
        "Base64 Encode",
        lambda: base64.StdEncoding.EncodeToString(data),
        lambda: py_b64.b64encode(data).decode(),
    )
    b.run(
        "Base64 Decode",
        lambda: base64.StdEncoding.DecodeString(b64_encoded),
        lambda: py_b64.b64decode(b64_encoded),
    )
    b.run("Hex Encode", lambda: hex.EncodeToString(hex_data), lambda: hex_data.hex())
    b.run("Hex Decode", lambda: hex.DecodeString(hex_encoded), lambda: bytes.fromhex(hex_encoded))


def bench_json(b: Bench):
    b.category("JSON")
    import json as py_json

    obj = {"name": "test", "value": 42, "items": [1, 2, 3], "nested": {"a": 1}}
    json_bytes = b'{"name":"test","value":42,"items":[1,2,3],"nested":{"a":1}}'
    json_str = json_bytes.decode()

    b.run("Marshal", lambda: json.Marshal(obj), lambda: py_json.dumps(obj))
    b.run("Unmarshal", lambda: json.Unmarshal(json_bytes), lambda: py_json.loads(json_str))

    def go_valid():
        return json.Valid(json_bytes)

    def py_valid():
        try:
            py_json.loads(json_str)
            return True
        except Exception:
            return False

    b.run("Valid", go_valid, py_valid)


def bench_hash(b: Bench):
    b.category("HASHING")
    data = b"Benchmark data for hashing " * 100

    b.run("MD5", lambda: hash.SumMD5(data), lambda: hashlib.md5(data).digest(), iterations=500)
    b.run("SHA1", lambda: hash.SumSHA1(data), lambda: hashlib.sha1(data).digest(), iterations=500)
    b.run(
        "SHA256",
        lambda: hash.SumSHA256(data),
        lambda: hashlib.sha256(data).digest(),
        iterations=500,
    )
    b.run(
        "SHA512",
        lambda: hash.SumSHA512(data),
        lambda: hashlib.sha512(data).digest(),
        iterations=500,
    )


def bench_compression(b: Bench):
    b.category("COMPRESSION")
    import gzip as py_gzip

    data = b"Compressible data with repetition. " * 100
    compressed = py_gzip.compress(data)

    def go_compress():
        buf = BytesIO()
        w = gzip.NewWriter(buf)
        w.Write(data)
        w.Close()
        return buf.getvalue()

    def go_decompress():
        r = gzip.NewReader(BytesIO(compressed)).unwrap()
        result = r.Read()
        r.Close()
        return result

    b.run("Gzip Compress", go_compress, lambda: py_gzip.compress(data), iterations=100)
    b.run("Gzip Decompress", go_decompress, lambda: py_gzip.decompress(compressed), iterations=100)


def bench_path(b: Bench):
    b.category("PATH")
    p = "/usr/local/bin/python3"
    p2 = "foo/bar/baz.txt"

    b.run("Base", lambda: path.Base(p), lambda: os.path.basename(p))
    b.run("Dir", lambda: path.Dir(p), lambda: os.path.dirname(p))
    b.run("Ext", lambda: path.Ext(p2), lambda: os.path.splitext(p2)[1])
    b.run("Join", lambda: path.Join("a", "b", "c"), lambda: os.path.join("a", "b", "c"))
    b.run("Clean", lambda: path.Clean("a//b/../c"), lambda: os.path.normpath("a//b/../c"))


def bench_filepath(b: Bench):
    b.category("FILEPATH")
    p = "/usr/local/bin/python3"

    b.run("Base", lambda: filepath.Base(p), lambda: os.path.basename(p))
    b.run("Dir", lambda: filepath.Dir(p), lambda: os.path.dirname(p))
    b.run("Ext", lambda: filepath.Ext(p), lambda: os.path.splitext(p)[1])
    b.run("IsAbs", lambda: filepath.IsAbs(p), lambda: os.path.isabs(p))
    b.run(
        "Join",
        lambda: filepath.Join("/usr", "local", "bin"),
        lambda: os.path.join("/usr", "local", "bin"),
    )


def bench_strconv(b: Bench):
    b.category("STRCONV")

    b.run("Itoa", lambda: strconv.Itoa(123456), lambda: str(123456))
    b.run("Atoi", lambda: strconv.Atoi("123456"), lambda: int("123456"))
    b.run(
        "FormatFloat",
        lambda: strconv.FormatFloat(3.14159, "f", 4, 64),
        lambda: f"{3.14159:.4f}",
    )
    b.run("ParseFloat", lambda: strconv.ParseFloat("3.14159", 64), lambda: float("3.14159"))
    b.run("ParseBool", lambda: strconv.ParseBool("true"), lambda: "true".lower() == "true")


def bench_url(b: Bench):
    b.category("URL")
    from urllib.parse import quote, unquote, urlparse

    test_url = "https://user:pass@example.com:8080/path?query=value#fragment"
    to_escape = "hello world & special=chars"
    escaped = "hello%20world%20%26%20special%3Dchars"

    b.run("Parse", lambda: url.Parse(test_url), lambda: urlparse(test_url), iterations=500)
    b.run("QueryEscape", lambda: url.QueryEscape(to_escape), lambda: quote(to_escape))
    b.run("QueryUnescape", lambda: url.QueryUnescape(escaped), lambda: unquote(escaped))


def bench_regexp(b: Bench):
    b.category("REGEXP")
    import re as py_re

    pattern = r"\d{3}-\d{3}-\d{4}"
    text = "Call 123-456-7890 or 987-654-3210"

    go_re = regexp.MustCompile(r"\d+")
    py_compiled = py_re.compile(r"\d+")

    b.run(
        "MatchString",
        lambda: regexp.MatchString(pattern, text),
        lambda: bool(py_re.search(pattern, text)),
    )
    b.run(
        "FindAllString",
        lambda: go_re.FindAllString(text, -1),
        lambda: py_compiled.findall(text),
    )
    b.run("Compile", lambda: regexp.Compile(r"\d+"), lambda: py_re.compile(r"\d+"), iterations=100)


def bench_sync(b: Bench):
    b.category("SYNC")
    import threading

    go_mutex = sync.Mutex()
    py_lock = threading.Lock()

    def go_lock():
        go_mutex.Lock()
        go_mutex.Unlock()

    def py_lock_fn():
        py_lock.acquire()
        py_lock.release()

    b.run("Mutex Lock/Unlock", go_lock, py_lock_fn, iterations=10000)

    go_once = sync.Once()
    py_once_done = [False]
    py_once_lock = threading.Lock()

    def go_once_fn():
        go_once.Do(lambda: None)

    def py_once_fn():
        with py_once_lock:
            if not py_once_done[0]:
                py_once_done[0] = True

    b.run("Once.Do", go_once_fn, py_once_fn, iterations=10000)


def bench_rand(b: Bench):
    b.category("RAND")
    import random

    b.run("Intn", lambda: rand.Intn(1000), lambda: random.randint(0, 999))
    b.run("Float64", lambda: rand.Float64(), lambda: random.random())

    items = list(range(100))
    b.run(
        "Shuffle",
        lambda: rand.Shuffle(len(items), lambda i, j: None),
        lambda: random.shuffle(items.copy()),
        iterations=100,
    )


def main():
    print("╔" + "═" * 83 + "╗")
    print("║" + "  GOATED COMPREHENSIVE BENCHMARKS  ".center(83) + "║")
    print("║" + "  goated.std vs Python stdlib  ".center(83) + "║")
    print("╚" + "═" * 83 + "╝")

    b = Bench()

    bench_strings(b)
    bench_bytes(b)
    bench_sort(b)
    bench_encoding(b)
    bench_json(b)
    bench_hash(b)
    bench_compression(b)
    bench_path(b)
    bench_filepath(b)
    bench_strconv(b)
    bench_url(b)
    bench_regexp(b)
    bench_sync(b)
    bench_rand(b)

    b.print_results()

    good = sum(1 for _, _, _, _, r in b.results if r <= 1.5)
    ok = sum(1 for _, _, _, _, r in b.results if 1.5 < r <= 3)
    slow = sum(1 for _, _, _, _, r in b.results if r > 3)

    print(f"\nSummary: {good} good, {ok} acceptable, {slow} need optimization")
    print(f"Total benchmarks: {len(b.results)}")


if __name__ == "__main__":
    main()
