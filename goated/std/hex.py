"""Go encoding/hex package bindings - Pure Python implementation.

This module provides Python bindings for Go's encoding/hex package.

Example:
    >>> from goated.std import hex
    >>>
    >>> # Encode bytes to hex string
    >>> hex.EncodeToString(b"Hello")
    '48656c6c6f'
    >>>
    >>> # Decode hex string to bytes
    >>> hex.DecodeString("48656c6c6f")
    (b'Hello', None)

"""

from __future__ import annotations

from typing import Any

__all__ = [
    "Encode",
    "Decode",
    "EncodeToString",
    "DecodeString",
    "EncodedLen",
    "DecodedLen",
    "Dump",
    "Dumper",
    "NewEncoder",
    "NewDecoder",
    # Errors
    "ErrLength",
    "InvalidByteError",
]


# =============================================================================
# Errors
# =============================================================================


class ErrLength(Exception):
    """ErrLength reports an attempt to decode an odd-length input."""

    def __init__(self) -> None:
        super().__init__("encoding/hex: odd length hex string")

    def Error(self) -> str:
        return "encoding/hex: odd length hex string"


class InvalidByteError(Exception):
    """InvalidByteError values describe errors resulting from an invalid byte."""

    def __init__(self, byte: int):
        self.byte = byte
        super().__init__(f"encoding/hex: invalid byte: {chr(byte)!r}")

    def Error(self) -> str:
        return f"encoding/hex: invalid byte: {chr(self.byte)!r}"


# =============================================================================
# Functions
# =============================================================================


def EncodedLen(n: int) -> int:
    """EncodedLen returns the length of an encoding of n source bytes.

    Specifically, it returns n * 2.
    """
    return n * 2


def DecodedLen(x: int) -> int:
    """DecodedLen returns the length of a decoding of x source bytes.

    Specifically, it returns x / 2.
    """
    return x // 2


def Encode(dst: bytearray, src: bytes) -> int:
    """Encode encodes src into EncodedLen(len(src)) bytes of dst.

    Returns the number of bytes written to dst.
    """
    hex_str = src.hex()
    encoded = hex_str.encode("ascii")
    n = len(encoded)
    dst[:n] = encoded
    return n


def Decode(dst: bytearray, src: bytes) -> tuple[int, Exception | None]:
    """Decode decodes src into DecodedLen(len(src)) bytes.

    Returns the number of bytes written to dst and any error.
    """
    if len(src) % 2 != 0:
        return 0, ErrLength()

    try:
        decoded = bytes.fromhex(src.decode("ascii"))
        n = len(decoded)
        dst[:n] = decoded
        return n, None
    except ValueError as e:
        # Find the invalid byte
        for i, b in enumerate(src):
            if chr(b) not in "0123456789abcdefABCDEF":
                return i // 2, InvalidByteError(b)
        return 0, e


def EncodeToString(src: bytes) -> str:
    """EncodeToString returns the hexadecimal encoding of src.

    Example:
        >>> EncodeToString(b"Hello, World!")
        '48656c6c6f2c20576f726c6421'

    """
    return src.hex()


def DecodeString(s: str) -> tuple[bytes, Exception | None]:
    """DecodeString returns the bytes represented by the hexadecimal string s.

    Example:
        >>> DecodeString("48656c6c6f")
        (b'Hello', None)

    """
    if len(s) % 2 != 0:
        return b"", ErrLength()

    try:
        return bytes.fromhex(s), None
    except ValueError:
        # Find the invalid character
        for _i, c in enumerate(s):
            if c not in "0123456789abcdefABCDEF":
                return b"", InvalidByteError(ord(c))
        return b"", ValueError("invalid hex string")


