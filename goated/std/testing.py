from __future__ import annotations

import contextlib
import sys
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "T",
    "B",
    "TB",
    "Main",
    "Benchmark",
    "Short",
    "Verbose",
    "AllocsPerRun",
]

_verbose = False
_short = False


def Verbose() -> bool:
    """Verbose reports whether the -v flag is set."""
    return _verbose


def Short() -> bool:
    """Short reports whether the -short flag is set."""
    return _short


@dataclass
class common:
    """Common elements between T and B."""

    _name: str = ""
    _failed: bool = False
    _skipped: bool = False
    _output: list[str] = field(default_factory=list)
    _start: float = 0.0
    _duration: float = 0.0
    _cleanup: list[Callable[[], None]] = field(default_factory=list)

    def Name(self) -> str:
        """Name returns the name of the running test or benchmark."""
        return self._name

    def Failed(self) -> bool:
        """Failed reports whether the function has failed."""
        return self._failed

    def Skipped(self) -> bool:
        """Skipped reports whether the test was skipped."""
        return self._skipped

    def Log(self, *args: Any) -> None:
        """Log formats its arguments and records the text in the error log."""
        msg = " ".join(str(a) for a in args)
        self._output.append(msg)
        if _verbose:
            print(f"    {self._name}: {msg}")

    def Logf(self, format: str, *args: Any) -> None:
        """Formats arguments according to format and records the text in the error log."""
        msg = format % args if args else format
        self._output.append(msg)
        if _verbose:
            print(f"    {self._name}: {msg}")

    def Error(self, *args: Any) -> None:
        """Error is equivalent to Log followed by Fail."""
        self.Log(*args)
        self.Fail()

    def Errorf(self, format: str, *args: Any) -> None:
        """Errorf is equivalent to Logf followed by Fail."""
        self.Logf(format, *args)
        self.Fail()

    def Fatal(self, *args: Any) -> None:
        """Fatal is equivalent to Log followed by FailNow."""
        self.Log(*args)
        self.FailNow()

    def Fatalf(self, format: str, *args: Any) -> None:
        """Fatalf is equivalent to Logf followed by FailNow."""
        self.Logf(format, *args)
        self.FailNow()

    def Fail(self) -> None:
        """Fail marks the function as having failed."""
        self._failed = True

    def FailNow(self) -> None:
        """FailNow marks the function as having failed and stops its execution."""
        self._failed = True
        raise _FailNowException()

    def Skip(self, *args: Any) -> None:
        """Skip is equivalent to Log followed by SkipNow."""
        self.Log(*args)
        self.SkipNow()

    def Skipf(self, format: str, *args: Any) -> None:
        """Skipf is equivalent to Logf followed by SkipNow."""
        self.Logf(format, *args)
        self.SkipNow()

    def SkipNow(self) -> None:
        """SkipNow marks the test as having been skipped and stops its execution."""
        self._skipped = True
        raise _SkipNowException()

    def Helper(self) -> None:
        """Helper marks the calling function as a test helper function."""
        pass

    def Cleanup(self, f: Callable[[], None]) -> None:
        """Cleanup registers a function to be called when the test completes."""
        self._cleanup.append(f)

    def TempDir(self) -> str:
        """TempDir returns a temporary directory for the test to use."""
        import tempfile

        return tempfile.mkdtemp()

    def Setenv(self, key: str, value: str) -> None:
        """Setenv calls os.Setenv and uses Cleanup to restore the environment variable."""
        import os

        old_value = os.environ.get(key)
        os.environ[key] = value

        def restore() -> None:
            if old_value is None:
                del os.environ[key]
            else:
                os.environ[key] = old_value

        self.Cleanup(restore)


class _FailNowException(Exception):
    """Exception raised by FailNow."""

    pass


class _SkipNowException(Exception):
    """Exception raised by SkipNow."""

    pass


