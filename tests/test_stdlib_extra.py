"""Tests for additional stdlib packages: bytes, strconv, json, crypto."""

import pytest

from goated.std import bytes as gobytes
from goated.std import crypto, strconv
from goated.std import json as gojson


class TestBytes:
    def test_contains(self):
        assert gobytes.Contains(b"hello", b"ell")
        assert not gobytes.Contains(b"hello", b"xyz")

    def test_count(self):
        assert gobytes.Count(b"cheese", b"e") == 3
        assert gobytes.Count(b"five", b"") == 5

    def test_equal(self):
        assert gobytes.Equal(b"hello", b"hello")
        assert not gobytes.Equal(b"hello", b"world")

    def test_compare(self):
        assert gobytes.Compare(b"a", b"b") == -1
        assert gobytes.Compare(b"b", b"a") == 1
        assert gobytes.Compare(b"a", b"a") == 0

    def test_has_prefix(self):
        assert gobytes.HasPrefix(b"hello", b"he")
        assert not gobytes.HasPrefix(b"hello", b"lo")

    def test_has_suffix(self):
        assert gobytes.HasSuffix(b"hello", b"lo")
        assert not gobytes.HasSuffix(b"hello", b"he")

    def test_index(self):
        assert gobytes.Index(b"hello", b"ll") == 2
        assert gobytes.Index(b"hello", b"xyz") == -1

    def test_last_index(self):
        assert gobytes.LastIndex(b"hello hello", b"hello") == 6

    def test_to_lower(self):
        assert gobytes.ToLower(b"HELLO") == b"hello"

    def test_to_upper(self):
        assert gobytes.ToUpper(b"hello") == b"HELLO"

    def test_trim_space(self):
        assert gobytes.TrimSpace(b"  hello  ") == b"hello"

    def test_repeat(self):
        assert gobytes.Repeat(b"ab", 3) == b"ababab"
        assert gobytes.Repeat(b"x", 0) == b""
        with pytest.raises(ValueError):
            gobytes.Repeat(b"x", -1)

    def test_replace(self):
        assert gobytes.Replace(b"oink oink oink", b"oink", b"moo", 2) == b"moo moo oink"

    def test_replace_all(self):
        assert gobytes.ReplaceAll(b"oink oink oink", b"oink", b"moo") == b"moo moo moo"


class TestStrconv:
    def test_atoi_success(self):
        result = strconv.Atoi("42")
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_atoi_failure(self):
        result = strconv.Atoi("not a number")
        assert result.is_err()

    def test_itoa(self):
        assert strconv.Itoa(42) == "42"
        assert strconv.Itoa(-123) == "-123"

    def test_parse_int(self):
        assert strconv.ParseInt("42").unwrap() == 42
        assert strconv.ParseInt("ff", 16).unwrap() == 255
        assert strconv.ParseInt("1010", 2).unwrap() == 10

    def test_parse_uint(self):
        assert strconv.ParseUint("42").unwrap() == 42
        assert strconv.ParseUint("-1").is_err()

    def test_parse_float(self):
        assert strconv.ParseFloat("3.14").unwrap() == pytest.approx(3.14)

    def test_parse_bool(self):
        assert strconv.ParseBool("true").unwrap() is True
        assert strconv.ParseBool("false").unwrap() is False
        assert strconv.ParseBool("1").unwrap() is True
        assert strconv.ParseBool("0").unwrap() is False
        assert strconv.ParseBool("invalid").is_err()

    def test_format_int(self):
        assert strconv.FormatInt(255, 16) == "ff"
        assert strconv.FormatInt(10, 2) == "1010"
        assert strconv.FormatInt(42, 10) == "42"

    def test_format_uint(self):
        assert strconv.FormatUint(255, 16) == "ff"

    def test_format_float(self):
        assert "3.14" in strconv.FormatFloat(3.14159, "f", 2)

    def test_format_bool(self):
        assert strconv.FormatBool(True) == "true"
        assert strconv.FormatBool(False) == "false"

    def test_quote(self):
        result = strconv.Quote("hello")
        assert "hello" in result

    def test_unquote(self):
        result = strconv.Unquote('"hello"')
        assert result.is_ok()
        assert result.unwrap() == "hello"


class TestJSON:
    def test_marshal_dict(self):
        result = gojson.Marshal({"name": "Go", "version": 1})
        assert result.is_ok()
        assert "name" in result.unwrap()
        assert "Go" in result.unwrap()

    def test_marshal_list(self):
        result = gojson.Marshal([1, 2, 3])
        assert result.is_ok()
        assert result.unwrap() == "[1,2,3]"

    def test_marshal_indent(self):
        result = gojson.MarshalIndent({"a": 1}, indent="  ")
        assert result.is_ok()
        assert "\n" in result.unwrap()

    def test_unmarshal_dict(self):
        result = gojson.Unmarshal('{"name": "Go"}')
        assert result.is_ok()
        assert result.unwrap() == {"name": "Go"}

    def test_unmarshal_list(self):
        result = gojson.Unmarshal("[1, 2, 3]")
        assert result.is_ok()
        assert result.unwrap() == [1, 2, 3]

    def test_unmarshal_invalid(self):
        result = gojson.Unmarshal("not json")
        assert result.is_err()

    def test_valid(self):
        assert gojson.Valid('{"valid": true}')
        assert gojson.Valid("[1, 2, 3]")
        assert not gojson.Valid("not json")

    def test_compact(self):
        result = gojson.Compact('{\n  "a": 1,\n  "b": 2\n}')
        assert result.is_ok()
        assert result.unwrap() == '{"a":1,"b":2}'


class TestCrypto:
    def test_sha256_sum(self):
        result = crypto.sha256.Sum("hello world")
        assert len(result) == 64
        assert result == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    def test_sha256_sum_bytes(self):
        result = crypto.sha256.SumBytes(b"hello world")
        assert len(result) == 32

    def test_sha512_sum(self):
        result = crypto.sha512.Sum("hello world")
        assert len(result) == 128

    def test_sha1_sum(self):
        result = crypto.sha1.Sum("hello world")
        assert len(result) == 40

    def test_md5_sum(self):
        result = crypto.md5.Sum("hello world")
        assert len(result) == 32
        assert result == "5eb63bbbe01eeed093cb22bb8f5acdc3"

    def test_sha256_size(self):
        assert crypto.sha256.Size == 32
        assert crypto.sha256.BlockSize == 64

    def test_sha512_size(self):
        assert crypto.sha512.Size == 64
        assert crypto.sha512.BlockSize == 128
