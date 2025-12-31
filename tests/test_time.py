"""Tests for the Go time package bindings."""

import pytest


class TestDuration:
    """Tests for Duration type."""

    def test_duration_constants(self):
        """Test duration constants."""
        from goated.std.time import Hour, Microsecond, Millisecond, Minute, Nanosecond, Second

        assert Nanosecond == 1
        assert Microsecond == 1000
        assert Millisecond == 1000000
        assert Second == 1000000000
        assert Minute == 60 * Second
        assert Hour == 60 * Minute

    def test_duration_string(self):
        """Test Duration.String()."""
        from goated.std.time import Duration, Hour, Minute, Second

        assert str(Duration(0)) == "0s"
        assert str(Duration(Second)) == "1s"
        assert str(Duration(Minute)) == "1m"  # Our impl omits trailing 0s
        assert str(Duration(Hour)) == "1h"
        assert str(Duration(Hour + 30 * Minute)) == "1h30m"
        assert str(Duration(-Second)) == "-1s"

    def test_duration_methods(self):
        """Test Duration methods."""
        from goated.std.time import Duration, Minute

        d = Duration(90 * Minute)

        assert d.Hours() == 1.5
        assert d.Minutes() == 90.0
        assert d.Seconds() == 5400.0
        assert d.Milliseconds() == 5400000
        assert d.Nanoseconds() == 5400000000000

    def test_duration_abs(self):
        """Test Duration.Abs()."""
        from goated.std.time import Duration, Second

        d = Duration(-5 * Second)
        assert d.Abs() == Duration(5 * Second)

    def test_parse_duration(self):
        """Test ParseDuration."""
        from goated.std.time import Hour, Minute, ParseDuration, Second

        assert ParseDuration("1s") == Duration(Second)
        assert ParseDuration("1m") == Duration(Minute)
        assert ParseDuration("1h") == Duration(Hour)
        assert ParseDuration("1h30m") == Duration(Hour + 30 * Minute)
        assert ParseDuration("-1s") == Duration(-Second)
        assert ParseDuration("500ms") == Duration(500000000)
        assert ParseDuration("1.5s") == Duration(int(1.5 * Second))

    def test_parse_duration_invalid(self):
        """Test ParseDuration with invalid input."""
        from goated.std.time import ParseDuration

        with pytest.raises(ValueError):
            ParseDuration("")

        with pytest.raises(ValueError):
            ParseDuration("invalid")


class TestMonth:
    """Tests for Month type."""

    def test_month_constants(self):
        """Test month constants."""
        from goated.std.time import (
            December,
            January,
        )

        assert int(January) == 1
        assert int(December) == 12

    def test_month_string(self):
        """Test Month.String()."""
        from goated.std.time import January, Month

        assert str(January) == "January"
        assert str(Month(6)) == "June"


class TestWeekday:
    """Tests for Weekday type."""

    def test_weekday_constants(self):
        """Test weekday constants."""
        from goated.std.time import Saturday, Sunday

        assert int(Sunday) == 0
        assert int(Saturday) == 6

    def test_weekday_string(self):
        """Test Weekday.String()."""
        from goated.std.time import Monday, Weekday

        assert str(Monday) == "Monday"
        assert str(Weekday(5)) == "Friday"