@dataclass
class T(common):
    """T is a type passed to Test functions."""

    _parallel: bool = False
    _sub_tests: list[T] = field(default_factory=list)

    def Parallel(self) -> None:
        """Parallel signals that this test is to be run in parallel."""
        self._parallel = True

    def Run(self, name: str, f: Callable[[T], None]) -> bool:
        """Run runs f as a subtest of t called name."""
        sub_t = T(_name=f"{self._name}/{name}")
        sub_t._start = time.time()

        try:
            f(sub_t)
        except _FailNowException:
            pass
        except _SkipNowException:
            pass
        except Exception as e:
            sub_t._failed = True
            sub_t._output.append(f"panic: {e}\n{traceback.format_exc()}")
        finally:
            sub_t._duration = time.time() - sub_t._start
            for cleanup in reversed(sub_t._cleanup):
                with contextlib.suppress(Exception):
                    cleanup()

        self._sub_tests.append(sub_t)

        if sub_t._skipped:
            print(f"--- SKIP: {sub_t._name}")
        elif sub_t._failed:
            print(f"--- FAIL: {sub_t._name}")
            for line in sub_t._output:
                print(f"        {line}")
        elif _verbose:
            print(f"--- PASS: {sub_t._name} ({sub_t._duration:.2f}s)")

        return not sub_t._failed

    def Deadline(self) -> tuple[float, bool]:
        """Deadline reports the time at which the test binary will have exceeded the timeout."""
        return 0.0, False


@dataclass
class B(common):
    """B is a type passed to Benchmark functions."""

    N: int = 0
    _bytes: int = 0
    _timer_on: bool = False
    _result: BenchmarkResult | None = None

    def ResetTimer(self) -> None:
        """ResetTimer zeros the elapsed benchmark time."""
        self._start = time.time()

    def StartTimer(self) -> None:
        """StartTimer starts timing a test."""
        if not self._timer_on:
            self._start = time.time()
            self._timer_on = True

    def StopTimer(self) -> None:
        """StopTimer stops timing a test."""
        if self._timer_on:
            self._duration += time.time() - self._start
            self._timer_on = False

    def SetBytes(self, n: int) -> None:
        """SetBytes records the number of bytes processed in a single operation."""
        self._bytes = n

    def ReportAllocs(self) -> None:
        """ReportAllocs enables malloc statistics for this benchmark."""
        pass

    def ReportMetric(self, n: float, unit: str) -> None:
        """ReportMetric adds a custom metric to the benchmark result."""
        pass

    def Run(self, name: str, f: Callable[[B], None]) -> bool:
        """Run runs f as a subbenchmark of b called name."""
        sub_b = B(_name=f"{self._name}/{name}")
        result = _run_benchmark(sub_b, f)
        return result is not None


@dataclass
class BenchmarkResult:
    """BenchmarkResult contains the results of a benchmark run."""

    N: int = 0
    T: float = 0.0
    Bytes: int = 0
    MemAllocs: int = 0
    MemBytes: int = 0

    def NsPerOp(self) -> int:
        """NsPerOp returns the nanoseconds per operation."""
        if self.N <= 0:
            return 0
        return int(self.T * 1e9 / self.N)

    def AllocsPerOp(self) -> int:
        """AllocsPerOp returns the allocations per operation."""
        if self.N <= 0:
            return 0
        return self.MemAllocs // self.N

    def AllocedBytesPerOp(self) -> int:
        """AllocedBytesPerOp returns the bytes allocated per operation."""
        if self.N <= 0:
            return 0
        return self.MemBytes // self.N

    def String(self) -> str:
        """String returns the benchmark results as a string."""
        ns_per_op = self.NsPerOp()
        return f"{self.N}\t{ns_per_op} ns/op"


TB = T


def _run_benchmark(b: B, f: Callable[[B], None]) -> BenchmarkResult | None:
    """Run a benchmark function."""
    n = 1
    duration = 0.0

    while duration < 1.0 and n < 1_000_000_000:
        b.N = n
        b._duration = 0.0
        b._start = time.time()
        b._timer_on = True

        try:
            f(b)
        except Exception:
            return None
        finally:
            if b._timer_on:
                b._duration += time.time() - b._start

        duration = b._duration

        if duration < 0.1:
            n *= 10
        elif duration < 0.5:
            n *= 2
        else:
            break

    result = BenchmarkResult(
        N=n,
        T=duration,
        Bytes=b._bytes,
    )
    b._result = result
    return result


def Benchmark(f: Callable[[B], None]) -> BenchmarkResult:
    """Benchmark benchmarks a single function."""
    b = B(_name="Benchmark")
    result = _run_benchmark(b, f)
    return result or BenchmarkResult()


def AllocsPerRun(runs: int, f: Callable[[], None]) -> float:
    """AllocsPerRun returns the average number of allocations during f."""
    return 0.0


def Main(m: Any = None) -> None:
    """Main is an exported function for running tests."""
    global _verbose, _short

    if "-v" in sys.argv or "--verbose" in sys.argv:
        _verbose = True
    if "-short" in sys.argv:
        _short = True
