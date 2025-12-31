from __future__ import annotations

import contextlib
import os as _os
import zipfile as _zipfile
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import IO

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "OpenReader",
    "NewReader",
    "NewWriter",
    "Reader",
    "Writer",
    "File",
    "FileHeader",
    "ReadCloser",
    "Deflate",
    "Store",
]

Store = _zipfile.ZIP_STORED
Deflate = _zipfile.ZIP_DEFLATED


@dataclass
class FileHeader:
    """FileHeader describes a file within a zip archive."""

    Name: str = ""
    Comment: str = ""
    CreatorVersion: int = 0
    ReaderVersion: int = 0
    Flags: int = 0
    Method: int = Deflate
    Modified: datetime | None = None
    CRC32: int = 0
    CompressedSize: int = 0
    UncompressedSize: int = 0
    CompressedSize64: int = 0
    UncompressedSize64: int = 0
    Extra: bytes = b""
    ExternalAttrs: int = 0

    def FileInfo(self) -> FileInfo:
        """FileInfo returns an os.FileInfo for the FileHeader."""
        return FileInfo(
            name=_os.path.basename(self.Name),
            size=self.UncompressedSize64 or self.UncompressedSize,
            mode=0o644,
            mod_time=self.Modified or datetime.now(),
            is_dir=self.Name.endswith("/"),
        )

    def Mode(self) -> int:
        """Mode returns the permission and mode bits for the FileHeader."""
        return (self.ExternalAttrs >> 16) & 0o777

    def SetMode(self, mode: int) -> None:
        """SetMode changes the permission and mode bits for the FileHeader."""
        self.ExternalAttrs = (self.ExternalAttrs & 0xFFFF) | (mode << 16)


@dataclass
class FileInfo:
    """FileInfo for zip entries."""

    name: str
    size: int
    mode: int
    mod_time: datetime
    is_dir: bool

    def Name(self) -> str:
        return self.name

    def Size(self) -> int:
        return self.size

    def Mode(self) -> int:
        return self.mode

    def ModTime(self) -> datetime:
        return self.mod_time

    def IsDir(self) -> bool:
        return self.is_dir


class File:
    """File represents a file in a zip archive."""

    def __init__(self, zf: _zipfile.ZipFile, info: _zipfile.ZipInfo):
        self._zf = zf
        self._info = info
        self.FileHeader = self._make_header(info)

    def _make_header(self, info: _zipfile.ZipInfo) -> FileHeader:
        mod_time = None
        if info.date_time:
            with contextlib.suppress(Exception):
                mod_time = datetime(*info.date_time)

        return FileHeader(
            Name=info.filename,
            Comment=info.comment.decode() if isinstance(info.comment, bytes) else info.comment,
            Method=info.compress_type,
            Modified=mod_time,
            CRC32=info.CRC,
            CompressedSize=info.compress_size,
            UncompressedSize=info.file_size,
            CompressedSize64=info.compress_size,
            UncompressedSize64=info.file_size,
            Extra=info.extra,
            ExternalAttrs=info.external_attr,
        )

    def Open(self) -> Result[IO[bytes], GoError]:
        """Open returns a ReadCloser that provides access to the file's contents."""
        try:
            return Ok(self._zf.open(self._info))
        except Exception as e:
            return Err(GoError(str(e), "zip.Error"))

    def Read(self) -> Result[bytes, GoError]:
        """Read reads the entire file contents."""
        try:
            return Ok(self._zf.read(self._info))
        except Exception as e:
            return Err(GoError(str(e), "zip.Error"))


class Reader:
    """Reader reads a zip archive."""

    def __init__(self, r: IO[bytes], size: int):
        self._reader = r
        self._size = size
        self._zf: _zipfile.ZipFile | None = None
        self.File: list[File] = []
        self.Comment: str = ""

    def _init(self) -> Result[None, GoError]:
        try:
            self._zf = _zipfile.ZipFile(self._reader, "r")
            self.Comment = self._zf.comment.decode() if self._zf.comment else ""
            self.File = [File(self._zf, info) for info in self._zf.infolist()]
            return Ok(None)
        except _zipfile.BadZipFile as e:
            return Err(GoError(str(e), "zip.ErrFormat"))
        except Exception as e:
            return Err(GoError(str(e), "zip.Error"))

    def Close(self) -> Result[None, GoError]:
        """Close closes the Reader."""
        if self._zf:
            with contextlib.suppress(Exception):
                self._zf.close()
        return Ok(None)

    def Open(self, name: str) -> Result[IO[bytes], GoError]:
        """Open opens a file in the archive by name."""
        for f in self.File:
            if f.FileHeader.Name == name:
                return f.Open()
        return Err(GoError(f"file not found: {name}", "zip.ErrNotFound"))