class TestTime:
    """Tests for Time type."""

    def test_now(self):
        """Test Now()."""
        from goated.std.time import Now, Time

        t = Now()
        assert isinstance(t, Time)
        assert t.Year() >= 2024

    def test_date(self):
        """Test Date()."""
        from goated.std.time import UTC, Date, January

        t = Date(2024, 1, 15, 10, 30, 0, 0, UTC)

        assert t.Year() == 2024
        assert t.Month() == January
        assert t.Day() == 15
        assert t.Hour() == 10
        assert t.Minute() == 30
        assert t.Second() == 0

    def test_unix(self):
        """Test Unix() and related functions."""
        from goated.std.time import Time, Unix

        t = Unix(0, 0)
        assert isinstance(t, Time)
        assert t.Year() == 1970
        assert t.Month() == 1
        assert t.Day() == 1

    def test_time_components(self):
        """Test Time component methods."""
        from goated.std.time import UTC, Date, Month

        t = Date(2024, 6, 15, 14, 30, 45, 123456789, UTC)

        assert t.Year() == 2024
        assert t.Month() == Month(6)
        assert t.Day() == 15
        assert t.Hour() == 14
        assert t.Minute() == 30
        assert t.Second() == 45

    def test_time_clock(self):
        """Test Time.Clock()."""
        from goated.std.time import UTC, Date

        t = Date(2024, 1, 1, 10, 30, 45, 0, UTC)
        h, m, s = t.Clock()

        assert h == 10
        assert m == 30
        assert s == 45

    def test_time_date_method(self):
        """Test Time.Date() method."""
        from goated.std.time import UTC, Date, Month

        t = Date(2024, 6, 15, 0, 0, 0, 0, UTC)
        y, m, d = t.Date()

        assert y == 2024
        assert m == Month(6)
        assert d == 15

    def test_time_weekday(self):
        """Test Time.Weekday()."""
        from goated.std.time import UTC, Date, Saturday

        # June 15, 2024 is a Saturday
        t = Date(2024, 6, 15, 0, 0, 0, 0, UTC)
        assert t.Weekday() == Saturday

    def test_time_comparison(self):
        """Test Time comparison methods."""
        from goated.std.time import UTC, Date

        t1 = Date(2024, 1, 1, 0, 0, 0, 0, UTC)
        t2 = Date(2024, 1, 2, 0, 0, 0, 0, UTC)
        t3 = Date(2024, 1, 1, 0, 0, 0, 0, UTC)

        assert t1.Before(t2)
        assert t2.After(t1)
        assert t1.Equal(t3)
        assert t1 < t2
        assert t2 > t1
        assert t1 == t3

    def test_time_add(self):
        """Test Time.Add()."""
        from goated.std.time import UTC, Date, Duration, Hour

        t1 = Date(2024, 1, 1, 10, 0, 0, 0, UTC)
        t2 = t1.Add(Duration(2 * Hour))

        assert t2.Hour() == 12

    def test_time_sub(self):
        """Test Time.Sub()."""
        from goated.std.time import UTC, Date, Hour

        t1 = Date(2024, 1, 1, 10, 0, 0, 0, UTC)
        t2 = Date(2024, 1, 1, 12, 0, 0, 0, UTC)

        d = t2.Sub(t1)
        assert d == 2 * Hour

    def test_time_add_date(self):
        """Test Time.AddDate()."""
        from goated.std.time import UTC, Date

        t1 = Date(2024, 1, 15, 0, 0, 0, 0, UTC)
        t2 = t1.AddDate(1, 2, 10)

        assert t2.Year() == 2025
        assert t2.Month() == 3
        assert t2.Day() == 25

    def test_time_unix_methods(self):
        """Test Time Unix conversion methods."""
        from goated.std.time import Unix

        t = Unix(1000, 500000000)

        assert t.Unix() == 1000
        assert t.UnixMilli() == 1000500
        assert t.UnixMicro() == 1000500000


class TestFormat:
    """Tests for time formatting."""

    def test_format_rfc3339(self):
        """Test RFC3339 formatting."""
        from goated.std.time import RFC3339, UTC, Date

        t = Date(2024, 1, 15, 10, 30, 0, 0, UTC)
        formatted = t.Format(RFC3339)

        assert "2024-01-15" in formatted
        assert "10:30:00" in formatted

    def test_parse_rfc3339(self):
        """Test RFC3339 parsing."""
        from goated.std.time import RFC3339, Parse

        t = Parse(RFC3339, "2024-01-15T10:30:00Z")

        assert t.Year() == 2024
        assert t.Month() == 1
        assert t.Day() == 15
        assert t.Hour() == 10
        assert t.Minute() == 30


class TestLocation:
    """Tests for Location type."""

    def test_utc_location(self):
        """Test UTC location."""
        from goated.std.time import UTC

        assert str(UTC) == "UTC"

    def test_local_location(self):
        """Test Local location."""
        from goated.std.time import Local

        assert str(Local) == "Local"

    def test_fixed_zone(self):
        """Test FixedZone."""
        from goated.std.time import FixedZone

        loc = FixedZone("EST", -5 * 3600)
        assert str(loc) == "EST"

    def test_time_in_location(self):
        """Test Time.In()."""
        from goated.std.time import UTC, Date, FixedZone

        t = Date(2024, 1, 15, 10, 0, 0, 0, UTC)
        est = FixedZone("EST", -5 * 3600)

        t_est = t.In(est)
        assert t_est.Location() == est


class TestSinceUntil:
    """Tests for Since and Until."""

    def test_since(self):
        """Test Since()."""
        from goated.std.time import UTC, Date, Since

        past = Date(2020, 1, 1, 0, 0, 0, 0, UTC)
        d = Since(past)

        # Should be positive (time has passed)
        assert d > 0

    def test_until(self):
        """Test Until()."""
        from goated.std.time import UTC, Date, Until

        future = Date(2030, 1, 1, 0, 0, 0, 0, UTC)
        d = Until(future)

        # Should be positive (time until future)
        assert d > 0


# Import Duration for use in tests
from goated.std.time import Duration
