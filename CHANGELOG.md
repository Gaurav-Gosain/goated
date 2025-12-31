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
- GoGroup `__init__` optimized by removing unused fields (65% faster creation: ~3μs → 1μs)
- GoGroup/ErrGroup `__exit__` optimized: use `shutdown(wait=True)` for owned executors (eliminates `futures_wait` overhead, closes 14% performance gap vs raw TPE)

### Fixed
- `filepath.EvalSymlinks` now correctly resolves symlinks
- `filepath.Match` pattern matching edge cases
- `path.Dir` trailing slash handling
- `strings.ToTitle` now uses `s.upper()` for correct behavior

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

[Unreleased]: https://github.com/Gaurav-Gosain/goated/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Gaurav-Gosain/goated/releases/tag/v0.1.0
