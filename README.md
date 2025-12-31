# GOATED - Go stdlib for Python

[![PyPI version](https://img.shields.io/pypi/v/goated-py)](https://pypi.org/project/goated-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/goated-py)](https://pypi.org/project/goated-py/)
[![CI](https://github.com/Gaurav-Gosain/goated/actions/workflows/ci.yml/badge.svg)](https://github.com/Gaurav-Gosain/goated/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Write Python-like code. Get Go speeds.

**GOATED** exposes Go's entire standard library to Python through high-performance FFI bindings. Get the best of both worlds: Python's ease of use with Go's blazing speed.

## Features

- **Go Speed**: Native Go performance for CPU-intensive operations
- **Pythonic API**: Three API styles to match your preferences
- **Type Safe**: Full type hints with `Result[T, E]` error handling
- **Async Ready**: Go channels integrate seamlessly with asyncio
- **Go Concurrency**: Goroutines, WaitGroups, channels - just like Go
- **Free-threaded Ready**: Optimized for Python 3.13t (no GIL) with true parallelism
- **Zero Dependencies**: Uses only Python stdlib (ctypes)

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

## Quick Start

### Style A: Direct Mapping (Go names)
```python
from goated.std import strings

# Split a string - returns GoSlice
result = strings.Split("hello,world,goated", ",")
print(result.to_list())  # ['hello', 'world', 'goated']

# Check containment
if strings.Contains("goated", "goat"):
    print("Found it!")
```

### Style B: Pythonic Wrappers (snake_case)
```python
from goated.pythonic import strings

# Returns native Python list
parts = strings.split("hello,world", ",")
print(parts)  # ['hello', 'world']

# Chainable operations with Result types
from goated.pythonic import strconv

value = strconv.parse_int("42", base=10).unwrap()
print(value)  # 42

# Handle errors gracefully
result = strconv.parse_int("not_a_number", base=10)
match result:
    case Ok(v):
        print(f"Parsed: {v}")
    case Err(e):
        print(f"Error: {e}")
```

### Style C: Drop-in Replacement
```python
# Use as drop-in replacement for Python stdlib
from goated.compat import json

data = json.loads('{"name": "goated", "fast": true}')
print(json.dumps(data, indent=2))
```

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

## Go-style Concurrency

GOATED provides two concurrency models:

### 1. Sync Goroutines (Go-style)

Perfect for CPU-bound work and Go-style concurrency patterns:

```python
from goated.runtime import go, WaitGroup, GoGroup, Chan, FastChan

# Simple goroutine spawning
go(lambda: print("Hello from goroutine!"))

# With WaitGroup (like Go's sync.WaitGroup)
wg = WaitGroup()
for i in range(10):
    wg.Add(1)
    go(worker, i, done=wg)
wg.Wait()  # Block until all done

# With GoGroup (easiest - automatic tracking)
with GoGroup() as g:
    for url in urls:
        g.go(fetch, url)
# Automatically waits here

# Channels for communication
ch = Chan[int](buffer=10)
go(lambda: [ch.Send(i) for i in range(10)] and ch.Close())
for val in ch:
    print(val)

# FastChan - alternative channel implementation
fast_ch = FastChan[int](buffer=1000)
```

**Free-threaded Python (3.13t)**: The runtime automatically detects and optimizes for GIL-free execution:

```python
from goated import is_free_threaded

if is_free_threaded():
    print("Running on free-threaded Python - true parallelism!")
```

### 2. Async Channels (asyncio integration)

Perfect for I/O-bound work and asyncio applications:

```python
import asyncio
from goated import Channel, go

async def producer(ch: Channel[int]):
    for i in range(10):
        await ch.send(i)
    ch.close()

async def consumer(ch: Channel[int]):
    async for value in ch:
        print(f"Received: {value}")

async def main():
    ch = Channel[int](buffer_size=5)
    await asyncio.gather(
        producer(ch),
        consumer(ch)
    )

asyncio.run(main())
```

## Available Packages

| Package | Status | Description |
|---------|--------|-------------|
| `strings` | Stable | String manipulation |
| `bytes` | Stable | Byte slice operations |
| `strconv` | Stable | String conversions |
| `encoding/json` | Stable | JSON encoding/decoding |
| `encoding/base64` | Stable | Base64 encoding |
| `encoding/csv` | Stable | CSV reading/writing |
| `encoding/xml` | Stable | XML parsing |
| `crypto/sha256` | Stable | SHA-256 hashing |
| `crypto/md5` | Stable | MD5 hashing |
| `compress/gzip` | Stable | Gzip compression |
| `compress/zip` | Stable | ZIP archive support |
| `path` | Stable | Path manipulation |
| `path/filepath` | Stable | OS-specific path operations |
| `time` | Stable | Time and duration handling |
| `regexp` | Beta | Regular expressions |
| `net` | Beta | Network operations |
| `net/url` | Stable | URL parsing |
| **`runtime`** | **Stable** | **M:N goroutine scheduler, channels, sync primitives** |
| **`goroutine`** | **Stable** | **Go-style concurrency (WaitGroup, Chan, GoGroup)** |

See [docs/std.md](docs/std.md) for the complete API reference.

## Examples

The `examples/` directory contains runnable examples demonstrating various features:

| Example | Description |
|---------|-------------|
| [`basic_strings.py`](examples/basic_strings.py) | String manipulation basics |
| [`goroutines.py`](examples/goroutines.py) | Go-style concurrency with WaitGroup and GoGroup |
| [`async_channels.py`](examples/async_channels.py) | Async channels with asyncio integration |
| [`concurrent_patterns.py`](examples/concurrent_patterns.py) | Common concurrency patterns (fan-out, pipeline, worker pool) |
| [`result_types.py`](examples/result_types.py) | Error handling with Result[T, E] types |
| [`json_processing.py`](examples/json_processing.py) | JSON encoding/decoding |
| [`csv_etl.py`](examples/csv_etl.py) | CSV processing and ETL workflows |
| [`file_compression.py`](examples/file_compression.py) | Gzip and ZIP compression |
| [`hashing_crypto.py`](examples/hashing_crypto.py) | Cryptographic hashing (SHA256, MD5) |
| [`filepath_os.py`](examples/filepath_os.py) | File path operations |
| [`http_client.py`](examples/http_client.py) | HTTP client usage |
| [`pipeline.py`](examples/pipeline.py) | Data pipeline patterns |
| [`task_queue.py`](examples/task_queue.py) | Task queue implementation |
| [`web_scraper.py`](examples/web_scraper.py) | Concurrent web scraping |
| [`templating.py`](examples/templating.py) | Text templating |

Run any example with:
```bash
uv run python examples/basic_strings.py
```

## Benchmarks

```
Operation               Python      Goated      Speedup
-------------------------------------------------------
JSON parse (1MB)        45.2ms      8.1ms       5.6x
SHA256 (10MB)           89.3ms      12.4ms      7.2x
Gzip compress (5MB)     234ms       41ms        5.7x
String split (1M ops)   1.2s        0.18s       6.7x
Regex match (100K)      890ms       95ms        9.4x
```

## How It Works

1. **Go Shared Library**: Go code compiled with `-buildmode=c-shared`
2. **Handle-Based FFI**: No raw pointers cross the boundary (GC-safe)
3. **ctypes Binding**: Zero-dependency Python FFI
4. **Code Generation**: Bindings auto-generated from Go source

## Development

```bash
# Setup
make dev

# Build
make build

# Test
make test

# Lint
make lint
```

## Code Generator

GOATED includes a code generator that parses Go stdlib packages and generates FFI bindings automatically.

### Building the Generator

```bash
make gen-build
```

### Usage

```bash
# Show bindable functions in a package
make generator PKG=strings

# Generate Go FFI code
make generator PKG=strings GO_OUT=golib/strings_gen.go

# Generate Python bindings
make generator PKG=strings PY_OUT=goated/std/strings_gen.py

# Generate both
make generator PKG=bytes GO_OUT=golib/bytes_gen.go PY_OUT=goated/std/bytes_gen.py
```

### Direct CLI Usage

```bash
cd generator
./goated-gen -pkg strings                    # List bindable functions
./goated-gen -pkg strings -go-out /tmp/x.go  # Generate Go code
./goated-gen -pkg strings -py-out /tmp/x.py  # Generate Python code
```

The generator:
- Parses Go AST to extract exported functions
- Filters to only FFI-compatible signatures (basic types, slices)
- Generates Go CGO export functions
- Generates Python ctypes bindings with docstrings

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*GOATED: Because your Python deserves to be the Greatest Of All Time, Expedited and Developed.*