class ReadCloser(Reader):
    """ReadCloser is a Reader that must be closed when no longer needed."""

    def __init__(self, path: str):
        self._path = path
        self._file: IO[bytes] | None = None
        super().__init__(None, 0)  # type: ignore[arg-type]

    def _init(self) -> Result[None, GoError]:
        try:
            self._file = open(self._path, "rb")
            self._reader = self._file
            self._zf = _zipfile.ZipFile(self._reader, "r")
            self.Comment = self._zf.comment.decode() if self._zf.comment else ""
            self.File = [File(self._zf, info) for info in self._zf.infolist()]
            return Ok(None)
        except FileNotFoundError:
            return Err(GoError(f"file not found: {self._path}", "os.ErrNotExist"))
        except _zipfile.BadZipFile as e:
            return Err(GoError(str(e), "zip.ErrFormat"))
        except Exception as e:
            return Err(GoError(str(e), "zip.Error"))

    def Close(self) -> Result[None, GoError]:
        """Close closes the ReadCloser."""
        super().Close()
        if self._file:
            with contextlib.suppress(Exception):
                self._file.close()
        return Ok(None)


class Writer:
    """Writer writes a zip archive."""

    def __init__(self, w: IO[bytes]):
        self._writer = w
        self._zf = _zipfile.ZipFile(w, "w", _zipfile.ZIP_DEFLATED)
        self._closed = False

    def Create(self, name: str) -> Result[IO[bytes], GoError]:
        """Create adds a file to the zip archive using the provided name."""
        try:
            return Ok(_WriterFile(self._zf, name))  # type: ignore[arg-type]
        except Exception as e:
            return Err(GoError(str(e), "zip.Error"))

    def CreateHeader(self, fh: FileHeader) -> Result[IO[bytes], GoError]:
        """CreateHeader adds a file using the provided FileHeader."""
        try:
            info = _zipfile.ZipInfo(fh.Name)
            info.compress_type = fh.Method
            if fh.Modified:
                info.date_time = (
                    fh.Modified.year,
                    fh.Modified.month,
                    fh.Modified.day,
                    fh.Modified.hour,
                    fh.Modified.minute,
                    fh.Modified.second,
                )
            if fh.Comment:
                info.comment = fh.Comment.encode()
            info.external_attr = fh.ExternalAttrs
            info.extra = fh.Extra
            return Ok(_WriterFile(self._zf, fh.Name, info))  # type: ignore[arg-type]
        except Exception as e:
            return Err(GoError(str(e), "zip.Error"))

    def SetComment(self, comment: str) -> None:
        """SetComment sets the end-of-central-directory comment."""
        self._zf.comment = comment.encode()

    def Close(self) -> Result[None, GoError]:
        """Close finishes writing the zip archive."""
        if self._closed:
            return Ok(None)
        try:
            self._zf.close()
            self._closed = True
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "zip.Error"))

    def Flush(self) -> Result[None, GoError]:
        """Flush flushes any buffered data."""
        return Ok(None)

    def __enter__(self) -> Writer:
        return self

    def __exit__(self, *args: object) -> None:
        self.Close()


class _WriterFile:
    """File-like object for writing to a zip entry."""

    def __init__(self, zf: _zipfile.ZipFile, name: str, info: _zipfile.ZipInfo | None = None):
        self._zf = zf
        self._name = name
        self._info = info
        self._buffer = BytesIO()
        self._closed = False

    def write(self, data: bytes) -> int:
        return self._buffer.write(data)

    def Write(self, data: bytes) -> tuple[int, GoError | None]:
        try:
            n = self._buffer.write(data)
            return n, None
        except Exception as e:
            return 0, GoError(str(e), "zip.Error")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        data = self._buffer.getvalue()
        if self._info:
            self._zf.writestr(self._info, data)
        else:
            self._zf.writestr(self._name, data)

    def Close(self) -> Result[None, GoError]:
        try:
            self.close()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "zip.Error"))

    def __enter__(self) -> _WriterFile:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def OpenReader(name: str) -> Result[ReadCloser, GoError]:
    """OpenReader opens a zip file for reading."""
    rc = ReadCloser(name)
    result = rc._init()
    if result.is_err():
        err = result.err()
        assert err is not None
        return Err(err)
    return Ok(rc)


def NewReader(r: IO[bytes], size: int) -> Result[Reader, GoError]:
    """NewReader returns a new Reader reading from r."""
    reader = Reader(r, size)
    result = reader._init()
    if result.is_err():
        err = result.err()
        assert err is not None
        return Err(err)
    return Ok(reader)


def NewWriter(w: IO[bytes]) -> Writer:
    """NewWriter returns a new Writer writing to w."""
    return Writer(w)
