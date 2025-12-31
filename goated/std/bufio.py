r"""Go bufio package bindings - Pure Python implementation.

This module provides buffered I/O, matching Go's bufio package.

Example:
    >>> from goated.std import bufio, io
    >>>
    >>> # Scanner for reading lines
    >>> scanner = bufio.NewScanner(io.StringReader("line1\\nline2\\nline3"))
    >>> while scanner.Scan():
    ...     print(scanner.Text())
    line1
    line2
    line3

"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

__all__ = [
    "Reader",
    "Writer",
    "Scanner",
    "NewReader",
    "NewWriter",
    "NewScanner",
    "NewReaderSize",
    "NewWriterSize",
    # Split functions
    "ScanBytes",
    "ScanRunes",
    "ScanLines",
    "ScanWords",
    # Errors
    "ErrBufferFull",
    "ErrNegativeCount",
    "ErrTooLong",
    "ErrNegativeAdvance",
    "ErrAdvanceTooFar",
    "ErrBadReadCount",
    "ErrFinalToken",
]


# =============================================================================
# Constants
# =============================================================================

DefaultBufSize = 4096
MaxScanTokenSize = 64 * 1024


# =============================================================================
# Errors
# =============================================================================


class ErrBufferFull(Exception):
    def __init__(self) -> None:
        super().__init__("bufio: buffer full")


class ErrNegativeCount(Exception):
    def __init__(self) -> None:
        super().__init__("bufio: negative count")


class ErrTooLong(Exception):
    def __init__(self) -> None:
        super().__init__("bufio.Scanner: token too long")


class ErrNegativeAdvance(Exception):
    def __init__(self) -> None:
        super().__init__("bufio.Scanner: SplitFunc returns negative advance count")


class ErrAdvanceTooFar(Exception):
    def __init__(self) -> None:
        super().__init__("bufio.Scanner: SplitFunc returns advance count beyond input")


class ErrBadReadCount(Exception):
    def __init__(self) -> None:
        super().__init__("bufio: bad read count")


class ErrFinalToken(Exception):
    """ErrFinalToken is a special sentinel error."""

    def __init__(self) -> None:
        super().__init__("final token")


# =============================================================================
# Split Functions
# =============================================================================

SplitFunc = Callable[[bytes, bool], tuple[int, bytes, Exception | None]]


def ScanBytes(data: bytes, at_eof: bool) -> tuple[int, bytes, Exception | None]:
    """ScanBytes is a split function that returns each byte as a token."""
    if at_eof and len(data) == 0:
        return 0, b"", None
    return 1, data[:1], None


def ScanRunes(data: bytes, at_eof: bool) -> tuple[int, bytes, Exception | None]:
    """ScanRunes is a split function that returns each UTF-8-encoded rune as a token."""
    if at_eof and len(data) == 0:
        return 0, b"", None

    if len(data) == 0:
        return 0, b"", None

    # Try to decode a single character
    for i in range(1, min(5, len(data) + 1)):
        try:
            data[:i].decode("utf-8")
            return i, data[:i], None
        except UnicodeDecodeError:
            continue

    # Invalid UTF-8, return single byte
    return 1, data[:1], None


def ScanLines(data: bytes, at_eof: bool) -> tuple[int, bytes, Exception | None]:
    """ScanLines is a split function that returns each line of text.

    The returned line may be empty. The newline is stripped.
    """
    if at_eof and len(data) == 0:
        return 0, b"", None

    # Look for newline
    i = data.find(b"\n")
    if i >= 0:
        # Strip \r if present
        line = data[:i]
        if line.endswith(b"\r"):
            line = line[:-1]
        return i + 1, line, None

    # At EOF, return remaining data
    if at_eof:
        line = data
        if line.endswith(b"\r"):
            line = line[:-1]
        return len(data), line, None

    # Request more data
    return 0, b"", None


def ScanWords(data: bytes, at_eof: bool) -> tuple[int, bytes, Exception | None]:
    """ScanWords is a split function that returns each space-separated word."""
    # Skip leading spaces
    start = 0
    while start < len(data) and data[start : start + 1] in (b" ", b"\t", b"\n", b"\r"):
        start += 1

    if start == len(data):
        if at_eof:
            return len(data), b"", None
        return 0, b"", None

    # Find end of word
    end = start
    while end < len(data) and data[end : end + 1] not in (b" ", b"\t", b"\n", b"\r"):
        end += 1

    if end == len(data) and not at_eof:
        # Word might continue
        return 0, b"", None

    return end, data[start:end], None


# =============================================================================
# Reader
# =============================================================================


class Reader:
    """Reader implements buffering for an io.Reader object."""

    def __init__(self, rd: Any, size: int = DefaultBufSize) -> None:
        self._rd = rd
        self._buf = bytearray(size)
        self._r = 0  # Read position
        self._w = 0  # Write position
        self._err: Exception | None = None

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        """Read reads data into p."""
        if len(p) == 0:
            return 0, None

        if self._r == self._w:
            if self._err:
                return 0, self._err

            # Buffer is empty, read directly if p is large enough
            if len(p) >= len(self._buf):
                n, self._err = self._rd.Read(p)
                return n, self._err

            # Fill buffer
            self._r = 0
            self._w = 0
            n, self._err = self._rd.Read(self._buf)
            if n == 0:
                return 0, self._err
            self._w = n

        # Copy from buffer
        n = min(len(p), self._w - self._r)
        p[:n] = self._buf[self._r : self._r + n]
        self._r += n
        return n, None

    def ReadByte(self) -> tuple[int, Exception | None]:
        """ReadByte reads and returns a single byte."""
        if self._r == self._w:
            if self._err:
                return 0, self._err
            self._r = 0
            self._w = 0
            n, self._err = self._rd.Read(self._buf)
            if n == 0:
                return 0, self._err
            self._w = n

        c = self._buf[self._r]
        self._r += 1
        return c, None

    def UnreadByte(self) -> Exception | None:
        """UnreadByte unreads the last byte."""
        if self._r == 0:
            return ErrBufferFull()
        self._r -= 1
        return None

    def ReadLine(self) -> tuple[bytes, bool, Exception | None]:
        """ReadLine reads a line, not including the end-of-line bytes.

        Returns (line, isPrefix, error) where isPrefix indicates whether
        the line was too long for the buffer.
        """
        line = bytearray()

        while True:
            # Look for newline in buffer
            for i in range(self._r, self._w):
                if self._buf[i] == ord("\n"):
                    result = bytes(line) + bytes(self._buf[self._r : i])
                    self._r = i + 1
                    # Strip \r
                    if result.endswith(b"\r"):
                        result = result[:-1]
                    return result, False, None

            # Add buffer content to line
            line.extend(self._buf[self._r : self._w])
            self._r = self._w

            # Try to fill buffer
            if self._err:
                if line:
                    return bytes(line), False, None
                return b"", False, self._err

            self._r = 0
            self._w = 0
            n, self._err = self._rd.Read(self._buf)
            self._w = n

            if n == 0 and self._err:
                if line:
                    return bytes(line), False, None
                return b"", False, self._err

    def ReadString(self, delim: str) -> tuple[str, Exception | None]:
        """ReadString reads until the first occurrence of delim."""
        delim_byte = ord(delim)
        result = bytearray()

        while True:
            for i in range(self._r, self._w):
                if self._buf[i] == delim_byte:
                    result.extend(self._buf[self._r : i + 1])
                    self._r = i + 1
                    return result.decode("utf-8"), None

            result.extend(self._buf[self._r : self._w])
            self._r = self._w

            if self._err:
                return result.decode("utf-8"), self._err

            self._r = 0
            self._w = 0
            n, self._err = self._rd.Read(self._buf)
            self._w = n

            if n == 0 and self._err:
                return result.decode("utf-8"), self._err

    def Peek(self, n: int) -> tuple[bytes, Exception | None]:
        """Peek returns the next n bytes without advancing the reader."""
        if n < 0:
            return b"", ErrNegativeCount()

        # Ensure buffer has enough data
        while self._w - self._r < n and not self._err:
            # Make room
            if self._r > 0:
                self._buf[: self._w - self._r] = self._buf[self._r : self._w]
                self._w -= self._r
                self._r = 0

            if self._w >= len(self._buf):
                return bytes(self._buf[: self._w]), ErrBufferFull()

            nr, self._err = self._rd.Read(memoryview(self._buf)[self._w :])
            self._w += nr

        avail = min(n, self._w - self._r)
        return bytes(self._buf[self._r : self._r + avail]), self._err if avail < n else None

    def Buffered(self) -> int:
        """Buffered returns the number of bytes in the buffer."""
        return self._w - self._r

    def Reset(self, r: Any) -> None:
        """Reset discards any buffered data and resets the reader."""
        self._rd = r
        self._r = 0
        self._w = 0
        self._err = None


# =============================================================================
# Writer
# =============================================================================


class Writer:
    """Writer implements buffering for an io.Writer object."""

    def __init__(self, wr: Any, size: int = DefaultBufSize) -> None:
        self._wr = wr
        self._buf = bytearray(size)
        self._n = 0  # Buffer position
        self._err: Exception | None = None

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        """Write writes the contents of p into the buffer."""
        total = 0

        while len(p) > 0:
            if self._err:
                return total, self._err

            # Copy to buffer
            n = min(len(p), len(self._buf) - self._n)
            self._buf[self._n : self._n + n] = p[:n]
            self._n += n
            total += n
            p = p[n:]

            # Flush if buffer is full
            if self._n >= len(self._buf):
                err = self.Flush()
                if err:
                    return total, err

        return total, None

    def WriteString(self, s: str) -> tuple[int, Exception | None]:
        """WriteString writes a string."""
        return self.Write(s.encode("utf-8"))

    def WriteByte(self, c: int) -> Exception | None:
        """WriteByte writes a single byte."""
        if self._err:
            return self._err

        if self._n >= len(self._buf):
            err = self.Flush()
            if err:
                return err

        self._buf[self._n] = c
        self._n += 1
        return None

    def Flush(self) -> Exception | None:
        """Flush writes any buffered data to the underlying writer."""
        if self._err:
            return self._err

        if self._n == 0:
            return None

        n, self._err = self._wr.Write(bytes(self._buf[: self._n]))
        if n < self._n and self._err is None:
            from .io import ErrShortWrite

            self._err = ErrShortWrite()

        if self._err:
            if n > 0 and n < self._n:
                self._buf[: self._n - n] = self._buf[n : self._n]
                self._n -= n
            return self._err

        self._n = 0
        return None

    def Available(self) -> int:
        """Available returns how many bytes are unused in the buffer."""
        return len(self._buf) - self._n

    def Buffered(self) -> int:
        """Buffered returns the number of bytes written to the buffer."""
        return self._n

    def Reset(self, w: Any) -> None:
        """Reset discards any unflushed data and resets the writer."""
        self._wr = w
        self._n = 0
        self._err = None


# =============================================================================
# Scanner
# =============================================================================


class Scanner:
    """Scanner provides a convenient interface for reading data, such as
    a file of newline-delimited lines of text.
    """

    def __init__(self, r: Any, split: SplitFunc | None = None) -> None:
        self._reader = r
        self._split = split or ScanLines
        self._buf = bytearray(MaxScanTokenSize)
        self._start = 0
        self._end = 0
        self._token: bytes = b""
        self._err: Exception | None = None
        self._done = False

    def Scan(self) -> bool:
        """Scan advances the Scanner to the next token.

        Returns False when scanning stops, either by reaching the end of
        the input or an error.
        """
        if self._done:
            return False

        while True:
            # Try to get a token from existing buffer
            if self._end > self._start:
                advance, token, err = self._split(
                    bytes(self._buf[self._start : self._end]), self._err is not None
                )

                if err:
                    if isinstance(err, ErrFinalToken):
                        self._token = token
                        self._done = True
                        return len(token) > 0
                    self._err = err
                    return False

                if advance > 0:
                    self._start += advance
                    self._token = token
                    return True

            # Need more data
            if self._err is not None:
                # EOF or error, try one last time
                if self._end > self._start:
                    advance, token, err = self._split(
                        bytes(self._buf[self._start : self._end]), True
                    )
                    if advance > 0 or len(token) > 0:
                        self._start += advance
                        self._token = token
                        self._done = True
                        return True
                self._done = True
                return False

            # Compact buffer
            if self._start > 0:
                self._buf[: self._end - self._start] = self._buf[self._start : self._end]
                self._end -= self._start
                self._start = 0

            # Read more data
            buf = bytearray(4096)
            n, self._err = self._reader.Read(buf)
            if n > 0:
                if self._end + n > len(self._buf):
                    new_size = len(self._buf) + len(self._buf) // 2
                    new_buf = bytearray(new_size)
                    new_buf[: self._end] = self._buf[: self._end]
                    self._buf = new_buf
                self._buf[self._end : self._end + n] = buf[:n]
                self._end += n

    def Text(self) -> str:
        """Text returns the most recent token as a string."""
        return self._token.decode("utf-8")

    def Bytes(self) -> bytes:
        """Bytes returns the most recent token as bytes."""
        return self._token

    def Err(self) -> Exception | None:
        """Err returns the first non-EOF error encountered."""
        from .io import EOF

        if isinstance(self._err, EOF):
            return None
        return self._err

    def Split(self, split: SplitFunc) -> None:
        """Split sets the split function for the Scanner."""
        self._split = split

    def Buffer(self, buf: bytearray, max_size: int) -> None:
        """Buffer sets the initial buffer and maximum size."""
        self._buf = buf if buf else bytearray(max_size)


# =============================================================================
# Constructors
# =============================================================================


def NewReader(rd: Any) -> Reader:
    """NewReader returns a new Reader with default buffer size."""
    return Reader(rd)


def NewReaderSize(rd: Any, size: int) -> Reader:
    """NewReaderSize returns a new Reader with the specified buffer size."""
    if size < 16:
        size = 16
    return Reader(rd, size)


def NewWriter(wr: Any) -> Writer:
    """NewWriter returns a new Writer with default buffer size."""
    return Writer(wr)


def NewWriterSize(wr: Any, size: int) -> Writer:
    """NewWriterSize returns a new Writer with the specified buffer size."""
    if size < 16:
        size = 16
    return Writer(wr, size)


def NewScanner(r: Any) -> Scanner:
    """NewScanner returns a new Scanner to read from r."""
    return Scanner(r)
