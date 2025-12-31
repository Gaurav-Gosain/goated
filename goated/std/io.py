"""Go io package bindings - Pure Python implementation.

This module provides Python bindings for Go's io package interfaces
and utility functions.

Example:
    >>> from goated.std import io
    >>>
    >>> # Copy between readers and writers
    >>> src = io.StringReader("Hello, World!")
    >>> dst = io.StringBuilder()
    >>> io.Copy(dst, src)
    >>> print(dst.String())
    Hello, World!

"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol

__all__ = [
    # Interfaces
    "Reader",
    "Writer",
    "Closer",
    "Seeker",
    "ReadWriter",
    "ReadCloser",
    "WriteCloser",
    "ReadWriteCloser",
    "ReadSeeker",
    "WriteSeeker",
    "ReadWriteSeeker",
    "ReaderAt",
    "WriterAt",
    "ByteReader",
    "ByteWriter",
    "StringWriter",
    # Functions
    "Copy",
    "CopyN",
    "CopyBuffer",
    "ReadAll",
    "ReadAtLeast",
    "ReadFull",
    "WriteString",
    "LimitReader",
    "MultiReader",
    "MultiWriter",
    "TeeReader",
    "Pipe",
    # Implementations
    "StringReader",
    "BytesReader",
    "StringBuilder",
    "BytesBuffer",
    "NopCloser",
    "Discard",
    # Seek constants
    "SeekStart",
    "SeekCurrent",
    "SeekEnd",
    # Errors
    "EOF",
    "ErrClosedPipe",
    "ErrShortBuffer",
    "ErrShortWrite",
    "ErrUnexpectedEOF",
]

# =============================================================================
# Seek Constants
# =============================================================================

SeekStart = 0  # Seek relative to origin
SeekCurrent = 1  # Seek relative to current offset
SeekEnd = 2  # Seek relative to end

# =============================================================================
# Errors
# =============================================================================


class EOF(Exception):
    """EOF is the error returned by Read when no more input is available."""

    pass


class ErrClosedPipe(Exception):
    """ErrClosedPipe is the error used for read/write on a closed pipe."""

    pass


class ErrShortBuffer(Exception):
    """ErrShortBuffer means the buffer was too short."""

    pass


class ErrShortWrite(Exception):
    """ErrShortWrite means a write accepted fewer bytes than requested."""

    pass


class ErrUnexpectedEOF(Exception):
    """ErrUnexpectedEOF means EOF was encountered in the middle of reading."""

    pass


# =============================================================================
# Interfaces (Protocols)
# =============================================================================


class Reader(Protocol):
    """Reader is the interface that wraps the basic Read method."""

    @abstractmethod
    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        """Read reads up to len(p) bytes into p."""
        ...


class Writer(Protocol):
    """Writer is the interface that wraps the basic Write method."""

    @abstractmethod
    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        """Write writes len(p) bytes from p to the underlying data stream."""
        ...


class Closer(Protocol):
    """Closer is the interface that wraps the basic Close method."""

    @abstractmethod
    def Close(self) -> Exception | None:
        """Close closes the resource."""
        ...


class Seeker(Protocol):
    """Seeker is the interface that wraps the basic Seek method."""

    @abstractmethod
    def Seek(self, offset: int, whence: int) -> tuple[int, Exception | None]:
        """Seek sets the offset for the next Read or Write."""
        ...


class ReadWriter(Reader, Writer, Protocol):
    """ReadWriter combines Reader and Writer."""

    pass


class ReadCloser(Reader, Closer, Protocol):
    """ReadCloser combines Reader and Closer."""

    pass


class WriteCloser(Writer, Closer, Protocol):
    """WriteCloser combines Writer and Closer."""

    pass


class ReadWriteCloser(Reader, Writer, Closer, Protocol):
    """ReadWriteCloser combines Reader, Writer, and Closer."""

    pass


class ReadSeeker(Reader, Seeker, Protocol):
    """ReadSeeker combines Reader and Seeker."""

    pass


class WriteSeeker(Writer, Seeker, Protocol):
    """WriteSeeker combines Writer and Seeker."""

    pass


class ReadWriteSeeker(Reader, Writer, Seeker, Protocol):
    """ReadWriteSeeker combines Reader, Writer, and Seeker."""

    pass


class ReaderAt(Protocol):
    """ReaderAt is the interface that wraps the basic ReadAt method."""

    @abstractmethod
    def ReadAt(self, p: bytearray, off: int) -> tuple[int, Exception | None]:
        """ReadAt reads len(p) bytes into p starting at offset off."""
        ...


class WriterAt(Protocol):
    """WriterAt is the interface that wraps the basic WriteAt method."""

    @abstractmethod
    def WriteAt(self, p: bytes, off: int) -> tuple[int, Exception | None]:
        """WriteAt writes len(p) bytes from p starting at offset off."""
        ...


class ByteReader(Protocol):
    """ByteReader is the interface that wraps the ReadByte method."""

    @abstractmethod
    def ReadByte(self) -> tuple[int, Exception | None]:
        """ReadByte reads and returns the next byte."""
        ...


class ByteWriter(Protocol):
    """ByteWriter is the interface that wraps the WriteByte method."""

    @abstractmethod
    def WriteByte(self, c: int) -> Exception | None:
        """WriteByte writes a single byte."""
        ...


class StringWriter(Protocol):
    """StringWriter is the interface that wraps the WriteString method."""

    @abstractmethod
    def WriteString(self, s: str) -> tuple[int, Exception | None]:
        """WriteString writes a string."""
        ...


# =============================================================================
# Implementations
# =============================================================================


class StringReader:
    """StringReader implements Reader by reading from a string."""

    __slots__ = ("_data", "_pos")

    def __init__(self, s: str):
        self._data = s.encode("utf-8")
        self._pos = 0

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        if self._pos >= len(self._data):
            return 0, EOF()

        n = min(len(p), len(self._data) - self._pos)
        p[:n] = self._data[self._pos : self._pos + n]
        self._pos += n
        return n, None

    def ReadByte(self) -> tuple[int, Exception | None]:
        if self._pos >= len(self._data):
            return 0, EOF()
        b = self._data[self._pos]
        self._pos += 1
        return b, None

    def Len(self) -> int:
        """Return the number of bytes remaining."""
        return len(self._data) - self._pos

    def Size(self) -> int:
        """Return the original length of the string."""
        return len(self._data)

    def Reset(self, s: str) -> None:
        """Reset resets the Reader to be reading from s."""
        self._data = s.encode("utf-8")
        self._pos = 0

    def Seek(self, offset: int, whence: int) -> tuple[int, Exception | None]:
        if whence == SeekStart:
            new_pos = offset
        elif whence == SeekCurrent:
            new_pos = self._pos + offset
        elif whence == SeekEnd:
            new_pos = len(self._data) + offset
        else:
            return 0, ValueError(f"invalid whence: {whence}")

        if new_pos < 0:
            return 0, ValueError("negative position")

        self._pos = new_pos
        return self._pos, None


class BytesReader:
    """BytesReader implements Reader by reading from a bytes object."""

    __slots__ = ("_data", "_pos")

    def __init__(self, b: bytes):
        self._data = b
        self._pos = 0

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        if self._pos >= len(self._data):
            return 0, EOF()

        n = min(len(p), len(self._data) - self._pos)
        p[:n] = self._data[self._pos : self._pos + n]
        self._pos += n
        return n, None

    def ReadByte(self) -> tuple[int, Exception | None]:
        if self._pos >= len(self._data):
            return 0, EOF()
        b = self._data[self._pos]
        self._pos += 1
        return b, None

    def Len(self) -> int:
        return len(self._data) - self._pos

    def Size(self) -> int:
        return len(self._data)

    def Reset(self, b: bytes) -> None:
        self._data = b
        self._pos = 0

    def Seek(self, offset: int, whence: int) -> tuple[int, Exception | None]:
        if whence == SeekStart:
            new_pos = offset
        elif whence == SeekCurrent:
            new_pos = self._pos + offset
        elif whence == SeekEnd:
            new_pos = len(self._data) + offset
        else:
            return 0, ValueError(f"invalid whence: {whence}")

        if new_pos < 0:
            return 0, ValueError("negative position")

        self._pos = new_pos
        return self._pos, None


class StringBuilder:
    """StringBuilder implements Writer for building strings."""

    __slots__ = ("_parts",)

    def __init__(self) -> None:
        self._parts: list[bytes] = []

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        self._parts.append(bytes(p))
        return len(p), None

    def WriteString(self, s: str) -> tuple[int, Exception | None]:
        b = s.encode("utf-8")
        self._parts.append(b)
        return len(b), None

    def WriteByte(self, c: int) -> Exception | None:
        self._parts.append(bytes([c]))
        return None

    def String(self) -> str:
        return b"".join(self._parts).decode("utf-8")

    def Bytes(self) -> bytes:
        return b"".join(self._parts)

    def Len(self) -> int:
        return sum(len(p) for p in self._parts)

    def Reset(self) -> None:
        self._parts.clear()


class BytesBuffer:
    """BytesBuffer is a variable-sized buffer of bytes with Read and Write methods."""

    __slots__ = ("_buf", "_pos")

    def __init__(self, initial: bytes = b""):
        self._buf = bytearray(initial)
        self._pos = 0

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        self._buf.extend(p)
        return len(p), None

    def WriteString(self, s: str) -> tuple[int, Exception | None]:
        b = s.encode("utf-8")
        self._buf.extend(b)
        return len(b), None

    def WriteByte(self, c: int) -> Exception | None:
        self._buf.append(c)
        return None

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        if self._pos >= len(self._buf):
            return 0, EOF()

        n = min(len(p), len(self._buf) - self._pos)
        p[:n] = self._buf[self._pos : self._pos + n]
        self._pos += n
        return n, None

    def ReadByte(self) -> tuple[int, Exception | None]:
        if self._pos >= len(self._buf):
            return 0, EOF()
        b = self._buf[self._pos]
        self._pos += 1
        return b, None

    def Bytes(self) -> bytes:
        return bytes(self._buf[self._pos :])

    def String(self) -> str:
        return self._buf[self._pos :].decode("utf-8")

    def Len(self) -> int:
        return len(self._buf) - self._pos

    def Cap(self) -> int:
        return len(self._buf)

    def Reset(self) -> None:
        self._buf.clear()
        self._pos = 0

    def Truncate(self, n: int) -> None:
        if n < 0 or n > len(self._buf):
            raise ValueError("truncation out of range")
        self._buf = self._buf[: self._pos + n]

    def Grow(self, n: int) -> None:
        if n < 0:
            raise ValueError("negative grow count")
        # Pre-allocate space
        self._buf.extend(b"\x00" * n)
        del self._buf[-n:]


class _DiscardWriter:
    """Writer that discards all data."""

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        return len(p), None

    def WriteString(self, s: str) -> tuple[int, Exception | None]:
        return len(s.encode("utf-8")), None


Discard = _DiscardWriter()


class NopCloser:
    """NopCloser wraps a Reader with a no-op Close method."""

    def __init__(self, r: Reader):
        self._reader = r

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        return self._reader.Read(p)

    def Close(self) -> Exception | None:
        return None


# =============================================================================
# Functions
# =============================================================================


def Copy(dst: Writer, src: Reader) -> tuple[int, Exception | None]:
    """Copy copies from src to dst until either EOF or an error.

    Returns the number of bytes copied and any error encountered.
    """
    return CopyBuffer(dst, src, None)


def CopyN(dst: Writer, src: Reader, n: int) -> tuple[int, Exception | None]:
    """Copy copies exactly n bytes from src to dst."""
    total = 0
    buf = bytearray(32 * 1024)

    while total < n:
        to_read = min(len(buf), n - total)
        read_buf = bytearray(buf[:to_read])
        nr, err = src.Read(read_buf)
        buf[:nr] = read_buf[:nr]

        if nr > 0:
            nw, werr = dst.Write(bytes(buf[:nr]))
            total += nw
            if werr:
                return total, werr
            if nw != nr:
                return total, ErrShortWrite()

        if err:
            if isinstance(err, EOF) and total == n:
                return total, None
            return total, err

    return total, None


def CopyBuffer(dst: Writer, src: Reader, buf: bytearray | None) -> tuple[int, Exception | None]:
    """Copy copies from src to dst using the provided buffer."""
    if buf is None:
        buf = bytearray(32 * 1024)

    total = 0
    while True:
        nr, err = src.Read(buf)

        if nr > 0:
            nw, werr = dst.Write(bytes(buf[:nr]))
            total += nw
            if werr:
                return total, werr
            if nw != nr:
                return total, ErrShortWrite()

        if err:
            if isinstance(err, EOF):
                return total, None
            return total, err


def ReadAll(r: Reader) -> tuple[bytes, Exception | None]:
    """ReadAll reads from r until EOF and returns the data read."""
    buf = BytesBuffer()
    _, err = Copy(buf, r)
    if err:
        return buf.Bytes(), err
    return buf.Bytes(), None


def ReadAtLeast(r: Reader, buf: bytearray, min_bytes: int) -> tuple[int, Exception | None]:
    """ReadAtLeast reads from r into buf until it has read at least min bytes."""
    if len(buf) < min_bytes:
        return 0, ErrShortBuffer()

    total = 0
    while total < min_bytes:
        read_buf = bytearray(len(buf) - total)
        n, err = r.Read(read_buf)
        buf[total : total + n] = read_buf[:n]
        total += n
        if err:
            if isinstance(err, EOF) and total >= min_bytes:
                return total, None
            if isinstance(err, EOF):
                return total, ErrUnexpectedEOF()
            return total, err

    return total, None


def ReadFull(r: Reader, buf: bytearray) -> tuple[int, Exception | None]:
    """ReadFull reads exactly len(buf) bytes from r into buf."""
    return ReadAtLeast(r, buf, len(buf))


def WriteString(w: Writer, s: str) -> tuple[int, Exception | None]:
    """WriteString writes the contents of string s to w."""
    if hasattr(w, "WriteString"):
        result: tuple[int, Exception | None] = w.WriteString(s)
        return result
    return w.Write(s.encode("utf-8"))


class _LimitedReader:
    """LimitedReader reads from R but limits the amount of data returned."""

    def __init__(self, r: Reader, n: int):
        self._reader = r
        self._remaining = n

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        if self._remaining <= 0:
            return 0, EOF()

        read_buf = bytearray(self._remaining) if len(p) > self._remaining else p

        n, err = self._reader.Read(read_buf)
        if read_buf is not p:
            p[:n] = read_buf[:n]
        self._remaining -= n
        return n, err


def LimitReader(r: Reader, n: int) -> Reader:
    """LimitReader returns a Reader that reads from r but stops after n bytes."""
    return _LimitedReader(r, n)


class _MultiReader:
    """MultiReader returns a Reader that's the logical concatenation of readers."""

    def __init__(self, readers: list[Reader]):
        self._readers = list(readers)

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        while self._readers:
            n, err = self._readers[0].Read(p)
            if n > 0 or not isinstance(err, EOF):
                if isinstance(err, EOF) and len(self._readers) > 1:
                    err = None
                return n, err
            self._readers.pop(0)
        return 0, EOF()


