"""Go standard library bindings - Direct mapping style.

This module provides access to Go's standard library with Go-style naming.
Functions and types maintain their original Go names and signatures.

Available packages:
- strings: String manipulation functions
- bytes: Byte slice operations
- strconv: String conversions
- json: JSON encoding/decoding
- crypto: Cryptographic functions
- path: URL path manipulation
- filepath: File path manipulation
- regexp: Regular expressions
- time: Time and duration
- math: Mathematical functions
- unicode: Unicode character properties
- utf8: UTF-8 encoding utilities
- sort: Sorting algorithms
- base64: Base64 encoding/decoding
- hex: Hexadecimal encoding/decoding
- io: I/O primitives
- bufio: Buffered I/O
- fmt: Formatted I/O
- errors: Error handling
- context: Context for cancellation/deadlines
- sync: Synchronization primitives
- url: URL parsing (net/url)
- os: OS operations (file, env)
- gzip: Gzip compression
- csv: CSV encoding/decoding
- xml: XML encoding/decoding
- html: HTML escaping
- rand: Random numbers
- log: Logging
- hash: Hash functions
- mime: MIME types
- http: HTTP client/server (net/http)
- zip: ZIP archive handling (archive/zip)
- template: Text templating (text/template)
- binary: Binary encoding (encoding/binary)
- net: Network primitives
- testing: Testing utilities
- parallel: Go parallel batch operations
- goroutine: Go-style concurrency primitives (go, WaitGroup, Chan, etc.)

Example:
    >>> from goated.std import strings, time, fmt
    >>>
    >>> # String operations
    >>> strings.Contains("hello world", "world")
    True
    >>>
    >>> # Time operations
    >>> now = time.Now()
    >>> fmt.Sprintf("Current time: %v", now)
    'Current time: 2024-01-15T10:30:00Z'
    >>>
    >>> # Sorting
    >>> from goated.std import sort
    >>> data = [3, 1, 4, 1, 5]
    >>> sort.Ints(data)
    >>> data
    [1, 1, 3, 4, 5]

"""

# Import available packages
# These are imported lazily to avoid loading the library until needed

__all__ = [
    "strings",
    "bytes",
    "strconv",
    "json",
    "crypto",
    "path",
    "filepath",
    "regexp",
    "unicode",
    "utf8",
    "time",
    "math",
    "sort",
    "base64",
    "hex",
    "io",
    "bufio",
    "fmt",
    "errors",
    "context",
    "sync",
    "url",
    "os",
    "gzip",
    "csv",
    "xml",
    "html",
    "rand",
    "log",
    "hash",
    "mime",
    "http",
    "zip",
    "template",
    "binary",
    "net",
    "testing",
    "parallel",
    "goroutine",
]


from types import ModuleType


def __getattr__(name: str) -> ModuleType:
    import importlib

    modules = {
        "strings": "goated.std.strings",
        "bytes": "goated.std.bytes",
        "strconv": "goated.std.strconv",
        "json": "goated.std.json",
        "crypto": "goated.std.crypto",
        "path": "goated.std.path",
        "filepath": "goated.std.filepath",
        "regexp": "goated.std.regexp",
        "unicode": "goated.std.unicode",
        "utf8": "goated.std.utf8",
        "time": "goated.std.time",
        "math": "goated.std.math",
        "sort": "goated.std.sort",
        "base64": "goated.std.base64",
        "hex": "goated.std.hex",
        "io": "goated.std.io",
        "bufio": "goated.std.bufio",
        "fmt": "goated.std.fmt",
        "errors": "goated.std.errors",
        "context": "goated.std.context",
        "sync": "goated.std.sync",
        "url": "goated.std.url",
        "os": "goated.std.goos",
        "gzip": "goated.std.gzip",
        "csv": "goated.std.csv",
        "xml": "goated.std.xml",
        "html": "goated.std.html",
        "rand": "goated.std.rand",
        "log": "goated.std.log",
        "hash": "goated.std.hash",
        "mime": "goated.std.mime",
        "http": "goated.std.http",
        "zip": "goated.std.zip",
        "template": "goated.std.template",
        "binary": "goated.std.binary",
        "net": "goated.std.net",
        "testing": "goated.std.testing",
        "parallel": "goated.std.parallel",
        "goroutine": "goated.std.goroutine",
    }

    if name in modules:
        return importlib.import_module(modules[name])
    raise AttributeError(f"module 'goated.std' has no attribute {name!r}")
