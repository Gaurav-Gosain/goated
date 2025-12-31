from __future__ import annotations

import os as _os
import sys
import time as _time
from typing import Any, TextIO

__all__ = [
    "Print",
    "Printf",
    "Println",
    "Fatal",
    "Fatalf",
    "Fatalln",
    "Panic",
    "Panicf",
    "Panicln",
    "SetOutput",
    "SetPrefix",
    "SetFlags",
    "Flags",
    "Prefix",
    "Output",
    "Writer",
    "New",
    "Default",
    "Logger",
    "Ldate",
    "Ltime",
    "Lmicroseconds",
    "Llongfile",
    "Lshortfile",
    "LUTC",
    "Lmsgprefix",
    "LstdFlags",
]

Ldate = 1 << 0
Ltime = 1 << 1
Lmicroseconds = 1 << 2
Llongfile = 1 << 3
Lshortfile = 1 << 4
LUTC = 1 << 5
Lmsgprefix = 1 << 6
LstdFlags = Ldate | Ltime


class Logger:
    """Logger represents an active logging object."""

    def __init__(self, out: TextIO = sys.stderr, prefix: str = "", flag: int = LstdFlags):
        self._out = out
        self._prefix = prefix
        self._flag = flag

    def _format_header(self) -> str:
        parts = []

        if self._flag & Lmsgprefix == 0 and self._prefix:
            parts.append(self._prefix)

        if self._flag & (Ldate | Ltime | Lmicroseconds):
            now = _time.time()
            t = _time.gmtime(now) if self._flag & LUTC else _time.localtime(now)

            if self._flag & Ldate:
                parts.append(_time.strftime("%Y/%m/%d", t))

            if self._flag & Ltime:
                if self._flag & Lmicroseconds:
                    micros = int((now % 1) * 1000000)
                    parts.append(_time.strftime("%H:%M:%S", t) + f".{micros:06d}")
                else:
                    parts.append(_time.strftime("%H:%M:%S", t))

        if self._flag & (Llongfile | Lshortfile):
            import traceback

            stack = traceback.extract_stack()
            for frame in reversed(stack):
                if "log.py" not in frame.filename:
                    if self._flag & Lshortfile:
                        parts.append(f"{_os.path.basename(frame.filename)}:{frame.lineno}:")
                    else:
                        parts.append(f"{frame.filename}:{frame.lineno}:")
                    break

        return " ".join(parts) + " " if parts else ""

    def _output(self, s: str) -> None:
        header = self._format_header()

        msg = header + self._prefix + s if self._flag & Lmsgprefix and self._prefix else header + s

        if not msg.endswith("\n"):
            msg += "\n"

        self._out.write(msg)
        self._out.flush()

    def Print(self, *v: Any) -> None:
        """Print calls Output to print to the logger."""
        self._output(" ".join(str(x) for x in v))

    def Printf(self, format: str, *v: Any) -> None:
        """Printf calls Output to print formatted output to the logger."""
        self._output(format % v if v else format)

    def Println(self, *v: Any) -> None:
        """Println calls Output to print to the logger."""
        self._output(" ".join(str(x) for x in v))

    def Fatal(self, *v: Any) -> None:
        """Fatal is equivalent to Print() followed by sys.exit(1)."""
        self.Print(*v)
        sys.exit(1)

    def Fatalf(self, format: str, *v: Any) -> None:
        """Fatalf is equivalent to Printf() followed by sys.exit(1)."""
        self.Printf(format, *v)
        sys.exit(1)

    def Fatalln(self, *v: Any) -> None:
        """Fatalln is equivalent to Println() followed by sys.exit(1)."""
        self.Println(*v)
        sys.exit(1)

    def Panic(self, *v: Any) -> None:
        """Panic is equivalent to Print() followed by a raise."""
        s = " ".join(str(x) for x in v)
        self._output(s)
        raise RuntimeError(s)

    def Panicf(self, format: str, *v: Any) -> None:
        """Panicf is equivalent to Printf() followed by a raise."""
        s = format % v if v else format
        self._output(s)
        raise RuntimeError(s)

    def Panicln(self, *v: Any) -> None:
        """Panicln is equivalent to Println() followed by a raise."""
        s = " ".join(str(x) for x in v)
        self._output(s)
        raise RuntimeError(s)

    def SetOutput(self, w: TextIO) -> None:
        """SetOutput sets the output destination for the logger."""
        self._out = w

    def SetPrefix(self, prefix: str) -> None:
        """SetPrefix sets the output prefix for the logger."""
        self._prefix = prefix

    def SetFlags(self, flag: int) -> None:
        """SetFlags sets the output flags for the logger."""
        self._flag = flag

    def Flags(self) -> int:
        """Flags returns the output flags for the logger."""
        return self._flag

    def Prefix(self) -> str:
        """Prefix returns the output prefix for the logger."""
        return self._prefix

    def Output(self, calldepth: int, s: str) -> Exception | None:
        """Output writes the output for a logging event."""
        try:
            self._output(s)
            return None
        except Exception as e:
            return e

    def Writer(self) -> TextIO:
        """Writer returns the output destination for the logger."""
        return self._out


_std = Logger(sys.stderr, "", LstdFlags)


def Default() -> Logger:
    """Default returns the standard logger used by the package-level output functions."""
    return _std


def New(out: TextIO, prefix: str, flag: int) -> Logger:
    """New creates a new Logger."""
    return Logger(out, prefix, flag)


def SetOutput(w: TextIO) -> None:
    """SetOutput sets the output destination for the standard logger."""
    _std.SetOutput(w)


def SetPrefix(prefix: str) -> None:
    """SetPrefix sets the output prefix for the standard logger."""
    _std.SetPrefix(prefix)


def SetFlags(flag: int) -> None:
    """SetFlags sets the output flags for the standard logger."""
    _std.SetFlags(flag)


def Flags() -> int:
    """Flags returns the output flags for the standard logger."""
    return _std.Flags()


def Prefix() -> str:
    """Prefix returns the output prefix for the standard logger."""
    return _std.Prefix()


def Output(calldepth: int, s: str) -> Exception | None:
    """Output writes the output for a logging event."""
    return _std.Output(calldepth, s)


def Writer() -> TextIO:
    """Writer returns the output destination for the standard logger."""
    return _std.Writer()


def Print(*v: Any) -> None:
    """Print calls Output to print to the standard logger."""
    _std.Print(*v)


def Printf(format: str, *v: Any) -> None:
    """Printf calls Output to print formatted output."""
    _std.Printf(format, *v)


def Println(*v: Any) -> None:
    """Println calls Output to print to the standard logger."""
    _std.Println(*v)


def Fatal(*v: Any) -> None:
    """Fatal is equivalent to Print() followed by sys.exit(1)."""
    _std.Fatal(*v)


def Fatalf(format: str, *v: Any) -> None:
    """Fatalf is equivalent to Printf() followed by sys.exit(1)."""
    _std.Fatalf(format, *v)


def Fatalln(*v: Any) -> None:
    """Fatalln is equivalent to Println() followed by sys.exit(1)."""
    _std.Fatalln(*v)


def Panic(*v: Any) -> None:
    """Panic is equivalent to Print() followed by a raise."""
    _std.Panic(*v)


def Panicf(format: str, *v: Any) -> None:
    """Panicf is equivalent to Printf() followed by a raise."""
    _std.Panicf(format, *v)


def Panicln(*v: Any) -> None:
    """Panicln is equivalent to Println() followed by a raise."""
    _std.Panicln(*v)
