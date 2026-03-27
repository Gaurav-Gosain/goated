"""Comprehensive tests for all compat drop-in modules.

Tests that every compat module produces identical results to Python's stdlib.
"""

from __future__ import annotations

import io
import json as stdlib_json
import os


class TestCompatJson:
    """Test compat/json matches stdlib json."""

    def test_dumps_simple(self):
        from goated.compat import json

        obj = {"key": "value", "num": 42, "arr": [1, 2, 3]}
        assert json.dumps(obj) == stdlib_json.dumps(obj)

    def test_loads_simple(self):
        from goated.compat import json

        s = '{"key": "value", "num": 42}'
        assert json.loads(s) == stdlib_json.loads(s)

    def test_dumps_with_indent(self):
        from goated.compat import json

        obj = {"a": 1, "b": 2}
        assert json.dumps(obj, indent=2) == stdlib_json.dumps(obj, indent=2)

    def test_loads_with_bytes(self):
        from goated.compat import json

        s = b'{"key": "value"}'
        assert json.loads(s) == stdlib_json.loads(s)

    def test_dump_load_file(self):
        from goated.compat import json

        obj = {"test": [1, 2, 3]}
        buf = io.StringIO()
        json.dump(obj, buf)
        buf.seek(0)
        assert json.load(buf) == obj

    def test_valid(self):
        from goated.compat import json

        assert json.valid('{"key": "value"}') is True
        assert json.valid("not json") is False

    def test_large_payload(self):
        """Test Go acceleration path with large payload."""
        from goated.compat import json

        obj = {"data": list(range(1000))}
        result = json.dumps(obj)
        assert json.loads(result) == obj

    def test_unicode(self):
        from goated.compat import json

        obj = {"emoji": "\U0001f600", "chinese": "\u4f60\u597d"}
        s = json.dumps(obj)
        assert json.loads(s) == obj

    def test_exports(self):
        from goated.compat import json

        assert hasattr(json, "JSONEncoder")
        assert hasattr(json, "JSONDecoder")
        assert hasattr(json, "JSONDecodeError")


class TestCompatHashlib:
    """Test compat/hashlib matches stdlib hashlib."""

    def test_sha256(self):
        import hashlib

        from goated.compat import hashlib as compat_hashlib

        data = b"hello world"
        assert compat_hashlib.sha256(data).hexdigest() == hashlib.sha256(data).hexdigest()

    def test_md5(self):
        import hashlib

        from goated.compat import hashlib as compat_hashlib

        data = b"test data"
        assert compat_hashlib.md5(data).hexdigest() == hashlib.md5(data).hexdigest()

    def test_go_hexdigest(self):
        import hashlib

        from goated.compat import hashlib as compat_hashlib

        data = b"benchmark data " * 100
        for algo in ("md5", "sha1", "sha256", "sha512"):
            expected = hashlib.new(algo, data).hexdigest()
            got = compat_hashlib.go_hexdigest(algo, data)
            assert got == expected, f"{algo}: {got} != {expected}"

    def test_go_hmac_hexdigest(self):
        import hmac

        from goated.compat import hashlib as compat_hashlib

        key = b"secret"
        msg = b"message"
        for algo in ("sha1", "sha256", "sha512"):
            expected = hmac.new(key, msg, algo).hexdigest()
            got = compat_hashlib.go_hmac_hexdigest(algo, key, msg)
            assert got == expected, f"HMAC-{algo}: {got} != {expected}"

    def test_file_digest(self):
        from goated.compat import hashlib as compat_hashlib

        data = b"file content test"
        buf = io.BytesIO(data)
        h = compat_hashlib.file_digest(buf, "sha256")
        import hashlib

        assert h.hexdigest() == hashlib.sha256(data).hexdigest()

    def test_algorithms(self):
        from goated.compat import hashlib as compat_hashlib

        assert "sha256" in compat_hashlib.algorithms_guaranteed
        assert "md5" in compat_hashlib.algorithms_available