def MultiReader(*readers: Reader) -> Reader:
    """MultiReader returns a Reader that's the logical concatenation of the readers."""
    return _MultiReader(list(readers))


class _MultiWriter:
    """MultiWriter creates a writer that duplicates its writes to all writers."""

    def __init__(self, writers: list[Writer]):
        self._writers = list(writers)

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        for w in self._writers:
            n, err = w.Write(p)
            if err:
                return n, err
            if n != len(p):
                return n, ErrShortWrite()
        return len(p), None


def MultiWriter(*writers: Writer) -> Writer:
    """MultiWriter creates a writer that duplicates its writes to all writers."""
    return _MultiWriter(list(writers))


class _TeeReader:
    """TeeReader returns a Reader that writes to w what it reads from r."""

    def __init__(self, r: Reader, w: Writer):
        self._reader = r
        self._writer = w

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        n, err = self._reader.Read(p)
        if n > 0:
            nw, werr = self._writer.Write(bytes(p[:n]))
            if werr:
                return n, werr
            if nw != n:
                return n, ErrShortWrite()
        return n, err


def TeeReader(r: Reader, w: Writer) -> Reader:
    """TeeReader returns a Reader that writes to w what it reads from r."""
    return _TeeReader(r, w)


class _PipeReader:
    """PipeReader is the read half of a pipe."""

    def __init__(self) -> None:
        self._buf = BytesBuffer()
        self._closed = False
        self._write_closed = False

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        if self._closed:
            return 0, ErrClosedPipe()
        if self._buf.Len() == 0 and self._write_closed:
            return 0, EOF()
        return self._buf.Read(p)

    def Close(self) -> Exception | None:
        self._closed = True
        return None


class _PipeWriter:
    """PipeWriter is the write half of a pipe."""

    def __init__(self, reader: _PipeReader):
        self._reader = reader
        self._closed = False

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        if self._closed:
            return 0, ErrClosedPipe()
        if self._reader._closed:
            return 0, ErrClosedPipe()
        return self._reader._buf.Write(p)

    def Close(self) -> Exception | None:
        self._closed = True
        self._reader._write_closed = True
        return None


def Pipe() -> tuple[_PipeReader, _PipeWriter]:
    """Pipe creates a synchronous in-memory pipe.

    Returns a connected pair of PipeReader and PipeWriter.
    """
    r = _PipeReader()
    w = _PipeWriter(r)
    return r, w
