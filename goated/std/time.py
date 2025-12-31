"""Go time package bindings - Pure Python implementation.

This module provides Python bindings for Go's time package, maintaining
Go-style naming conventions and behavior.

Example:
    >>> from goated.std import time
    >>>
    >>> # Current time
    >>> now = time.Now()
    >>> print(now)
    >>>
    >>> # Parse and format
    >>> t = time.Parse(time.RFC3339, "2023-01-15T10:30:00Z")
    >>> time.Format(t, time.Kitchen)

"""

from __future__ import annotations

import calendar
import re
import time as _time
from datetime import datetime, timedelta, timezone

_DURATION_PATTERN = re.compile(r"([0-9]*\.?[0-9]+)(ns|us|µs|μs|ms|s|m|h)")

__all__ = [
    # Constants - Layout formats
    "Layout",
    "ANSIC",
    "UnixDate",
    "RubyDate",
    "RFC822",
    "RFC822Z",
    "RFC850",
    "RFC1123",
    "RFC1123Z",
    "RFC3339",
    "RFC3339Nano",
    "Kitchen",
    "Stamp",
    "StampMilli",
    "StampMicro",
    "StampNano",
    "DateTime",
    "DateOnly",
    "TimeOnly",
    # Duration constants
    "Nanosecond",
    "Microsecond",
    "Millisecond",
    "Second",
    "Minute",
    "Hour",
    # Functions
    "Now",
    "Unix",
    "UnixMilli",
    "UnixMicro",
    "UnixNano",
    "Date",
    "Parse",
    "ParseDuration",
    "Since",
    "Until",
    "Sleep",
    "After",
    # Types
    "Time",
    "Duration",
    "Month",
    "Weekday",
    "Location",
    # Location
    "UTC",
    "Local",
    "LoadLocation",
    "FixedZone",
]

# =============================================================================
# Layout Constants (Go reference time: Mon Jan 2 15:04:05 MST 2006)
# =============================================================================

Layout = "01/02 03:04:05PM '06 -0700"
ANSIC = "Mon Jan _2 15:04:05 2006"
UnixDate = "Mon Jan _2 15:04:05 MST 2006"
RubyDate = "Mon Jan 02 15:04:05 -0700 2006"
RFC822 = "02 Jan 06 15:04 MST"
RFC822Z = "02 Jan 06 15:04 -0700"
RFC850 = "Monday, 02-Jan-06 15:04:05 MST"
RFC1123 = "Mon, 02 Jan 2006 15:04:05 MST"
RFC1123Z = "Mon, 02 Jan 2006 15:04:05 -0700"
RFC3339 = "2006-01-02T15:04:05Z07:00"
RFC3339Nano = "2006-01-02T15:04:05.999999999Z07:00"
Kitchen = "3:04PM"
Stamp = "Jan _2 15:04:05"
StampMilli = "Jan _2 15:04:05.000"
StampMicro = "Jan _2 15:04:05.000000"
StampNano = "Jan _2 15:04:05.000000000"
DateTime = "2006-01-02 15:04:05"
DateOnly = "2006-01-02"
TimeOnly = "15:04:05"

# =============================================================================
# Duration Constants (in nanoseconds)
# =============================================================================

Nanosecond = 1
Microsecond = 1000 * Nanosecond
Millisecond = 1000 * Microsecond
Second = 1000 * Millisecond
Minute = 60 * Second
Hour = 60 * Minute


# =============================================================================
# Month and Weekday
# =============================================================================