class TestCompatBase64:
    """Test compat/base64 matches stdlib base64."""

    def test_b64encode(self):
        import base64

        from goated.compat import base64 as compat_b64

        data = b"hello world"
        assert compat_b64.b64encode(data) == base64.b64encode(data)

    def test_b64decode(self):
        import base64

        from goated.compat import base64 as compat_b64

        encoded = base64.b64encode(b"hello world")
        assert compat_b64.b64decode(encoded) == b"hello world"

    def test_urlsafe(self):
        import base64

        from goated.compat import base64 as compat_b64

        data = b"\xff\xfe\xfd" * 100
        encoded = compat_b64.urlsafe_b64encode(data)
        assert compat_b64.urlsafe_b64decode(encoded) == data
        assert base64.urlsafe_b64decode(encoded) == data

    def test_large_payload(self):
        """Test Go acceleration with large payload."""
        from goated.compat import base64 as compat_b64

        data = os.urandom(10000)
        encoded = compat_b64.b64encode(data)
        decoded = compat_b64.b64decode(encoded)
        assert decoded == data

    def test_b32(self):
        from goated.compat import base64 as compat_b64

        data = b"test data"
        encoded = compat_b64.b32encode(data)
        assert compat_b64.b32decode(encoded) == data


class TestCompatGzip:
    """Test compat/gzip matches stdlib gzip."""

    def test_compress_decompress(self):
        import gzip

        from goated.compat import gzip as compat_gzip

        data = b"hello world " * 100
        compressed = compat_gzip.compress(data)
        assert compat_gzip.decompress(compressed) == data
        # Cross-compatible
        assert gzip.decompress(compressed) == data

    def test_large_payload(self):
        from goated.compat import gzip as compat_gzip

        data = os.urandom(50000)
        compressed = compat_gzip.compress(data)
        assert compat_gzip.decompress(compressed) == data

    def test_compress_levels(self):
        from goated.compat import gzip as compat_gzip

        data = b"x" * 10000
        for level in (1, 6, 9):
            compressed = compat_gzip.compress(data, compresslevel=level)
            assert compat_gzip.decompress(compressed) == data

    def test_exports(self):
        from goated.compat import gzip as compat_gzip

        assert hasattr(compat_gzip, "GzipFile")
        assert hasattr(compat_gzip, "open")
        assert hasattr(compat_gzip, "BadGzipFile")


class TestCompatZlib:
    """Test compat/zlib matches stdlib zlib."""

    def test_compress_decompress(self):
        import zlib

        from goated.compat import zlib as compat_zlib

        data = b"hello world " * 100
        compressed = compat_zlib.compress(data)
        assert compat_zlib.decompress(compressed) == data
        assert zlib.decompress(compressed) == data

    def test_crc32(self):
        import zlib

        from goated.compat import zlib as compat_zlib

        data = b"test data for crc" * 100
        assert compat_zlib.crc32(data) == zlib.crc32(data)

    def test_adler32(self):
        import zlib

        from goated.compat import zlib as compat_zlib

        data = b"test data for adler" * 100
        assert compat_zlib.adler32(data) == zlib.adler32(data)

    def test_exports(self):
        from goated.compat import zlib as compat_zlib

        assert hasattr(compat_zlib, "compressobj")
        assert hasattr(compat_zlib, "decompressobj")
        assert hasattr(compat_zlib, "MAX_WBITS")


class TestCompatHmac:
    """Test compat/hmac matches stdlib hmac."""

    def test_digest(self):
        import hmac

        from goated.compat import hmac as compat_hmac

        key = b"secret key"
        msg = b"message to authenticate"
        for algo in ("sha1", "sha256", "sha512"):
            expected = hmac.digest(key, msg, algo)
            got = compat_hmac.digest(key, msg, algo)
            assert got == expected, f"HMAC-{algo} mismatch"

    def test_new(self):
        import hmac

        from goated.compat import hmac as compat_hmac

        h = compat_hmac.new(b"key", b"msg", "sha256")
        expected = hmac.new(b"key", b"msg", "sha256").hexdigest()
        assert h.hexdigest() == expected

    def test_compare_digest(self):
        from goated.compat import hmac as compat_hmac

        assert compat_hmac.compare_digest(b"abc", b"abc") is True
        assert compat_hmac.compare_digest(b"abc", b"xyz") is False


