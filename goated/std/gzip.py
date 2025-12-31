"""Go compress/gzip package bindings - Gzip compression/decompression.

This module provides Python bindings for Go's compress/gzip package.

Example:
    >>> from goated.std import gzip
    >>>
    >>> compressed = gzip.Compress(b"hello world")
    >>> gzip.Decompress(compressed.unwrap())
    Ok(b'hello world')

"""

from __future__ import annotations

import gzip as _gzip
import io
from dataclasses import dataclass
from typing import IO

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Compress",
    "Decompress",
    "NewReader",
    "NewWriter",
    "Reader",
    "Writer",
    "Header",
    "BestCompression",
    "BestSpeed",
    "DefaultCompression",
    "NoCompression",
    "HuffmanOnly",
]

# Compression levels
NoCompression = 0
BestSpeed = 1
BestCompression = 9
DefaultCompression = -1
HuffmanOnly = -2  # Python doesn't have direct equivalent


@dataclass
class Header:
    """Header represents the gzip file header."""

    Comment: str = ""
    Extra: bytes = b""
    ModTime: float = 0.0
    Name: str = ""
    OS: int = 255  # Unknown OS


class Reader:
    """Reader is an io.Reader that can be read to retrieve uncompressed data."""

    def __init__(self, r: IO[bytes]):
        self._reader = _gzip.GzipFile(fileobj=r, mode="rb")
        self.Header = Header()
        try:
            # Try to read header info
            if hasattr(self._reader, "name") and self._reader.name:
                self.Header.Name = self._reader.name
            if hasattr(self._reader, "mtime"):
                mtime = self._reader.mtime
                self.Header.ModTime = float(mtime) if mtime is not None else 0.0
        except Exception:
            pass

    def Read(self, n: int = -1) -> Result[bytes, GoError]:
        """Reads decompressed data."""
        try:
            data = self._reader.read(n)
            if data == b"":
                return Err(GoError("EOF", "io.EOF"))
            return Ok(data)
        except Exception as e:
            return Err(GoError(str(e), "gzip.ErrHeader"))

    def Close(self) -> Result[None, GoError]:
        """Closes the reader."""
        try:
            self._reader.close()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "gzip.Error"))

    def Reset(self, r: IO[bytes]) -> Result[None, GoError]:
        """Resets the reader to read from a new source."""
        try:
            self._reader = _gzip.GzipFile(fileobj=r, mode="rb")
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "gzip.Error"))

    def __enter__(self) -> Reader:
        return self

    def __exit__(self, *args: object) -> None:
        self.Close()


class Writer:
    """Writer is an io.WriteCloser that compresses data."""

    def __init__(self, w: IO[bytes], level: int = DefaultCompression):
        self._buffer = w
        compress_level = level if level != DefaultCompression else 9
        if compress_level < 0:
            compress_level = 9
        self._writer = _gzip.GzipFile(
            fileobj=w, mode="wb", compresslevel=min(9, max(0, compress_level))
        )
        self.Header = Header()

    def Write(self, data: bytes | str) -> Result[int, GoError]:
        """Writes compressed data."""
        try:
            if isinstance(data, str):
                data = data.encode()
            return Ok(self._writer.write(data))
        except Exception as e:
            return Err(GoError(str(e), "gzip.Error"))

    def Close(self) -> Result[None, GoError]:
        """Closes the writer, flushing any unwritten data."""
        try:
            self._writer.close()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "gzip.Error"))

    def Flush(self) -> Result[None, GoError]:
        """Flushes any pending compressed data."""
        try:
            self._writer.flush()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "gzip.Error"))

    def Reset(self, w: IO[bytes]) -> None:
        """Resets the writer to write to a new destination."""
        self._buffer = w
        self._writer = _gzip.GzipFile(fileobj=w, mode="wb")

    def __enter__(self) -> Writer:
        return self

    def __exit__(self, *args: object) -> None:
        self.Close()


def NewReader(r: IO[bytes]) -> Result[Reader, GoError]:
    """Creates a new Reader reading from r."""
    try:
        return Ok(Reader(r))
    except Exception as e:
        return Err(GoError(str(e), "gzip.ErrHeader"))


def NewWriter(w: IO[bytes]) -> Writer:
    """Creates a new Writer writing to w with default compression level."""
    return Writer(w)


def NewWriterLevel(w: IO[bytes], level: int) -> Result[Writer, GoError]:
    """Creates a new Writer with specified compression level."""
    if (level < HuffmanOnly or level > BestCompression) and level != DefaultCompression:
        return Err(GoError(f"gzip: invalid compression level: {level}", "gzip.Error"))
    return Ok(Writer(w, level))


def Compress(data: bytes | str, level: int = DefaultCompression) -> Result[bytes, GoError]:
    """Compresses data using gzip compression."""
    try:
        if isinstance(data, str):
            data = data.encode()

        compress_level = level if level != DefaultCompression else 9
        if compress_level < 0:
            compress_level = 9

        buf = io.BytesIO()
        with _gzip.GzipFile(
            fileobj=buf, mode="wb", compresslevel=min(9, max(0, compress_level))
        ) as f:
            f.write(data)
        return Ok(buf.getvalue())
    except Exception as e:
        return Err(GoError(str(e), "gzip.Error"))


def Decompress(data: bytes) -> Result[bytes, GoError]:
    """Decompresses gzip-compressed data."""
    try:
        buf = io.BytesIO(data)
        with _gzip.GzipFile(fileobj=buf, mode="rb") as f:
            return Ok(f.read())
    except _gzip.BadGzipFile:
        return Err(GoError("gzip: invalid header", "gzip.ErrHeader"))
    except Exception as e:
        return Err(GoError(str(e), "gzip.Error"))
