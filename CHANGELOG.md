# Changelog

All notable changes to GOATED will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Concurrency optimizations for Chan, GoGroup, and ErrGroup
- Chan now uses `deque` + `Condition` instead of `queue.Queue` (1.5x faster)
- GoGroup/ErrGroup with limits now use native `ThreadPoolExecutor`
- `GoGroup.go_map(fn, items)` - batch operation matching TPE.map() performance
- `GoGroup.go_batch(fn, args_list)` - efficient multi-task submission
- `GoGroup.go1(fn, arg)` - optimized single-argument task submission
- `GoGroup.executor` property - direct executor access for zero-overhead submission

### Changed
- Mutex `__enter__`/`__exit__` now use direct lock operations
- GoGroup `__init__` optimized by removing unused fields (65% faster creation: ~3us -> 1us)
- GoGroup/ErrGroup `__exit__` optimized: use `shutdown(wait=True)` for owned executors (eliminates `futures_wait` overhead, closes 14% performance gap vs raw TPE)

### Fixed
- `filepath.EvalSymlinks` now correctly resolves symlinks
- `filepath.Match` pattern matching edge cases
- `path.Dir` trailing slash handling
- `strings.ToTitle` now uses `s.upper()` for correct behavior

## [0.2.0] - 2026-03-26

### Added
- 21 drop-in compat modules: json, hashlib, base64, re, gzip, zlib, hmac, struct, statistics, heapq, bisect, csv, html, difflib, textwrap, ipaddress, fnmatch, colorsys, email_utils, uuid, urllib
- 279 Go FFI exports across 33 Go source files
- `goated.batch` module with batch_sha256, batch_sha512, batch_md5, batch_gzip_compress, batch_gzip_decompress, batch_b64encode, batch_b64decode, batch_json_valid, batch_regex_match
- `goated.server` module with GoServer, FileServer, BenchServer for Go net/http servers
- cffi API-mode compiled extension (`_build_cffi.py`) for 3-5x faster FFI calls
- Concurrency: Semaphore for bounding concurrent access
- Concurrency: `pipe()` for channel pipeline stages
- Concurrency: `merge()` for fan-in across multiple channels
- Concurrency: `fan_out()` for distributing work to N consumers
- True unbuffered channel rendezvous semantics
- Proper Select with condition-variable notification (no spin-wait)
- RWMutex with writer preference
- Pool with thread-local fast path
- New Go exports: gzip, zlib, base64, hmac, csv, html, url, sort, time, regexp, difflib, textwrap, ipaddress, email, fnmatch, colorsys, uuid, httpserver, batch operations
- Comprehensive test suite (1064 tests total)
- Benchmarks: bench_compat.py, bench_pure_python.py

### Changed
- Upgraded go.mod from Go 1.21 to Go 1.23
- `_core.py` now supports cffi API mode with ctypes fallback
- Smart thresholds: auto-fallback to Python C extensions when they are faster for small payloads
- `goroutine` decorator uses `functools.wraps` for proper function metadata
- Thread-safe `get_lib()` singleton for shared library loading

### Fixed
- Select spin-wait replaced with condition-variable notification
- Chan/FastChan iterators use proper blocking (no polling)
- Unbuffered channels now have true rendezvous semantics
- RWMutex fixed in both `std/sync.py` and `runtime/api.py`
- Removed unused strconv types

## [0.1.0] - 2025-12-30

### Added
- Initial release
- Go stdlib bindings via FFI (ctypes)
- Handle-based memory management (GC-safe)
- Result[T, E] error handling inspired by Rust
- Three API styles: Direct Mapping, Pythonic Wrappers, Drop-in Replacement
- Code generator for auto-generating bindings from Go source

### Standard Library Modules
- `strings` - String manipulation (Split, Join, Contains, Replace, etc.)
- `bytes` - Byte slice operations
- `strconv` - String conversions (Atoi, Itoa, ParseInt, etc.)
- `encoding/json` - JSON encoding/decoding
- `encoding/base64` - Base64 encoding
- `encoding/csv` - CSV reading/writing
- `encoding/xml` - XML parsing
- `encoding/binary` - Binary encoding
- `crypto/sha256` - SHA-256 hashing
- `crypto/md5` - MD5 hashing
- `compress/gzip` - Gzip compression
- `compress/zip` - ZIP archive support
- `path` - Path manipulation
- `path/filepath` - OS-specific path operations
- `time` - Time and duration handling
- `regexp` - Regular expressions
- `sort` - Sorting algorithms
- `rand` - Random number generation
- `log` - Logging
- `html` - HTML escaping
- `mime` - MIME type handling
- `net` - Network operations
- `net/url` - URL parsing
- `text/template` - Text templating

### Concurrency (goated.runtime)
- `go()` - Spawn goroutines
- `WaitGroup` - Synchronization primitive
- `GoGroup` - Automatic goroutine tracking with context manager
- `ErrGroup` - Error-propagating goroutine groups
- `Chan[T]` - Typed channels with send/receive
- `FastChan[T]` - High-throughput channel variant
- `Mutex` - Mutual exclusion lock
- `Select` - Select on multiple channels
- `parallel_map` - Parallel list transformation
- M:N scheduler with work-stealing

### Async Support (goated.channel)
- `Channel[T]` - Async channels for asyncio integration
- Full async iteration support

[Unreleased]: https://github.com/Gaurav-Gosain/goated/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Gaurav-Gosain/goated/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Gaurav-Gosain/goated/releases/tag/v0.1.0