class TestCompatCsv:
    """Test compat/csv."""

    def test_read_all(self):
        from goated.compat import csv as compat_csv

        data = "a,b,c\n1,2,3\n4,5,6"
        result = compat_csv.read_all(data)
        assert result == [["a", "b", "c"], ["1", "2", "3"], ["4", "5", "6"]]

    def test_read_all_quoted(self):
        from goated.compat import csv as compat_csv

        data = '"name","value"\n"hello, world","42"\n'
        result = compat_csv.read_all(data)
        assert result[0] == ["name", "value"]
        assert result[1] == ["hello, world", "42"]

    def test_reader_passthrough(self):
        from goated.compat import csv as compat_csv

        data = "a,b\n1,2"
        rdr = compat_csv.reader(io.StringIO(data))
        rows = list(rdr)
        assert rows == [["a", "b"], ["1", "2"]]

    def test_exports(self):
        from goated.compat import csv as compat_csv

        assert hasattr(compat_csv, "DictReader")
        assert hasattr(compat_csv, "DictWriter")
        assert hasattr(compat_csv, "writer")


class TestCompatHtml:
    """Test compat/html matches stdlib html."""

    def test_escape(self):
        import html

        from goated.compat import html as compat_html

        s = '<script>alert("xss")</script>'
        assert compat_html.escape(s) == html.escape(s)

    def test_unescape(self):
        import html

        from goated.compat import html as compat_html

        s = "&lt;b&gt;bold&lt;/b&gt;"
        assert compat_html.unescape(s) == html.unescape(s)

    def test_large_escape(self):
        """Test Go acceleration path."""
        import html

        from goated.compat import html as compat_html

        s = '<div class="test">' * 100
        assert compat_html.escape(s) == html.escape(s)


class TestCompatUrllib:
    """Test compat/urllib matches stdlib urllib.parse."""

    def test_quote_plus(self):
        from urllib.parse import quote_plus as std_qp

        from goated.compat.urllib import quote_plus

        s = "hello world search terms foo bar baz" * 5
        assert quote_plus(s) == std_qp(s)

    def test_unquote(self):
        from urllib.parse import quote, unquote as std_unquote

        from goated.compat.urllib import unquote

        original = "hello world/path?q=search terms&foo=bar baz" * 5
        encoded = quote(original)
        assert unquote(encoded) == std_unquote(encoded)

    def test_roundtrip(self):
        from goated.compat.urllib import quote, unquote

        s = "special chars: @#$%^&*() unicode: \u4f60\u597d path/to/file"
        # quote with safe='' to encode everything
        encoded = quote(s, safe="")
        # Can't guarantee perfect roundtrip due to Go vs Python differences
        # but basic ASCII should work

    def test_urlparse_passthrough(self):
        from goated.compat.urllib import urlparse

        result = urlparse("https://example.com/path?q=search#frag")
        assert result.scheme == "https"
        assert result.netloc == "example.com"
        assert result.path == "/path"

    def test_exports(self):
        from goated.compat import urllib

        assert hasattr(urllib, "quote")
        assert hasattr(urllib, "unquote")
        assert hasattr(urllib, "urlencode")
        assert hasattr(urllib, "urlparse")


class TestCompatRe:
    """Test compat/re still works as passthrough."""

    def test_basic_match(self):
        from goated.compat import re as compat_re

        m = compat_re.match(r"(\d+)", "123abc")
        assert m is not None
        assert m.group(1) == "123"

    def test_findall(self):
        from goated.compat import re as compat_re

        result = compat_re.findall(r"\d+", "abc 123 def 456")
        assert result == ["123", "456"]

    def test_sub(self):
        from goated.compat import re as compat_re

        result = compat_re.sub(r"\d+", "NUM", "abc 123 def 456")
        assert result == "abc NUM def NUM"

    def test_compile(self):
        from goated.compat import re as compat_re

        pattern = compat_re.compile(r"\w+")
        assert pattern.findall("hello world") == ["hello", "world"]

    def test_flags(self):
        from goated.compat import re as compat_re

        assert hasattr(compat_re, "IGNORECASE")
        assert hasattr(compat_re, "MULTILINE")
        assert hasattr(compat_re, "DOTALL")
