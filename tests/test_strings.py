"""Comprehensive tests for strings package bindings.

Tests both Go-style (goated.std.strings) and Pythonic (goated.pythonic.strings) APIs.
Uses Python fallback when Go library is not available.
"""

import pytest

from goated.pythonic import strings as py_strings
from goated.std import strings


class TestContains:
    def test_contains_present(self):
        assert strings.Contains("hello world", "world") is True
        assert py_strings.contains("hello world", "world") is True

    def test_contains_absent(self):
        assert strings.Contains("hello world", "xyz") is False
        assert py_strings.contains("hello world", "xyz") is False

    def test_contains_empty_substr(self):
        assert strings.Contains("hello", "") is True

    def test_contains_empty_string(self):
        assert strings.Contains("", "hello") is False

    def test_contains_both_empty(self):
        assert strings.Contains("", "") is True


class TestContainsAny:
    def test_contains_any_present(self):
        assert strings.ContainsAny("hello", "aeiou") is True

    def test_contains_any_absent(self):
        assert strings.ContainsAny("xyz", "aeiou") is False

    def test_contains_any_empty_chars(self):
        assert strings.ContainsAny("hello", "") is False


class TestContainsRune:
    def test_contains_rune_present(self):
        assert strings.ContainsRune("hello", "e") is True

    def test_contains_rune_absent(self):
        assert strings.ContainsRune("hello", "x") is False

    def test_contains_rune_invalid(self):
        with pytest.raises(ValueError):
            strings.ContainsRune("hello", "ab")


class TestCount:
    def test_count_multiple(self):
        assert strings.Count("cheese", "e") == 3
        assert py_strings.count("cheese", "e") == 3

    def test_count_none(self):
        assert strings.Count("hello", "x") == 0

    def test_count_empty_substr(self):
        assert strings.Count("five", "") == 5


class TestEqualFold:
    def test_equal_fold_same_case(self):
        assert strings.EqualFold("Hello", "Hello") is True

    def test_equal_fold_different_case(self):
        assert strings.EqualFold("HELLO", "hello") is True
        assert strings.EqualFold("HeLLo", "hEllO") is True

    def test_equal_fold_different(self):
        assert strings.EqualFold("Hello", "World") is False


class TestHasPrefix:
    def test_has_prefix_true(self):
        assert strings.HasPrefix("hello world", "hello") is True
        assert py_strings.has_prefix("hello world", "hello") is True

    def test_has_prefix_false(self):
        assert strings.HasPrefix("hello world", "world") is False

    def test_has_prefix_empty(self):
        assert strings.HasPrefix("hello", "") is True


class TestHasSuffix:
    def test_has_suffix_true(self):
        assert strings.HasSuffix("hello.txt", ".txt") is True
        assert py_strings.has_suffix("hello.txt", ".txt") is True

    def test_has_suffix_false(self):
        assert strings.HasSuffix("hello.txt", ".py") is False

    def test_has_suffix_empty(self):
        assert strings.HasSuffix("hello", "") is True


class TestIndex:
    def test_index_found(self):
        assert strings.Index("hello", "ll") == 2
        assert py_strings.index("hello", "ll") == 2

    def test_index_not_found(self):
        assert strings.Index("hello", "xyz") == -1

    def test_index_empty(self):
        assert strings.Index("hello", "") == 0


class TestIndexAny:
    def test_index_any_found(self):
        assert strings.IndexAny("hello", "aeiou") == 1

    def test_index_any_not_found(self):
        assert strings.IndexAny("xyz", "aeiou") == -1


class TestIndexByte:
    def test_index_byte_found(self):
        assert strings.IndexByte("hello", "l") == 2

    def test_index_byte_not_found(self):
        assert strings.IndexByte("hello", "x") == -1

    def test_index_byte_invalid(self):
        with pytest.raises(ValueError):
            strings.IndexByte("hello", "ab")


class TestLastIndex:
    def test_last_index_found(self):
        assert strings.LastIndex("hello hello", "hello") == 6
        assert py_strings.last_index("hello hello", "hello") == 6

    def test_last_index_not_found(self):
        assert strings.LastIndex("hello", "xyz") == -1


class TestLastIndexAny:
    def test_last_index_any_found(self):
        assert strings.LastIndexAny("hello", "aeiou") == 4

    def test_last_index_any_not_found(self):
        assert strings.LastIndexAny("xyz", "aeiou") == -1


class TestSplit:
    def test_split_basic(self):
        result = strings.Split("a,b,c", ",")
        if hasattr(result, "to_list"):
            result = result.to_list()
        assert result == ["a", "b", "c"]

    def test_split_pythonic(self):
        assert py_strings.split("a,b,c", ",") == ["a", "b", "c"]

    def test_split_no_separator(self):
        result = strings.Split("hello", ",")
        if hasattr(result, "to_list"):
            result = result.to_list()
        assert result == ["hello"]

    def test_split_empty_string(self):
        result = strings.Split("", ",")
        if hasattr(result, "to_list"):
            result = result.to_list()
        assert result == [""]


class TestSplitN:
    def test_split_n(self):
        assert strings.SplitN("a,b,c,d", ",", 2) == ["a", "b,c,d"]
        assert py_strings.split_n("a,b,c,d", ",", 2) == ["a", "b,c,d"]

    def test_split_n_zero(self):
        assert strings.SplitN("a,b,c", ",", 0) == []

    def test_split_n_negative(self):
        assert strings.SplitN("a,b,c", ",", -1) == ["a", "b", "c"]


class TestSplitAfter:
    def test_split_after(self):
        assert strings.SplitAfter("a,b,c", ",") == ["a,", "b,", "c"]
        assert py_strings.split_after("a,b,c", ",") == ["a,", "b,", "c"]


