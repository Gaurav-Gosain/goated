# GOATED - Go stdlib for Python

[![PyPI version](https://img.shields.io/pypi/v/goated-py)](https://pypi.org/project/goated-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/goated-py)](https://pypi.org/project/goated-py/)
[![CI](https://github.com/Gaurav-Gosain/goated/actions/workflows/ci.yml/badge.svg)](https://github.com/Gaurav-Gosain/goated/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Write Python-like code. Get Go speeds.

## What is GOATED

GOATED exposes Go's standard library to Python through high-performance FFI bindings. It provides **21 drop-in stdlib replacements** backed by **279 Go FFI exports**, delivering an average **10x speedup** over pure-Python stdlib modules. Change your imports, keep your code.

## Installation

```bash
pip install goated-py
```

Or build from source:

```bash
git clone https://github.com/Gaurav-Gosain/goated
cd goated
make install
```

## Quick Start: Drop-in Replacements

The fastest way to speed up your Python code -- just change your imports:

```python
# Just change your imports - everything else stays the same
from goated.compat import json      # same as import json
from goated.compat import html      # 13x faster unescape
from goated.compat import gzip      # Go-powered compression
from goated.compat import hashlib   # Go one-shot hashing

# Your existing code works unchanged
data = json.loads('{"key": "value"}')
safe = html.escape("<script>alert('xss')</script>")
compressed = gzip.compress(b"data" * 1000)
digest = hashlib.sha256(b"hello").hexdigest()
```

No new APIs to learn. No code changes beyond the import line.

## Performance

Go targets pure-Python stdlib modules where Python has no C accelerator. Real benchmark results:

| Operation | Speedup vs Python stdlib |
|-----------|------------------------:|
| `email.parseaddr` | **46x** |
| `textwrap.fill` | **44x** |
| `html.unescape` | **16x** |
| `urllib.parse.unquote` | **11x** |
| Batch JSON validate | **5.5x** |
| Batch SHA256 | **3.8x** |

These numbers come from benchmarking Go FFI calls against Python's pure-Python implementations. Modules backed by C extensions in CPython (like `json` parsing) show smaller gains; modules that are pure Python (like `html`, `textwrap`, `email`) show the largest improvements.

## 21 Drop-in Modules

| Module | Import | Description |
|--------|--------|-------------|
| `json` | `from goated.compat import json` | JSON encoding/decoding, Go-accelerated validation and compaction |
| `hashlib` | `from goated.compat import hashlib` | One-shot SHA256/SHA512/MD5 hashing via Go |
| `base64` | `from goated.compat import base64` | Base64/URL-safe encoding for large payloads |
| `re` | `from goated.compat import re` | Go RE2 engine for compatible patterns |
| `gzip` | `from goated.compat import gzip` | Go-powered gzip compress/decompress |
| `zlib` | `from goated.compat import zlib` | Go-powered zlib compress/decompress and checksums |
| `hmac` | `from goated.compat import hmac` | Go-accelerated HMAC one-shot digests |
| `struct` | `from goated.compat import struct` | Binary packing (passthrough to Python) |
| `statistics` | `from goated.compat import statistics` | Go-accelerated stats for large datasets |
| `heapq` | `from goated.compat import heapq` | Go-accelerated nlargest/nsmallest |
| `bisect` | `from goated.compat import bisect` | Bisection algorithm (passthrough to Python) |
| `csv` | `from goated.compat import csv` | Go-accelerated bulk CSV read_all |
| `html` | `from goated.compat import html` | Go-accelerated escape/unescape (16x faster) |
| `difflib` | `from goated.compat import difflib` | Go-accelerated unified diff generation |
| `textwrap` | `from goated.compat import textwrap` | Go-accelerated fill/wrap (44x faster) |
| `ipaddress` | `from goated.compat import ipaddress` | Go-accelerated IP validation and parsing |
| `fnmatch` | `from goated.compat import fnmatch` | Go-accelerated glob pattern matching |
| `colorsys` | `from goated.compat import colorsys` | Go-accelerated batch color conversions |
| `email_utils` | `from goated.compat import email_utils` | Go-accelerated address parsing (46x faster) |
| `uuid` | `from goated.compat import uuid` | Go-accelerated UUID4 generation |
| `urllib` | `from goated.compat import urllib` | Go-accelerated URL quote/unquote (11x faster) |

## Batch Operations

For maximum throughput, use batch APIs that process many items in a single FFI call with goroutine parallelism:

```python
from goated.batch import batch_sha256, batch_gzip_compress, batch_json_valid

# Hash 1000 items in parallel via goroutines
import os
data = [os.urandom(4096) for _ in range(1000)]
hashes = batch_sha256(data)  # 3-4x faster than sequential Python

# Compress in parallel
compressed = batch_gzip_compress(data)

# Validate JSON in parallel
jsons = ['{"valid": true}', 'not json', '{"also": "valid"}']
results = batch_json_valid(jsons)  # [True, False, True]
```

Available batch operations: `batch_sha256`, `batch_sha512`, `batch_md5`, `batch_gzip_compress`, `batch_gzip_decompress`, `batch_b64encode`, `batch_b64decode`, `batch_json_valid`, `batch_regex_match`.

## Go HTTP Server

Start a Go `net/http` server from Python -- handles 100K+ requests/second:

```python
from goated.server import GoServer

with GoServer(":8080") as app:
    app.json("/api/health", '{"status": "ok"}')
    app.static("/", "Hello from Go!")
    input("Server running at :8080, press Enter to stop...")
```

Also available: `FileServer` for serving static directories and `BenchServer` for maximum-throughput benchmarking.

## Go-style Concurrency

Full Go concurrency primitives, backed by an M:N work-stealing scheduler:

```python
from goated.runtime import go, WaitGroup, GoGroup, Chan

# Fire-and-forget goroutine
go(lambda: print("Hello from goroutine!"))

# WaitGroup for synchronization
wg = WaitGroup()
for i in range(10):
    wg.Add(1)
    go(worker, i, done=wg)
wg.Wait()

# GoGroup with automatic tracking
with GoGroup() as g:
    for url in urls:
        g.go(fetch, url)
# Automatically waits here

# Typed channels
ch = Chan[int](buffer=10)
go(lambda: [ch.Send(i) for i in range(10)] or ch.Close())
for val in ch:
    print(val)
```

### Pipelines, Fan-out, and Semaphores

```python
from goated.runtime import Chan, pipe, merge, fan_out, Semaphore, GoGroup

# Pipeline: transform values through stages
src = Chan[int](buffer=10)
doubled = pipe(src, lambda x: x * 2)
stringed = pipe(doubled, lambda x: str(x))

# Fan-out: distribute work across N consumers
outputs = fan_out(src, n=4)

# Merge: combine multiple channels into one
combined = merge(ch1, ch2, ch3)

# Semaphore: limit concurrent operations
sem = Semaphore(3)
with GoGroup() as g:
    for item in work_items:
        def task(it=item):
            with sem:
                process(it)
        g.go(task)
```

Additional primitives: `ErrGroup`, `Mutex`, `RWMutex`, `Once`, `Pool`, `Select`, `Ticker`, `After`, `AfterFunc`, `parallel_map`, `parallel_for`, `FastChan`, `MPMCQueue`.

Channels support true unbuffered rendezvous semantics. Select uses condition-variable notification (no spin-wait).

**Free-threaded Python (3.13t)**: The runtime automatically detects GIL-free execution and enables true OS-thread parallelism.

## Error Handling with Result Types

GOATED uses Rust-inspired `Result[T, E]` types for elegant error handling:

```python
from goated import Ok, Err, Result
from goated.std import strconv

def parse_config(raw: str) -> Result[int, Exception]:
    return strconv.Atoi(raw)

# Pattern matching (Python 3.10+)
match parse_config("42"):
    case Ok(value):
        print(f"Config value: {value}")
    case Err(error):
        print(f"Failed to parse: {error}")

# Fluent API
value = parse_config("42").unwrap_or(0)
doubled = parse_config("21").map(lambda x: x * 2).unwrap()
```

## Three API Styles

| Style | Import | Returns | Use when |
|-------|--------|---------|----------|
| **Direct** | `from goated.std import strings` | `GoSlice`, Go types | You want Go's exact API |
| **Pythonic** | `from goated.pythonic import strings` | Native Python types | You want snake_case + Result types |
| **Compat** | `from goated.compat import json` | Python stdlib types | You want a drop-in replacement |

## cffi Acceleration

For the fastest possible FFI calls, build the optional cffi compiled extension:

```bash
python goated/_build_cffi.py  # optional, 3-5x faster FFI calls
```

This generates a C extension that calls the Go shared library directly, reducing per-call overhead from ~300ns (ctypes) to ~70ns. GOATED falls back to ctypes automatically if cffi is not available.

## Available Packages

### Standard Library Bindings (39 modules)

| Module | Description |
|--------|-------------|
| `strings` | String manipulation (Split, Join, Contains, Replace, etc.) |
| `bytes` | Byte slice operations |
| `strconv` | String conversions (Atoi, Itoa, ParseInt, etc.) |
| `json` | JSON encoding/decoding |
| `base64` | Base64/URL-safe encoding |
| `csv` | CSV reading/writing |
| `xml` | XML parsing |
| `binary` | Binary encoding |
| `crypto` | SHA-256, SHA-512, MD5 hashing |
| `hash` | Hash interface |
| `hex` | Hexadecimal encoding |
| `gzip` | Gzip compression |
| `zip` | ZIP archive support |
| `path` | Path manipulation |
| `filepath` | OS-specific path operations |
| `time` | Time and duration handling |
| `regexp` | Regular expressions (Go RE2) |
| `sort` | Sorting algorithms |
| `rand` | Random number generation |
| `math` | Mathematical functions |
| `log` | Logging |
| `html` | HTML escaping |
| `mime` | MIME type handling |
| `net` | Network operations |
| `url` | URL parsing |
| `http` | HTTP client |
| `fmt` | Formatted I/O |
| `io` | I/O primitives |
| `bufio` | Buffered I/O |
| `errors` | Error handling |
| `context` | Context propagation |
| `unicode` | Unicode utilities |
| `utf8` | UTF-8 encoding |
| `sync` | Mutex, RWMutex, Once, Pool |
| `goroutine` | Goroutines, WaitGroup, Chan, GoGroup |
| `parallel` | Parallel map/for |
| `template` | Text templating |
| `goos` | OS-level functions |
| `testing` | Test utilities |

### Drop-in Compat Modules (21 modules)

| Module | Description |
|--------|-------------|
| `json` | JSON with Go-accelerated validation/compaction |
| `hashlib` | One-shot Go hashing (SHA256, SHA512, MD5) |
| `base64` | Go-accelerated Base64 for large payloads |
| `re` | Go RE2 for compatible regex patterns |
| `gzip` | Go-powered compress/decompress |
| `zlib` | Go-powered zlib + checksums |
| `hmac` | Go-accelerated HMAC digests |
| `struct` | Binary packing (passthrough) |
| `statistics` | Go-accelerated for large datasets |
| `heapq` | Go-accelerated nlargest/nsmallest |
| `bisect` | Bisection (passthrough) |
| `csv` | Go-accelerated bulk read_all |
| `html` | Go-accelerated escape/unescape |
| `difflib` | Go-accelerated unified diff |
| `textwrap` | Go-accelerated fill/wrap |
| `ipaddress` | Go-accelerated IP validation |
| `fnmatch` | Go-accelerated pattern matching |
| `colorsys` | Go-accelerated color conversions |
| `email_utils` | Go-accelerated address parsing |
| `uuid` | Go-accelerated UUID4 generation |
| `urllib` | Go-accelerated URL quote/unquote |

## Development

```bash
# Setup
make dev

# Build Go shared library
make build

# Run tests (1064 total)
make test

# Lint
make lint
```

## Architecture

```
Python code
    |
    v
goated.compat / goated.std / goated.pythonic   (Python API layer)
    |
    v
goated._core                                    (cffi API-mode or ctypes fallback)
    |
    v
libgoated.so                                    (Go shared library, -buildmode=c-shared)
    |
    v
Go stdlib                                       (279 exported functions across 33 Go files)
```

Handle-based FFI: no raw pointers cross the boundary, keeping the Go GC happy. Smart thresholds auto-fallback to Python's C extensions when they are faster for small payloads.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*GOATED: Because your Python deserves to be the Greatest Of All Time, Expedited and Developed.*
