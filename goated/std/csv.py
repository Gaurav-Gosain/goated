r"""Go encoding/csv package bindings - CSV reading and writing.

This module provides Python bindings for Go's encoding/csv package.

Example:
    >>> from goated.std import csv
    >>>
    >>> reader = csv.NewReader("a,b,c\\n1,2,3\\n")
    >>> reader.ReadAll()
    Ok([['a', 'b', 'c'], ['1', '2', '3']])

"""

from __future__ import annotations

import csv as _csv
import io
from collections.abc import Iterator
from typing import IO, Any

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Reader",
    "Writer",
    "NewReader",
    "NewWriter",
    "ParseError",
    "ErrFieldCount",
    "ErrQuote",
]

# Error types
ErrFieldCount = GoError("wrong number of fields", "csv.ParseError")
ErrQuote = GoError('bare " in non-quoted-field', "csv.ParseError")


class ParseError(Exception):
    """A ParseError is returned for parsing errors."""

    def __init__(self, line: int, column: int, message: str):
        self.Line = line
        self.Column = column
        self.Message = message
        super().__init__(f"parse error on line {line}, column {column}: {message}")


class Reader:
    """A Reader reads records from a CSV-encoded file.

    The reader can be configured with various options like Comma, Comment,
    FieldsPerRecord, LazyQuotes, and TrimLeadingSpace.
    """

    def __init__(self, r: str | IO[str]):
        if isinstance(r, str):
            r = io.StringIO(r)
        self._source = r
        self._reader: Any = None  # _csv.reader instance

        # Configuration options (Go-style)
        self.Comma: str = ","
        self.Comment: str = ""
        self.FieldsPerRecord: int = 0
        self.LazyQuotes: bool = False
        self.TrimLeadingSpace: bool = False
        self.ReuseRecord: bool = False

        self._line = 0
        self._fields_per_record = 0

    def _get_reader(self) -> Any:
        """Get or create the CSV reader with current settings."""
        if self._reader is None:
            self._reader = _csv.reader(
                self._source,
                delimiter=self.Comma,
                quotechar='"',
                skipinitialspace=self.TrimLeadingSpace,
            )
        return self._reader

    def Read(self) -> Result[list[str], GoError]:
        """Reads one record (a slice of fields) from the reader."""
        try:
            reader = self._get_reader()

            while True:
                try:
                    record: list[str] = next(reader)
                    self._line += 1

                    # Skip comment lines
                    if self.Comment and record and record[0].startswith(self.Comment):
                        continue

                    # Check field count
                    if self.FieldsPerRecord > 0:
                        if len(record) != self.FieldsPerRecord:
                            return Err(
                                GoError(
                                    f"wrong number of fields on line {self._line}", "csv.ParseError"
                                )
                            )
                    elif self.FieldsPerRecord == 0 and self._fields_per_record == 0:
                        self._fields_per_record = len(record)
                    elif self.FieldsPerRecord == 0:
                        if len(record) != self._fields_per_record:
                            return Err(
                                GoError(
                                    f"wrong number of fields on line {self._line}", "csv.ParseError"
                                )
                            )

                    return Ok(record)
                except StopIteration:
                    return Err(GoError("EOF", "io.EOF"))
        except _csv.Error as e:
            return Err(GoError(str(e), "csv.ParseError"))
        except Exception as e:
            return Err(GoError(str(e), "csv.ParseError"))

    def ReadAll(self) -> Result[list[list[str]], GoError]:
        """Reads all the remaining records from the reader."""
        records = []
        while True:
            result = self.Read()
            if result.is_err():
                err = result.err()
                if err is not None and err.go_type == "io.EOF":
                    break
                if err is not None:
                    return Err(err)
            records.append(result.unwrap())
        return Ok(records)

    def __iter__(self) -> Iterator[Result[list[str], GoError]]:
        """Iterate over records."""
        while True:
            result = self.Read()
            if result.is_err():
                err = result.err()
                if err is not None and err.go_type == "io.EOF":
                    break
                yield result
                break
            yield result


class Writer:
    """A Writer writes records using CSV encoding.

    The writer can be configured with Comma and UseCRLF options.
    """

    def __init__(self, w: IO[str]):
        self._dest = w

        # Configuration options
        self.Comma: str = ","
        self.UseCRLF: bool = False

        self._writer: Any = None  # _csv.writer instance

    def _get_writer(self) -> Any:
        """Get or create the CSV writer with current settings."""
        if self._writer is None:
            lineterminator = "\r\n" if self.UseCRLF else "\n"
            self._writer = _csv.writer(
                self._dest,
                delimiter=self.Comma,
                lineterminator=lineterminator,
                quotechar='"',
                quoting=_csv.QUOTE_MINIMAL,
            )
        return self._writer

    def Write(self, record: list[str]) -> Result[None, GoError]:
        """Writes a single CSV record to w."""
        try:
            writer = self._get_writer()
            writer.writerow(record)
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "csv.Error"))

    def WriteAll(self, records: list[list[str]]) -> Result[None, GoError]:
        """Writes multiple CSV records to w."""
        try:
            writer = self._get_writer()
            writer.writerows(records)
            self.Flush()
            return Ok(None)
        except Exception as e:
            return Err(GoError(str(e), "csv.Error"))

    def Flush(self) -> None:
        """Flushes any buffered data to the underlying io.Writer."""
        self._dest.flush()

    def Error(self) -> GoError | None:
        """Returns any error that has occurred during writing."""
        return None  # Python's csv module raises exceptions


def NewReader(r: str | IO[str]) -> Reader:
    """Returns a new Reader that reads from r."""
    return Reader(r)


def NewWriter(w: IO[str]) -> Writer:
    """Returns a new Writer that writes to w."""
    return Writer(w)