class TestSplitAfterN:
    def test_split_after_n(self):
        assert strings.SplitAfterN("a,b,c,d", ",", 2) == ["a,", "b,c,d"]


class TestJoin:
    def test_join(self):
        assert strings.Join(["a", "b", "c"], ",") == "a,b,c"
        assert py_strings.join(["a", "b", "c"], ",") == "a,b,c"

    def test_join_empty(self):
        assert strings.Join([], ",") == ""

    def test_join_single(self):
        assert strings.Join(["only"], ",") == "only"


class TestFields:
    def test_fields(self):
        assert strings.Fields("  hello   world  ") == ["hello", "world"]
        assert py_strings.fields("  hello   world  ") == ["hello", "world"]

    def test_fields_single_word(self):
        assert strings.Fields("hello") == ["hello"]

    def test_fields_empty(self):
        assert strings.Fields("   ") == []


class TestFieldsFunc:
    def test_fields_func(self):
        result = strings.FieldsFunc("a1b2c3", lambda c: c.isdigit())
        assert result == ["a", "b", "c"]


class TestToLower:
    def test_to_lower(self):
        assert strings.ToLower("HELLO World") == "hello world"
        assert py_strings.to_lower("HELLO World") == "hello world"

    def test_to_lower_already_lower(self):
        assert strings.ToLower("hello") == "hello"


class TestToUpper:
    def test_to_upper(self):
        assert strings.ToUpper("hello World") == "HELLO WORLD"
        assert py_strings.to_upper("hello World") == "HELLO WORLD"

    def test_to_upper_already_upper(self):
        assert strings.ToUpper("HELLO") == "HELLO"


class TestToTitle:
    def test_to_title(self):
        # Go's ToTitle converts ALL letters to title case (uppercase for ASCII)
        # This is different from Python's title() which capitalizes first letter of each word
        # Go's Title() does what Python's title() does
        assert strings.ToTitle("hello world") == "HELLO WORLD"
        assert py_strings.to_title("hello world") == "HELLO WORLD"


class TestRepeat:
    def test_repeat(self):
        assert strings.Repeat("ab", 3) == "ababab"
        assert py_strings.repeat("ab", 3) == "ababab"

    def test_repeat_zero(self):
        assert strings.Repeat("ab", 0) == ""

    def test_repeat_negative(self):
        with pytest.raises(ValueError):
            strings.Repeat("ab", -1)


class TestReplace:
    def test_replace_limited(self):
        assert strings.Replace("oink oink oink", "oink", "moo", 2) == "moo moo oink"
        assert py_strings.replace("oink oink oink", "oink", "moo", 2) == "moo moo oink"

    def test_replace_all(self):
        assert strings.Replace("oink oink oink", "oink", "moo", -1) == "moo moo moo"


class TestReplaceAll:
    def test_replace_all(self):
        assert strings.ReplaceAll("oink oink oink", "oink", "moo") == "moo moo moo"
        assert py_strings.replace_all("oink oink oink", "oink", "moo") == "moo moo moo"


class TestTrim:
    def test_trim(self):
        assert strings.Trim("!!!hello!!!", "!") == "hello"
        assert py_strings.trim("!!!hello!!!", "!") == "hello"

    def test_trim_multiple_chars(self):
        assert strings.Trim("¡¡¡Hello!!!", "!¡") == "Hello"


class TestTrimLeft:
    def test_trim_left(self):
        assert strings.TrimLeft("!!!hello!!!", "!") == "hello!!!"
        assert py_strings.trim_left("!!!hello!!!", "!") == "hello!!!"


class TestTrimRight:
    def test_trim_right(self):
        assert strings.TrimRight("!!!hello!!!", "!") == "!!!hello"
        assert py_strings.trim_right("!!!hello!!!", "!") == "!!!hello"


class TestTrimSpace:
    def test_trim_space(self):
        assert strings.TrimSpace("  hello world  ") == "hello world"
        assert py_strings.trim_space("  hello world  ") == "hello world"

    def test_trim_space_tabs(self):
        assert strings.TrimSpace("\t\nhello\t\n") == "hello"


class TestTrimPrefix:
    def test_trim_prefix_present(self):
        assert strings.TrimPrefix("HelloWorld", "Hello") == "World"
        assert py_strings.trim_prefix("HelloWorld", "Hello") == "World"

    def test_trim_prefix_absent(self):
        assert strings.TrimPrefix("HelloWorld", "Goodbye") == "HelloWorld"


class TestTrimSuffix:
    def test_trim_suffix_present(self):
        assert strings.TrimSuffix("HelloWorld", "World") == "Hello"
        assert py_strings.trim_suffix("HelloWorld", "World") == "Hello"

    def test_trim_suffix_absent(self):
        assert strings.TrimSuffix("HelloWorld", "Planet") == "HelloWorld"


class TestBuilder:
    def test_builder_basic(self):
        b = strings.Builder()
        b.WriteString("hello")
        b.WriteString(" ")
        b.WriteString("world")
        assert str(b) == "hello world"

    def test_builder_len(self):
        b = strings.Builder()
        b.WriteString("hello")
        assert b.Len() == 5

    def test_builder_reset(self):
        b = strings.Builder()
        b.WriteString("hello")
        b.Reset()
        assert str(b) == ""
        assert b.Len() == 0

    def test_builder_write_byte(self):
        b = strings.Builder()
        b.WriteString("h")
        b.WriteByte(ord("i"))
        assert str(b) == "hi"

    def test_builder_write_rune(self):
        b = strings.Builder()
        b.WriteRune("\U0001f600")
        assert "\U0001f600" in str(b)
