#!/usr/bin/env python3
"""Quick benchmark for smoke testing performance."""

import time

from goated.std import hash, json, strings

print("Quick benchmark: strings, json, hash\n")

text = "hello world " * 100
data = b"benchmark data " * 100

start = time.perf_counter()
for _ in range(10000):
    strings.Contains(text, "world")
print(f"strings.Contains: {(time.perf_counter() - start) * 1000:.1f}ms for 10k ops")

obj = {"key": "value", "nums": [1, 2, 3]}
start = time.perf_counter()
for _ in range(10000):
    json.Marshal(obj)
print(f"json.Marshal:     {(time.perf_counter() - start) * 1000:.1f}ms for 10k ops")

start = time.perf_counter()
for _ in range(1000):
    hash.SumSHA256(data)
print(f"hash.SumSHA256:   {(time.perf_counter() - start) * 1000:.1f}ms for 1k ops")