class Month(int):
    """Month specifies a month of the year (January = 1, ...)."""

    _names = [
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    def String(self) -> str:
        """Return the English name of the month."""
        if 1 <= self <= 12:
            return self._names[self]
        return f"Month({int(self)})"

    def __str__(self) -> str:
        return self.String()

    def __repr__(self) -> str:
        return f"Month({self.String()})"


# Month constants
January = Month(1)
February = Month(2)
March = Month(3)
April = Month(4)
May = Month(5)
June = Month(6)
July = Month(7)
August = Month(8)
September = Month(9)
October = Month(10)
November = Month(11)
December = Month(12)


class Weekday(int):
    """Weekday specifies a day of the week (Sunday = 0, ...)."""

    _names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    def String(self) -> str:
        """Return the English name of the day."""
        if 0 <= self <= 6:
            return self._names[self]
        return f"Weekday({int(self)})"

    def __str__(self) -> str:
        return self.String()

    def __repr__(self) -> str:
        return f"Weekday({self.String()})"


# Weekday constants
Sunday = Weekday(0)
Monday = Weekday(1)
Tuesday = Weekday(2)
Wednesday = Weekday(3)
Thursday = Weekday(4)
Friday = Weekday(5)
Saturday = Weekday(6)


# =============================================================================
# Location
# =============================================================================


class Location:
    """Location maps time instants to the zone in use at that time."""

    def __init__(self, name: str, offset: int = 0):
        """Create a new Location.

        Args:
            name: The timezone name
            offset: Offset from UTC in seconds

        """
        self._name = name
        self._offset = offset
        self._tz = timezone(timedelta(seconds=offset)) if offset != 0 or name == "UTC" else None

    def String(self) -> str:
        """Return the timezone name."""
        return self._name

    def __str__(self) -> str:
        return self.String()

    def __repr__(self) -> str:
        return f"Location({self._name!r})"


# Predefined locations
UTC = Location("UTC", 0)
Local = Location("Local", int(_time.timezone * -1 if _time.daylight == 0 else _time.altzone * -1))


def LoadLocation(name: str) -> Location:
    """Return the Location with the given name.

    Args:
        name: Timezone name (e.g., "America/New_York", "UTC", "Local")

    Returns:
        The Location for the given timezone

    """
    if name == "UTC":
        return UTC
    if name == "Local":
        return Local
    # For other timezones, we'd need pytz or zoneinfo
    # For now, return a basic location
    return Location(name, 0)


def FixedZone(name: str, offset: int) -> Location:
    """Return a Location with the given name and fixed offset from UTC.

    Args:
        name: The timezone name
        offset: Offset from UTC in seconds

    Returns:
        A new Location with fixed offset

    """
    return Location(name, offset)


# =============================================================================
# Duration
# =============================================================================


class Duration(int):
    """Duration represents the elapsed time between two instants as an int64 nanosecond count."""

    def String(self) -> str:
        """Return a string representing the duration in the form "72h3m0.5s"."""
        ns = int(self)
        if ns == 0:
            return "0s"

        neg = ns < 0
        if neg:
            ns = -ns

        parts = []

        # Hours
        if ns >= Hour:
            h = ns // Hour
            parts.append(f"{h}h")
            ns %= Hour

        # Minutes
        if ns >= Minute:
            m = ns // Minute
            parts.append(f"{m}m")
            ns %= Minute

        # Seconds (with fractions)
        if ns > 0 or not parts:
            s = ns / Second
            if s == int(s):
                parts.append(f"{int(s)}s")
            else:
                parts.append(f"{s:.9g}s")

        result = "".join(parts)
        if neg:
            result = "-" + result
        return result

    def __str__(self) -> str:
        return self.String()

    def __repr__(self) -> str:
        return f"Duration({self.String()})"

    def Hours(self) -> float:
        """Return the duration as a floating point number of hours."""
        return int(self) / Hour

    def Minutes(self) -> float:
        """Return the duration as a floating point number of minutes."""
        return int(self) / Minute

    def Seconds(self) -> float:
        """Return the duration as a floating point number of seconds."""
        return int(self) / Second

    def Milliseconds(self) -> int:
        """Return the duration as an integer millisecond count."""
        return int(self) // Millisecond

    def Microseconds(self) -> int:
        """Return the duration as an integer microsecond count."""
        return int(self) // Microsecond

    def Nanoseconds(self) -> int:
        """Return the duration as an integer nanosecond count."""
        return int(self)

    def Abs(self) -> Duration:
        """Return the absolute value of d."""
        return Duration(abs(int(self)))

    def Truncate(self, m: Duration) -> Duration:
        """Return the result of rounding d toward zero to a multiple of m."""
        if m <= 0:
            return self
        return Duration(int(self) - int(self) % int(m))

    def Round(self, m: Duration) -> Duration:
        """Return the result of rounding d to the nearest multiple of m."""
        if m <= 0:
            return self
        r = int(self) % int(m)
        if r < int(m) / 2:
            return Duration(int(self) - r)
        return Duration(int(self) + int(m) - r)


# =============================================================================
# Time
# =============================================================================

# Type aliases to avoid method name shadowing class names inside Time class
_Month = Month
_Location = Location


class Time:
    """Time represents an instant in time with nanosecond precision."""

    __slots__ = ("_dt", "_ns", "_loc")

    def __init__(self, dt: datetime | None = None, ns: int = 0, loc: Location | None = None):
        """Create a new Time instance.

        Args:
            dt: The datetime (default: epoch)
            ns: Additional nanoseconds
            loc: The location/timezone

        """
        self._dt = dt or datetime(1970, 1, 1, tzinfo=timezone.utc)
        self._ns = ns  # Additional nanoseconds beyond microseconds
        self._loc = loc or UTC

    def String(self) -> str:
        """Return a string representation of the time."""
        return self.Format(RFC3339)

    def __str__(self) -> str:
        return self.String()

    def __repr__(self) -> str:
        return f"Time({self.String()})"

    # Comparison operators
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return self.UnixNano() == other.UnixNano()

    def __lt__(self, other: Time) -> bool:
        return self.UnixNano() < other.UnixNano()

    def __le__(self, other: Time) -> bool:
        return self.UnixNano() <= other.UnixNano()

    def __gt__(self, other: Time) -> bool:
        return self.UnixNano() > other.UnixNano()

    def __ge__(self, other: Time) -> bool:
        return self.UnixNano() >= other.UnixNano()

    def Equal(self, u: Time) -> bool:
        """Report whether t and u represent the same time instant."""
        return self.UnixNano() == u.UnixNano()

    def Before(self, u: Time) -> bool:
        """Report whether the time instant t is before u."""
        return self.UnixNano() < u.UnixNano()

    def After(self, u: Time) -> bool:
        """Report whether the time instant t is after u."""
        return self.UnixNano() > u.UnixNano()

    def IsZero(self) -> bool:
        """Report whether t represents the zero time instant."""
        return self._dt.year == 1 and self._dt.month == 1 and self._dt.day == 1

    # Components
    def Year(self) -> int:
        """Return the year."""
        return self._dt.year

    def Month(self) -> _Month:
        """Return the month of the year."""
        return _Month(self._dt.month)

    def Day(self) -> int:
        """Return the day of the month."""
        return self._dt.day

    def Hour(self) -> int:
        """Return the hour within the day (0-23)."""
        return self._dt.hour

    def Minute(self) -> int:
        """Return the minute offset within the hour (0-59)."""
        return self._dt.minute

    def Second(self) -> int:
        """Return the second offset within the minute (0-59)."""
        return self._dt.second

    def Nanosecond(self) -> int:
        """Return the nanosecond offset within the second (0-999999999)."""
        return self._dt.microsecond * 1000 + self._ns

    def Weekday(self) -> Weekday:
        """Return the day of the week."""
        # Python: Monday=0, Go: Sunday=0
        return Weekday((self._dt.weekday() + 1) % 7)

    def YearDay(self) -> int:
        """Return the day of the year (1-366)."""
        return self._dt.timetuple().tm_yday

    def ISOWeek(self) -> tuple[int, int]:
        """Return the ISO 8601 year and week number."""
        iso = self._dt.isocalendar()
        return (iso[0], iso[1])

    def Clock(self) -> tuple[int, int, int]:
        """Return the hour, minute, and second within the day."""
        return (self._dt.hour, self._dt.minute, self._dt.second)

    def Date(self) -> tuple[int, _Month, int]:
        """Return the year, month, and day."""
        return (self._dt.year, _Month(self._dt.month), self._dt.day)

    # Unix timestamps
    def Unix(self) -> int:
        """Return t as a Unix time, seconds since January 1, 1970 UTC."""
        return int(self._dt.timestamp())

    def UnixMilli(self) -> int:
        """Return t as a Unix time, milliseconds since January 1, 1970 UTC."""
        return int(self._dt.timestamp() * 1000)

    def UnixMicro(self) -> int:
        """Return t as a Unix time, microseconds since January 1, 1970 UTC."""
        return int(self._dt.timestamp() * 1000000)

    def UnixNano(self) -> int:
        """Return t as a Unix time, nanoseconds since January 1, 1970 UTC."""
        return int(self._dt.timestamp() * 1000000000) + self._ns

    # Arithmetic
    def Add(self, d: Duration) -> Time:
        """Return the time t+d."""
        ns = int(d)
        new_dt = self._dt + timedelta(microseconds=ns // 1000)
        new_ns = self._ns + (ns % 1000)
        if new_ns >= 1000:
            new_dt += timedelta(microseconds=1)
            new_ns -= 1000
        return Time(new_dt, new_ns, self._loc)

    def Sub(self, u: Time) -> Duration:
        """Return the duration t-u."""
        return Duration(self.UnixNano() - u.UnixNano())

    def AddDate(self, years: int, months: int, days: int) -> Time:
        """Return the time corresponding to adding the given years, months, and days."""
        new_year = self._dt.year + years
        new_month = self._dt.month + months

        # Handle month overflow
        while new_month > 12:
            new_month -= 12
            new_year += 1
        while new_month < 1:
            new_month += 12
            new_year -= 1

        # Handle day overflow for the new month
        max_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(self._dt.day, max_day)

        new_dt = self._dt.replace(year=new_year, month=new_month, day=new_day)
        new_dt += timedelta(days=days)

        return Time(new_dt, self._ns, self._loc)

    # Formatting
    def Format(self, layout: str) -> str:
        """Return a textual representation of the time formatted according to layout."""
        return _format_time(self, layout)

    def GoString(self) -> str:
        """Return a Go-syntax representation of the time."""
        return (
            f"time.Date({self._dt.year}, time.{Month(self._dt.month)}, {self._dt.day}, "
            f"{self._dt.hour}, {self._dt.minute}, {self._dt.second}, "
            f"{self.Nanosecond()}, time.{self._loc})"
        )

    # Location
    def Location(self) -> _Location:
        """Return the time zone associated with t."""
        return self._loc

    def UTC(self) -> Time:
        """Return t with the location set to UTC."""
        if self._dt.tzinfo is None:
            dt = self._dt.replace(tzinfo=timezone.utc)
        else:
            dt = self._dt.astimezone(timezone.utc)
        return Time(dt, self._ns, UTC)

    def Local(self) -> Time:
        """Return t with the location set to local time."""
        dt = self._dt.astimezone()
        return Time(dt, self._ns, Local)

    def In(self, loc: _Location) -> Time:
        """Return a copy of t representing the same instant in the given location."""
        tz = loc._tz
        dt = self._dt.astimezone(tz) if tz else self._dt
        return Time(dt, self._ns, loc)

    # Truncation/Rounding
    def Truncate(self, d: Duration) -> Time:
        """Return the result of rounding t down to a multiple of d."""
        if d <= 0:
            return self
        ns = self.UnixNano()
        return Time(datetime.fromtimestamp((ns - ns % int(d)) / 1e9, tz=timezone.utc), 0, self._loc)

    def Round(self, d: Duration) -> Time:
        """Return the result of rounding t to the nearest multiple of d."""
        if d <= 0:
            return self
        ns = self.UnixNano()
        r = ns % int(d)
        if r < int(d) / 2:
            ns -= r
        else:
            ns += int(d) - r
        return Time(datetime.fromtimestamp(ns / 1e9, tz=timezone.utc), 0, self._loc)


# =============================================================================
# Time Functions
# =============================================================================


def Now() -> Time:
    """Return the current local time."""
    dt = datetime.now(timezone.utc)
    # Get additional nanoseconds from time.time_ns if available
    try:
        ns = _time.time_ns() % 1000
    except AttributeError:
        ns = 0
    return Time(dt, ns, Local)


def Unix(sec: int, nsec: int = 0) -> Time:
    """Return the local Time corresponding to the given Unix time."""
    dt = datetime.fromtimestamp(sec + nsec / 1e9, tz=timezone.utc)
    return Time(dt, nsec % 1000, Local)


def UnixMilli(msec: int) -> Time:
    """Return the local Time corresponding to the given Unix time in milliseconds."""
    return Unix(msec // 1000, (msec % 1000) * Millisecond)


def UnixMicro(usec: int) -> Time:
    """Return the local Time corresponding to the given Unix time in microseconds."""
    return Unix(usec // 1000000, (usec % 1000000) * Microsecond)


def UnixNano(nsec: int) -> Time:
    """Return the local Time corresponding to the given Unix time in nanoseconds."""
    return Unix(nsec // Second, nsec % Second)


def Date(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    min: int = 0,
    sec: int = 0,
    nsec: int = 0,
    loc: Location | None = None,
) -> Time:
    """Return the Time corresponding to the given date and time."""
    loc = loc or Local
    tz = loc._tz if loc._tz else timezone.utc
    dt = datetime(year, month, day, hour, min, sec, nsec // 1000, tzinfo=tz)
    return Time(dt, nsec % 1000, loc)


def Since(t: Time) -> Duration:
    """Return the time elapsed since t."""
    return Now().Sub(t)


def Until(t: Time) -> Duration:
    """Return the duration until t."""
    return t.Sub(Now())


def Sleep(d: Duration) -> None:
    """Pause the current goroutine for at least the duration d."""
    _time.sleep(int(d) / Second)


def After(d: Duration) -> Time:
    """Return the current time plus d."""
    return Now().Add(d)


# =============================================================================
# Parsing
# =============================================================================

# Go reference time components
_GO_REF = {
    "2006": "%Y",  # 4-digit year
    "06": "%y",  # 2-digit year
    "01": "%m",  # 2-digit month
    "1": "%-m",  # 1-2 digit month (no padding)
    "Jan": "%b",  # Abbreviated month
    "January": "%B",  # Full month
    "02": "%d",  # 2-digit day
    "2": "%-d",  # 1-2 digit day (no padding)
    "_2": "%e",  # Space-padded day
    "Mon": "%a",  # Abbreviated weekday
    "Monday": "%A",  # Full weekday
    "15": "%H",  # 24-hour hour
    "3": "%-I",  # 12-hour hour (no padding)
    "03": "%I",  # 12-hour hour (zero-padded)
    "04": "%M",  # Minutes
    "4": "%-M",  # Minutes (no padding)
    "05": "%S",  # Seconds
    "5": "%-S",  # Seconds (no padding)
    "PM": "%p",  # AM/PM
    "pm": "%p",  # am/pm (lowercase)
    "MST": "%Z",  # Timezone abbreviation
    "-0700": "%z",  # Timezone offset
    "-07:00": "%:z",  # Timezone offset with colon
    "Z0700": "%z",  # Timezone offset (Z for UTC)
    "Z07:00": "%:z",  # Timezone offset with colon (Z for UTC)
}


def _go_layout_to_strftime(layout: str) -> str:
    """Convert Go time layout to Python strftime format."""
    result = layout

    # Sort by length (longest first) to avoid partial replacements
    sorted_refs = sorted(_GO_REF.keys(), key=len, reverse=True)

    for go_ref, py_ref in [(k, _GO_REF[k]) for k in sorted_refs]:
        result = result.replace(go_ref, py_ref)

    return result


def _format_time(t: Time, layout: str) -> str:
    """Format a Time according to the Go layout."""
    # Handle special layouts
    if layout == RFC3339:
        return t._dt.strftime("%Y-%m-%dT%H:%M:%S") + _format_tz(t)
    if layout == RFC3339Nano:
        ns = t.Nanosecond()
        return t._dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{ns:09d}" + _format_tz(t)

    # General conversion
    fmt = _go_layout_to_strftime(layout)

    # Handle nanoseconds manually
    if ".999999999" in layout or ".000000000" in layout:
        ns = t.Nanosecond()
        fmt = fmt.replace(".999999999", f".{ns:09d}").replace(".000000000", f".{ns:09d}")
    elif ".000000" in layout:
        us = t._dt.microsecond
        fmt = fmt.replace(".000000", f".{us:06d}")
    elif ".000" in layout:
        ms = t._dt.microsecond // 1000
        fmt = fmt.replace(".000", f".{ms:03d}")

    try:
        return t._dt.strftime(fmt)
    except ValueError:
        # Fallback for unsupported format codes
        return t._dt.isoformat()


def _format_tz(t: Time) -> str:
    """Format timezone offset."""
    if t._loc == UTC or t._dt.tzinfo == timezone.utc:
        return "Z"

    offset = t._dt.utcoffset()
    if offset is None:
        return "Z"

    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return f"{sign}{hours:02d}:{minutes:02d}"


def Parse(layout: str, value: str) -> Time:
    """Parse a formatted string and return the time value it represents.

    Args:
        layout: The Go time layout format
        value: The string to parse

    Returns:
        The parsed Time

    Raises:
        ValueError: If the string cannot be parsed

    """
    # Handle RFC3339 format specially
    if layout in (RFC3339, RFC3339Nano):
        # Use ISO format parsing
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            ns = 0
            if "." in value:
                frac_part = value.split(".")[1].split("+")[0].split("-")[0].rstrip("Z")
                ns = int(frac_part.ljust(9, "0")[:9]) % 1000
            return Time(dt, ns, UTC if "Z" in value else Local)
        except ValueError:
            pass

    # Try standard conversion
    fmt = _go_layout_to_strftime(layout)
    try:
        dt = datetime.strptime(value, fmt)
        return Time(dt, 0, Local)
    except ValueError as e:
        raise ValueError(f"cannot parse {value!r} as {layout!r}: {e}") from e


def ParseDuration(s: str) -> Duration:
    """Parse a duration string.

    A duration string is a possibly signed sequence of decimal numbers,
    each with optional fraction and a unit suffix, such as "300ms", "-1.5h" or "2h45m".

    Valid time units are "ns", "us" (or "µs"), "ms", "s", "m", "h".

    Args:
        s: The duration string to parse

    Returns:
        The parsed Duration

    Raises:
        ValueError: If the string cannot be parsed

    """
    if not s:
        raise ValueError('time: invalid duration ""')

    orig = s
    neg = False

    if s[0] == "-" or s[0] == "+":
        neg = s[0] == "-"
        s = s[1:]

    if not s:
        raise ValueError(f"time: invalid duration {orig!r}")

    total_ns = 0

    # Unit multipliers in nanoseconds
    units = {
        "ns": Nanosecond,
        "us": Microsecond,
        "µs": Microsecond,
        "μs": Microsecond,
        "ms": Millisecond,
        "s": Second,
        "m": Minute,
        "h": Hour,
    }

    pattern = _DURATION_PATTERN
    pos = 0

    while pos < len(s):
        match = pattern.match(s, pos)
        if not match:
            raise ValueError(f"time: invalid duration {orig!r}")

        num_str, unit = match.groups()
        try:
            num = float(num_str)
        except ValueError as e:
            raise ValueError(f"time: invalid duration {orig!r}") from e

        total_ns += int(num * units[unit])
        pos = match.end()

    if neg:
        total_ns = -total_ns

    return Duration(total_ns)
