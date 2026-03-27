"""Drop-in replacements for Python standard library modules.

These modules provide the same API as Python's stdlib but use Go implementations
under the hood when available for better performance on large payloads.

Available modules:
    - json: JSON encoding/decoding (Go-accelerated validation/compaction)
    - hashlib: Hashing (Go-accelerated one-shot digests)
    - base64: Base64/URL encoding (Go-accelerated for large data)
    - re: Regular expressions (Go RE2 for compatible patterns)
    - gzip: Gzip compression (Go-accelerated compress/decompress)
    - zlib: Zlib compression (Go-accelerated compress/decompress/checksums)
    - hmac: HMAC authentication (Go-accelerated one-shot digests)
    - struct: Struct packing/unpacking (passthrough to Python)
    - statistics: Statistics functions (Go-accelerated for large datasets)
    - heapq: Heap queue (Go-accelerated nlargest/nsmallest)
    - bisect: Bisection algorithm (passthrough to Python)
    - csv: CSV parsing (Go-accelerated bulk read_all)
    - html: HTML escaping (Go-accelerated escape/unescape)
    - difflib: Diff generation (Go-accelerated unified diff)
    - textwrap: Text wrapping (Go-accelerated fill/wrap)
    - ipaddress: IP address parsing (Go-accelerated validation)
    - fnmatch: Filename matching (Go-accelerated pattern matching)
    - colorsys: Color conversions (Go-accelerated batch conversions)
    - email_utils: Email parsing (Go-accelerated address parsing)
    - uuid: UUID generation (Go-accelerated uuid4)

Usage:
    from goated.compat import json
    data = json.loads('{"key": "value"}')
"""

__all__ = [
    "json",
    "hashlib",
    "base64",
    "re",
    "gzip",
    "zlib",
    "hmac",
    "struct",
    "statistics",
    "heapq",
    "bisect",
    "csv",
    "html",
    "difflib",
    "textwrap",
    "ipaddress",
    "fnmatch",
    "colorsys",
    "email_utils",
    "uuid",
]
