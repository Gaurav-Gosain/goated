"""Drop-in replacements: change your imports, keep your code.

GOATED provides 21 modules that are API-compatible with Python's stdlib.
Just swap the import line and get Go-powered performance for free.
"""

# Before: import json
# After:
from goated.compat import json, html, gzip, hashlib

# -- JSON: same API, Go-accelerated validation and compaction --
data = json.loads('{"key": "value", "numbers": [1, 2, 3]}')
print("JSON parsed:", data)

encoded = json.dumps(data, indent=2)
print("JSON encoded:\n", encoded)

# -- HTML: 16x faster unescape --
safe = html.escape("<script>alert('xss')</script>")
print("Escaped HTML:", safe)

original = html.unescape("&lt;div&gt;Hello &amp; welcome&lt;/div&gt;")
print("Unescaped HTML:", original)

# -- Gzip: Go-powered compression --
payload = b"The quick brown fox jumps over the lazy dog. " * 100
compressed = gzip.compress(payload)
decompressed = gzip.decompress(compressed)
print(f"Gzip: {len(payload)} bytes -> {len(compressed)} bytes -> {len(decompressed)} bytes")
assert decompressed == payload

# -- Hashlib: Go one-shot hashing --
digest = hashlib.sha256(b"hello world").hexdigest()
print("SHA256:", digest)

md5_digest = hashlib.md5(b"hello world").hexdigest()
print("MD5:", md5_digest)

# -- More modules available --
from goated.compat import textwrap, ipaddress, fnmatch, uuid

# textwrap: 44x faster
wrapped = textwrap.fill(
    "GOATED provides drop-in replacements for Python stdlib modules, "
    "backed by Go implementations for better performance.",
    width=40,
)
print("\nWrapped text:")
print(wrapped)

# ipaddress: Go-accelerated validation
addr = ipaddress.ip_address("192.168.1.1")
print(f"\nIP address: {addr}, is_private={addr.is_private}")

# fnmatch: Go-accelerated pattern matching
print("fnmatch('readme.md', '*.md'):", fnmatch.fnmatch("readme.md", "*.md"))

# uuid: Go-accelerated generation
print("UUID4:", uuid.uuid4())
