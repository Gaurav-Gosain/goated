"""Tests for the Go sort package bindings."""

import math


class TestIntSorting:
    """Tests for integer sorting."""

    def test_ints(self):
        """Test Ints()."""
        from goated.std.sort import Ints

        data = [3, 1, 4, 1, 5, 9, 2, 6]
        Ints(data)
        assert data == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_ints_already_sorted(self):
        """Test Ints() with already sorted data."""
        from goated.std.sort import Ints

        data = [1, 2, 3, 4, 5]
        Ints(data)
        assert data == [1, 2, 3, 4, 5]

    def test_ints_reverse_sorted(self):
        """Test Ints() with reverse sorted data."""
        from goated.std.sort import Ints

        data = [5, 4, 3, 2, 1]
        Ints(data)
        assert data == [1, 2, 3, 4, 5]

    def test_ints_empty(self):
        """Test Ints() with empty list."""
        from goated.std.sort import Ints

        data = []
        Ints(data)
        assert data == []

    def test_ints_single(self):
        """Test Ints() with single element."""
        from goated.std.sort import Ints

        data = [42]
        Ints(data)
        assert data == [42]

    def test_ints_are_sorted(self):
        """Test IntsAreSorted()."""
        from goated.std.sort import IntsAreSorted

        assert IntsAreSorted([1, 2, 3, 4, 5])
        assert IntsAreSorted([1, 1, 2, 2, 3])
        assert not IntsAreSorted([1, 3, 2, 4, 5])
        assert IntsAreSorted([])
        assert IntsAreSorted([1])

    def test_search_ints(self):
        """Test SearchInts()."""
        from goated.std.sort import SearchInts

        data = [1, 2, 4, 5, 7, 9]

        # Element exists
        assert SearchInts(data, 4) == 2
        assert SearchInts(data, 1) == 0
        assert SearchInts(data, 9) == 5

        # Element doesn't exist - returns insertion point
        assert SearchInts(data, 3) == 2
        assert SearchInts(data, 0) == 0
        assert SearchInts(data, 10) == 6


class TestFloat64Sorting:
    """Tests for float64 sorting."""

    def test_float64s(self):
        """Test Float64s()."""
        from goated.std.sort import Float64s

        data = [3.14, 1.0, 2.71, 0.5]
        Float64s(data)
        assert data == [0.5, 1.0, 2.71, 3.14]

    def test_float64s_with_nan(self):
        """Test Float64s() with NaN values."""
        from goated.std.sort import Float64s

        data = [3.14, float("nan"), 1.0, float("nan")]
        Float64s(data)

        # NaN values should be at the beginning
        assert math.isnan(data[0])
        assert math.isnan(data[1])
        assert data[2] == 1.0
        assert data[3] == 3.14

    def test_float64s_are_sorted(self):
        """Test Float64sAreSorted()."""
        from goated.std.sort import Float64sAreSorted

        assert Float64sAreSorted([1.0, 2.0, 3.0])
        assert not Float64sAreSorted([1.0, 3.0, 2.0])

    def test_search_float64s(self):
        """Test SearchFloat64s()."""
        from goated.std.sort import SearchFloat64s

        data = [1.0, 2.0, 3.0, 4.0]

        assert SearchFloat64s(data, 2.5) == 2
        assert SearchFloat64s(data, 2.0) == 1


class TestStringSorting:
    """Tests for string sorting."""

    def test_strings(self):
        """Test Strings()."""
        from goated.std.sort import Strings

        data = ["banana", "apple", "cherry", "date"]
        Strings(data)
        assert data == ["apple", "banana", "cherry", "date"]

    def test_strings_case_sensitive(self):
        """Test Strings() is case-sensitive."""
        from goated.std.sort import Strings

        data = ["Banana", "apple", "Cherry"]
        Strings(data)
        # Uppercase comes before lowercase in ASCII
        assert data == ["Banana", "Cherry", "apple"]

    def test_strings_are_sorted(self):
        """Test StringsAreSorted()."""
        from goated.std.sort import StringsAreSorted

        assert StringsAreSorted(["a", "b", "c"])
        assert not StringsAreSorted(["a", "c", "b"])

    def test_search_strings(self):
        """Test SearchStrings()."""
        from goated.std.sort import SearchStrings

        data = ["apple", "banana", "cherry"]

        assert SearchStrings(data, "banana") == 1
        assert SearchStrings(data, "blueberry") == 2