def Dump(data: bytes) -> str:
    """Dump returns a string that contains a hex dump of the given data.

    The format matches the output of `hexdump -C` on the command line.

    Example:
        >>> print(Dump(b"Hello, World!"))
        00000000  48 65 6c 6c 6f 2c 20 57  6f 72 6c 64 21           |Hello, World!|

    """
    lines = []

    for offset in range(0, len(data), 16):
        chunk = data[offset : offset + 16]

        # Offset
        line = f"{offset:08x}  "

        # Hex bytes
        hex_parts = []
        for i, b in enumerate(chunk):
            hex_parts.append(f"{b:02x}")
            if i == 7:
                hex_parts.append("")

        # Pad if less than 16 bytes
        while len(hex_parts) < 17:  # 16 bytes + 1 separator
            hex_parts.append("  ")

        line += " ".join(hex_parts[:8]) + "  " + " ".join(hex_parts[8:16])

        # Pad hex section
        line = line.ljust(60)

        # ASCII representation
        ascii_repr = ""
        for b in chunk:
            if 32 <= b < 127:
                ascii_repr += chr(b)
            else:
                ascii_repr += "."

        line += f"|{ascii_repr}|"
        lines.append(line)

    return "\n".join(lines)


class Dumper:
    """Dumper writes hex dump format to the underlying writer."""

    def __init__(self, w: Any) -> None:
        self._writer = w
        self._buf = bytearray()
        self._offset = 0

    def Write(self, data: bytes) -> tuple[int, Exception | None]:
        """Write writes data to the hex dump."""
        self._buf.extend(data)

        # Write complete lines
        while len(self._buf) >= 16:
            chunk = bytes(self._buf[:16])
            self._buf = self._buf[16:]

            line = self._format_line(chunk, self._offset)
            self._offset += 16

            try:
                self._writer.write(line + "\n")
            except Exception as e:
                return 0, e

        return len(data), None

    def Close(self) -> Exception | None:
        """Close flushes any remaining data."""
        if self._buf:
            line = self._format_line(bytes(self._buf), self._offset)
            try:
                self._writer.write(line + "\n")
            except Exception as e:
                return e
        return None

    def _format_line(self, chunk: bytes, offset: int) -> str:
        line = f"{offset:08x}  "

        hex_parts = [f"{b:02x}" for b in chunk]
        while len(hex_parts) < 16:
            hex_parts.append("  ")

        line += " ".join(hex_parts[:8]) + "  " + " ".join(hex_parts[8:])
        line = line.ljust(60)

        ascii_repr = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        line += f"|{ascii_repr}|"

        return line


class Encoder:
    """Encoder wraps a writer, encoding bytes to hex before writing."""

    def __init__(self, w: Any) -> None:
        self._writer = w

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        """Write encodes p as hex and writes to the underlying writer."""
        try:
            hex_str = p.hex()
            self._writer.write(hex_str)
            return len(p), None
        except Exception as e:
            return 0, e


class Decoder:
    """Decoder wraps a reader, decoding hex to bytes when reading."""

    def __init__(self, r: Any) -> None:
        self._reader = r
        self._buf = ""

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        """Read decodes hex from the underlying reader into p."""
        try:
            # Read enough hex chars for the requested bytes
            needed = len(p) * 2 - len(self._buf)
            if needed > 0:
                data = self._reader.read(needed)
                if isinstance(data, bytes):
                    data = data.decode("ascii")
                self._buf += data

            # Decode pairs
            to_decode = (len(self._buf) // 2) * 2
            if to_decode == 0:
                from .io import EOF

                return 0, EOF()

            decoded, err = DecodeString(self._buf[:to_decode])
            if err:
                return 0, err

            self._buf = self._buf[to_decode:]

            n = min(len(decoded), len(p))
            p[:n] = decoded[:n]
            return n, None
        except Exception as e:
            return 0, e


def NewEncoder(w: Any) -> Encoder:
    """NewEncoder returns a new encoder that writes to w."""
    return Encoder(w)


def NewDecoder(r: Any) -> Decoder:
    """NewDecoder returns a new decoder that reads from r."""
    return Decoder(r)
