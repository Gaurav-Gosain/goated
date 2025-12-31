#!/usr/bin/env python3
"""Log file parsing with goated bufio and regexp."""

from collections.abc import Iterator
from dataclasses import dataclass

from goated.std import bufio, io, regexp, strings


@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str
    source: str = ""


LOG_PATTERN = regexp.MustCompile(
    r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)\] (?:\[([^\]]+)\] )?(.*)"
)


def parse_log_line(line: str) -> LogEntry | None:
    """Parse a single log line into a LogEntry."""
    line = strings.TrimSpace(line)
    if not line:
        return None

    matches = LOG_PATTERN.FindStringSubmatch(line)
    if not matches or len(matches) < 4:
        return None

    return LogEntry(
        timestamp=matches[1],
        level=matches[2],
        source=matches[3] if len(matches) > 4 else "",
        message=matches[4] if len(matches) > 4 else matches[3],
    )


def stream_logs(source: str) -> Iterator[LogEntry]:
    """Stream log entries from a source string."""
    reader = io.StringReader(source)
    scanner = bufio.NewScanner(reader)

    while scanner.Scan():
        line = scanner.Text()
        entry = parse_log_line(line)
        if entry:
            yield entry


def filter_by_level(entries: Iterator[LogEntry], level: str) -> Iterator[LogEntry]:
    """Filter log entries by level."""
    level_upper = strings.ToUpper(level)
    for entry in entries:
        if strings.ToUpper(entry.level) == level_upper:
            yield entry


def filter_errors_and_warnings(entries: Iterator[LogEntry]) -> Iterator[LogEntry]:
    """Filter for ERROR and WARN level entries."""
    for entry in entries:
        level = strings.ToUpper(entry.level)
        if level in ("ERROR", "WARN", "WARNING"):
            yield entry


def count_by_level(entries: list[LogEntry]) -> dict[str, int]:
    """Count entries by log level."""
    counts: dict[str, int] = {}
    for entry in entries:
        level = strings.ToUpper(entry.level)
        counts[level] = counts.get(level, 0) + 1
    return counts


def main():
    print("=== Log Parser Example ===\n")

    sample_logs = """[2024-01-15 10:30:00] [INFO] [server] Application started on port 8080
[2024-01-15 10:30:01] [DEBUG] [db] Connected to database
[2024-01-15 10:30:05] [INFO] [http] Request: GET /api/users
[2024-01-15 10:30:06] [WARN] [cache] Cache miss for key: user:123
[2024-01-15 10:30:07] [ERROR] [db] Query timeout after 5000ms
[2024-01-15 10:30:08] [INFO] [http] Request: POST /api/orders
[2024-01-15 10:30:09] [ERROR] [payment] Payment gateway unreachable
[2024-01-15 10:30:10] [INFO] [http] Request: GET /health
[2024-01-15 10:30:11] [DEBUG] [metrics] CPU: 45%, Memory: 62%
[2024-01-15 10:30:12] [WARN] [rate-limit] Rate limit approaching for IP 192.168.1.1"""

    print("=== All Entries ===")
    all_entries = list(stream_logs(sample_logs))
    for entry in all_entries:
        print(f"  [{entry.level:5}] {entry.source:12} | {entry.message}")

    print("\n=== Errors and Warnings Only ===")
    for entry in filter_errors_and_warnings(iter(all_entries)):
        print(f"  [{entry.level:5}] {entry.timestamp} | {entry.message}")

    print("\n=== Count by Level ===")
    counts = count_by_level(all_entries)
    for level, count in sorted(counts.items()):
        print(f"  {level:7}: {count}")

    print("\n=== INFO entries only ===")
    for entry in filter_by_level(iter(all_entries), "INFO"):
        print(f"  {entry.timestamp} | {entry.message}")


if __name__ == "__main__":
    main()
