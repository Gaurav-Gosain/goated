"""Comprehensive tests for Go type wrappers.

Tests cover:
- GoSlice creation, access, iteration
- GoString encoding/decoding
- GoMap dict-like interface
"""

import ctypes

import pytest

from goated.types import GoMap, GoSlice, GoString


class TestGoSlice:
    def test_from_list_empty(self):
        s = GoSlice.from_list([])
        assert len(s) == 0
        assert s.to_list() == []

    def test_from_list_integers(self):
        s = GoSlice.from_list([1, 2, 3, 4, 5])
        assert len(s) == 5
        assert s.to_list() == [1, 2, 3, 4, 5]

    def test_from_list_floats(self):
        s = GoSlice.from_list([1.5, 2.5, 3.5], elem_type=ctypes.c_double)
        assert len(s) == 3
        result = s.to_list()
        assert result[0] == pytest.approx(1.5)
        assert result[1] == pytest.approx(2.5)
        assert result[2] == pytest.approx(3.5)

    def test_from_bytes(self):
        s = GoSlice.from_bytes(b"hello")
        assert len(s) == 5
        assert s.to_bytes() == b"hello"

    def test_from_bytes_empty(self):
        s = GoSlice.from_bytes(b"")
        assert len(s) == 0
        assert s.to_bytes() == b""

    def test_indexing_positive(self):
        s = GoSlice.from_list([10, 20, 30, 40, 50])
        assert s[0] == 10
        assert s[2] == 30
        assert s[4] == 50

    def test_indexing_negative(self):
        s = GoSlice.from_list([10, 20, 30, 40, 50])
        assert s[-1] == 50
        assert s[-2] == 40
        assert s[-5] == 10

    def test_indexing_out_of_bounds(self):
        s = GoSlice.from_list([1, 2, 3])
        with pytest.raises(IndexError):
            _ = s[3]
        with pytest.raises(IndexError):
            _ = s[-4]

    def test_iteration(self):
        s = GoSlice.from_list([1, 2, 3])
        items = list(s)
        assert items == [1, 2, 3]

    def test_contains(self):
        s = GoSlice.from_list([1, 2, 3, 4, 5])
        assert 3 in s
        assert 10 not in s

    def test_capacity(self):
        s = GoSlice.from_list([1, 2, 3])
        assert s.capacity >= 3

    def test_equality_with_slice(self):
        s1 = GoSlice.from_list([1, 2, 3])
        s2 = GoSlice.from_list([1, 2, 3])
        assert s1 == s2

    def test_equality_with_list(self):
        s = GoSlice.from_list([1, 2, 3])
        assert s == [1, 2, 3]

    def test_repr_short(self):
        s = GoSlice.from_list([1, 2, 3])
        assert "GoSlice" in repr(s)
        assert "1" in repr(s)

    def test_repr_long(self):
        s = GoSlice.from_list(list(range(20)))
        r = repr(s)
        assert "GoSlice" in r
        assert "20 items" in r

    def test_to_struct(self):
        s = GoSlice.from_list([1, 2, 3])
        struct = s.to_struct()
        assert struct.len == 3
        assert struct.cap == 3


class TestGoString:
    def test_from_str_empty(self):
        gs = GoString.from_str("")
        assert str(gs) == ""
        assert len(gs) == 0

    def test_from_str_ascii(self):
        gs = GoString.from_str("hello")
        assert str(gs) == "hello"
        assert len(gs) == 5

    def test_from_str_unicode(self):
        gs = GoString.from_str("hello \U0001f600 world")
        assert str(gs) == "hello \U0001f600 world"

    def test_to_str(self):
        gs = GoString.from_str("test string")
        assert gs.to_str() == "test string"

    def test_to_bytes(self):
        gs = GoString.from_str("hello")
        assert gs.to_bytes() == b"hello"

    def test_to_bytes_unicode(self):
        gs = GoString.from_str("\U0001f600")
        assert gs.to_bytes() == "\U0001f600".encode()

    def test_len_bytes_not_chars(self):
        gs = GoString.from_str("\U0001f600")
        assert len(gs) == 4

    def test_equality_with_gostring(self):
        gs1 = GoString.from_str("hello")
        gs2 = GoString.from_str("hello")
        assert gs1 == gs2

    def test_equality_with_str(self):
        gs = GoString.from_str("hello")
        assert gs == "hello"

    def test_equality_with_bytes(self):
        gs = GoString.from_str("hello")
        assert gs == b"hello"

    def test_hash(self):
        gs1 = GoString.from_str("hello")
        gs2 = GoString.from_str("hello")
        assert hash(gs1) == hash(gs2)

    def test_repr(self):
        gs = GoString.from_str("test")
        assert "GoString" in repr(gs)

    def test_to_struct(self):
        gs = GoString.from_str("hello")
        struct = gs.to_struct()
        assert struct.n == 5


class TestGoMap:
    def test_from_dict_empty(self):
        m = GoMap.from_dict({})
        assert len(m) == 0
        assert m.to_dict() == {}

    def test_from_dict_string_int(self):
        m = GoMap.from_dict({"a": 1, "b": 2, "c": 3})
        assert len(m) == 3
        assert m["a"] == 1
        assert m["b"] == 2
        assert m["c"] == 3

    def test_to_dict(self):
        original = {"x": 10, "y": 20}
        m = GoMap.from_dict(original)
        assert m.to_dict() == original

    def test_getitem(self):
        m = GoMap.from_dict({"key": 42})
        assert m["key"] == 42

    def test_getitem_missing(self):
        m = GoMap.from_dict({"key": 42})
        with pytest.raises(KeyError):
            _ = m["missing"]

    def test_setitem(self):
        m = GoMap.from_dict({"a": 1})
        m["b"] = 2
        assert m["b"] == 2
        assert len(m) == 2

    def test_delitem(self):
        m = GoMap.from_dict({"a": 1, "b": 2})
        del m["a"]
        assert "a" not in m
        assert len(m) == 1

    def test_contains(self):
        m = GoMap.from_dict({"key": 1})
        assert "key" in m
        assert "other" not in m

    def test_len(self):
        m = GoMap.from_dict({"a": 1, "b": 2, "c": 3})
        assert len(m) == 3

    def test_iter(self):
        m = GoMap.from_dict({"a": 1, "b": 2})
        keys = set(m)
        assert keys == {"a", "b"}

    def test_keys(self):
        m = GoMap.from_dict({"a": 1, "b": 2})
        assert set(m.keys()) == {"a", "b"}

    def test_values(self):
        m = GoMap.from_dict({"a": 1, "b": 2})
        assert set(m.values()) == {1, 2}

    def test_items(self):
        m = GoMap.from_dict({"a": 1, "b": 2})
        assert set(m.items()) == {("a", 1), ("b", 2)}

    def test_get_existing(self):
        m = GoMap.from_dict({"key": 42})
        assert m.get("key") == 42

    def test_get_missing_default(self):
        m = GoMap.from_dict({"key": 42})
        assert m.get("missing", 0) == 0

    def test_get_missing_none(self):
        m = GoMap.from_dict({"key": 42})
        assert m.get("missing") is None

    def test_equality_with_gomap(self):
        m1 = GoMap.from_dict({"a": 1})
        m2 = GoMap.from_dict({"a": 1})
        assert m1 == m2

    def test_equality_with_dict(self):
        m = GoMap.from_dict({"a": 1, "b": 2})
        assert m == {"a": 1, "b": 2}

    def test_repr(self):
        m = GoMap.from_dict({"key": 1})
        assert "GoMap" in repr(m)