class TestSliceSorting:
    """Tests for generic Slice sorting."""

    def test_slice_custom_less(self):
        """Test Slice() with custom less function."""
        from goated.std.sort import Slice

        # Sort by second element of tuple
        data = [(1, "b"), (2, "a"), (3, "c")]
        Slice(data, lambda i, j: data[i][1] < data[j][1])

        assert data[0][1] == "a"
        assert data[1][1] == "b"
        assert data[2][1] == "c"

    def test_slice_reverse_sort(self):
        """Test Slice() for reverse sorting."""
        from goated.std.sort import Slice

        data = [1, 2, 3, 4, 5]
        Slice(data, lambda i, j: data[i] > data[j])

        assert data == [5, 4, 3, 2, 1]

    def test_slice_is_sorted(self):
        """Test SliceIsSorted()."""
        from goated.std.sort import SliceIsSorted

        data = [1, 2, 3, 4, 5]
        assert SliceIsSorted(data, lambda i, j: data[i] < data[j])

        data = [5, 4, 3, 2, 1]
        assert not SliceIsSorted(data, lambda i, j: data[i] < data[j])


class TestSearch:
    """Tests for Search function."""

    def test_search_basic(self):
        """Test Search() basic usage."""
        from goated.std.sort import Search

        data = [1, 2, 4, 5, 7, 9]

        # Find first element >= 4
        idx = Search(len(data), lambda i: data[i] >= 4)
        assert idx == 2
        assert data[idx] == 4

    def test_search_not_found(self):
        """Test Search() when element not found."""
        from goated.std.sort import Search

        data = [1, 2, 3, 4, 5]

        # Find first element >= 10
        idx = Search(len(data), lambda i: data[i] >= 10)
        assert idx == len(data)  # Returns n when not found


class TestIntSlice:
    """Tests for IntSlice type."""

    def test_int_slice_sort(self):
        """Test IntSlice.Sort()."""
        from goated.std.sort import IntSlice

        s = IntSlice([3, 1, 4, 1, 5])
        s.Sort()
        assert list(s) == [1, 1, 3, 4, 5]

    def test_int_slice_interface(self):
        """Test IntSlice implements Interface."""
        from goated.std.sort import IntSlice

        s = IntSlice([3, 1, 4])

        assert s.Len() == 3
        assert s.Less(1, 0)  # 1 < 3
        assert not s.Less(0, 1)  # 3 < 1 is false

        s.Swap(0, 1)
        assert s[0] == 1
        assert s[1] == 3

    def test_int_slice_search(self):
        """Test IntSlice.Search()."""
        from goated.std.sort import IntSlice

        s = IntSlice([1, 2, 4, 5])

        assert s.Search(2) == 1
        assert s.Search(3) == 2


class TestStringSlice:
    """Tests for StringSlice type."""

    def test_string_slice_sort(self):
        """Test StringSlice.Sort()."""
        from goated.std.sort import StringSlice

        s = StringSlice(["c", "a", "b"])
        s.Sort()
        assert list(s) == ["a", "b", "c"]


class TestInterfaceSorting:
    """Tests for Sort with Interface."""

    def test_sort_interface(self):
        """Test Sort() with Interface."""
        from goated.std.sort import IntSlice, Sort

        s = IntSlice([5, 2, 8, 1, 9])
        Sort(s)
        assert list(s) == [1, 2, 5, 8, 9]

    def test_stable_sort(self):
        """Test Stable() maintains order of equal elements."""
        from goated.std.sort import IntSlice, Stable

        s = IntSlice([3, 1, 4, 1, 5])
        Stable(s)
        assert list(s) == [1, 1, 3, 4, 5]

    def test_is_sorted(self):
        """Test IsSorted()."""
        from goated.std.sort import IntSlice, IsSorted

        assert IsSorted(IntSlice([1, 2, 3, 4, 5]))
        assert not IsSorted(IntSlice([1, 3, 2, 4, 5]))


class TestReverse:
    """Tests for Reverse wrapper."""

    def test_reverse(self):
        """Test Reverse() wrapper."""
        from goated.std.sort import IntSlice, Reverse, Sort

        s = IntSlice([1, 2, 3, 4, 5])
        Sort(Reverse(s))
        assert list(s) == [5, 4, 3, 2, 1]

    def test_reverse_already_reversed(self):
        """Test Reverse() on reverse-sorted data."""
        from goated.std.sort import IntSlice, Reverse, Sort

        # Sorting Reverse(s) sorts s in descending order
        # So [5,4,3,2,1] already in descending order stays the same
        s = IntSlice([5, 4, 3, 2, 1])
        Sort(Reverse(s))
        # The list is already sorted in descending order
        assert list(s) == [5, 4, 3, 2, 1]


class TestFind:
    """Tests for Find function."""

    def test_find_exists(self):
        """Test Find() when element exists."""
        from goated.std.sort import Find

        data = [1, 2, 4, 5, 7]

        def cmp(i):
            if data[i] < 4:
                return -1
            if data[i] > 4:
                return 1
            return 0

        idx, found = Find(len(data), cmp)
        assert found
        assert idx == 2
        assert data[idx] == 4

    def test_find_not_exists(self):
        """Test Find() when element doesn't exist."""
        from goated.std.sort import Find

        data = [1, 2, 5, 7]

        def cmp(i):
            if data[i] < 4:
                return -1
            if data[i] > 4:
                return 1
            return 0

        idx, found = Find(len(data), cmp)
        assert not found
        assert idx == 2  # Insertion point
