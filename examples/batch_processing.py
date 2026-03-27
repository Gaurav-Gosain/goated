"""Batch operations: process many items in parallel via goroutines.

Batch APIs send N items to Go in a single FFI call, where goroutines
process them in parallel across all CPU cores. This amortizes FFI
overhead and delivers 2-10x speedups over sequential Python.
"""

import os
import time

from goated.batch import (
    batch_b64encode,
    batch_gzip_compress,
    batch_gzip_decompress,
    batch_json_valid,
    batch_sha256,
)

# -- Batch SHA256: hash 1000 items in parallel --
print("=== Batch SHA256 ===")
files = [os.urandom(4096) for _ in range(1000)]

start = time.perf_counter()
hashes = batch_sha256(files)
elapsed = time.perf_counter() - start

print(f"Hashed {len(files)} items in {elapsed:.3f}s")
print(f"First hash: {hashes[0]}")
print(f"Last hash:  {hashes[-1]}")

# -- Batch Gzip: compress and decompress in parallel --
print("\n=== Batch Gzip ===")
data = [os.urandom(8192) for _ in range(500)]

start = time.perf_counter()
compressed = batch_gzip_compress(data)
elapsed_compress = time.perf_counter() - start

start = time.perf_counter()
decompressed = batch_gzip_decompress(compressed)
elapsed_decompress = time.perf_counter() - start

total_in = sum(len(d) for d in data)
total_out = sum(len(c) for c in compressed)
print(f"Compressed {len(data)} items in {elapsed_compress:.3f}s")
print(f"Decompressed in {elapsed_decompress:.3f}s")
print(f"Total: {total_in:,} bytes -> {total_out:,} bytes")
assert all(d == o for d, o in zip(data, decompressed))

# -- Batch JSON validation: validate many strings at once --
print("\n=== Batch JSON Validation ===")
json_strings = [
    '{"valid": true}',
    '{"also": "valid", "nested": {"a": 1}}',
    "not json at all",
    "[1, 2, 3]",
    '{"missing": "closing brace"',
    "42",
    "",
]

results = batch_json_valid(json_strings)
for s, valid in zip(json_strings, results):
    status = "VALID" if valid else "INVALID"
    print(f"  {status}: {s[:40]}")

# -- Batch Base64: encode many items in parallel --
print("\n=== Batch Base64 ===")
items = [os.urandom(1024) for _ in range(200)]

start = time.perf_counter()
encoded = batch_b64encode(items)
elapsed = time.perf_counter() - start

print(f"Encoded {len(items)} items in {elapsed:.3f}s")
print(f"First (truncated): {encoded[0][:40]}...")
