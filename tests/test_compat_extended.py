"""Tests for extended compat modules: difflib, textwrap, ipaddress, fnmatch,
colorsys, email, uuid, and the Go HTTP server."""

from __future__ import annotations

import os
import time


class TestCompatDifflib:
    def test_unified_diff_basic(self):
        from goated.compat import difflib

        a = ["line 1\n", "line 2\n", "line 3\n"]
        b = ["line 1\n", "line 2 modified\n", "line 3\n"]
        result = list(difflib.unified_diff(a, b, fromfile="a.txt", tofile="b.txt"))
        assert len(result) > 0

    def test_get_close_matches(self):
        from goated.compat import difflib

        result = difflib.get_close_matches("appel", ["ape", "apple", "peach"])
        assert "apple" in result

    def test_sequence_matcher(self):
        from goated.compat import difflib

        s = difflib.SequenceMatcher(None, "abcd", "bcde")
        assert 0 < s.ratio() < 1


class TestCompatTextwrap:
    def test_fill(self):
        from goated.compat import textwrap

        text = "hello world this is a test " * 10
        result = textwrap.fill(text, width=40)
        for line in result.split("\n"):
            assert len(line) <= 40

    def test_wrap(self):
        from goated.compat import textwrap

        text = "hello world this is a test " * 10
        result = textwrap.wrap(text, width=40)
        assert isinstance(result, list)
        assert len(result) > 1

    def test_dedent(self):
        from goated.compat import textwrap

        text = "    hello\n    world"
        result = textwrap.dedent(text)
        assert result == "hello\nworld"


class TestCompatIpaddress:
    def test_ip_address(self):
        from goated.compat import ipaddress

        ip = ipaddress.ip_address("192.168.1.1")
        assert str(ip) == "192.168.1.1"

    def test_ip_network(self):
        from goated.compat import ipaddress

        net = ipaddress.ip_network("10.0.0.0/8")
        assert ipaddress.ip_address("10.1.2.3") in net

    def test_is_valid_ip(self):
        from goated.compat import ipaddress

        assert ipaddress.is_valid("192.168.1.1") is True
        assert ipaddress.is_valid("not_an_ip") is False

    def test_ipv6(self):
        from goated.compat import ipaddress

        ip = ipaddress.ip_address("::1")
        assert str(ip) == "::1"


class TestCompatFnmatch:
    def test_fnmatch(self):
        from goated.compat import fnmatch

        assert fnmatch.fnmatch("test.py", "*.py") is True
        assert fnmatch.fnmatch("test.txt", "*.py") is False

    def test_filter(self):
        from goated.compat import fnmatch

        files = ["test.py", "main.py", "readme.txt", "config.yaml"]
        result = fnmatch.filter(files, "*.py")
        assert result == ["test.py", "main.py"]

    def test_translate(self):
        from goated.compat import fnmatch

        pattern = fnmatch.translate("*.py")
        assert isinstance(pattern, str)


class TestCompatColorsys:
    def test_rgb_to_hsv(self):
        import colorsys as stdlib

        from goated.compat import colorsys

        r, g, b = 0.5, 0.3, 0.8
        expected = stdlib.rgb_to_hsv(r, g, b)
        result = colorsys.rgb_to_hsv(r, g, b)
        for e, r in zip(expected, result):
            assert abs(e - r) < 0.001

    def test_hsv_to_rgb(self):
        import colorsys as stdlib

        from goated.compat import colorsys

        h, s, v = 0.75, 0.625, 0.8
        expected = stdlib.hsv_to_rgb(h, s, v)
        result = colorsys.hsv_to_rgb(h, s, v)
        for e, r in zip(expected, result):
            assert abs(e - r) < 0.001


class TestCompatUuid:
    def test_uuid4(self):
        from goated.compat import uuid

        u = uuid.uuid4()
        s = str(u)
        assert len(s) == 36
        assert s[8] == "-"
        assert s[14] == "4"  # version 4

    def test_uuid4_unique(self):
        from goated.compat import uuid

        uuids = {str(uuid.uuid4()) for _ in range(100)}
        assert len(uuids) == 100

    def test_batch_uuid4(self):
        from goated.compat import uuid

        if hasattr(uuid, "batch_uuid4"):
            result = uuid.batch_uuid4(100)
            assert len(result) == 100
            assert len(set(result)) == 100


class TestGoServer:
    def test_server_lifecycle(self):
        from goated.server import GoServer

        srv = GoServer("127.0.0.1:0")  # port 0 = auto-assign
        # Just test construction
        assert srv is not None

    def test_server_context_manager(self):
        """Test that server can start and stop."""
        from goated.server import GoServer

        srv = GoServer("127.0.0.1:19876")
        srv.route("/test", "hello")
        srv.start()
        time.sleep(0.05)
        srv.stop()
