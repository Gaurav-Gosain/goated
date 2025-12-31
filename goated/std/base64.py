"""Go encoding/base64 package bindings - Pure Python implementation.

This module provides Python bindings for Go's encoding/base64 package,
maintaining Go-style naming conventions and behavior.

Example:
    >>> from goated.std import base64
    >>>
    >>> # Standard encoding
    >>> encoded = base64.StdEncoding.EncodeToString(b"Hello, World!")
    >>> print(encoded)
    SGVsbG8sIFdvcmxkIQ==
    >>>
    >>> decoded, _ = base64.StdEncoding.DecodeString(encoded)
    >>> print(decoded)
    b'Hello, World!'

"""

from __future__ import annotations

import base64 as _base64
from typing import Any

__all__ = [
    # Encodings
    "StdEncoding",
    "URLEncoding",
    "RawStdEncoding",
    "RawURLEncoding",
    # Types
    "Encoding",
    # Functions
    "NewEncoding",
    "NewEncoder",
    "NewDecoder",
    # Errors
    "CorruptInputError",
]


# =============================================================================
# Errors
# =============================================================================


class CorruptInputError(Exception):
    """CorruptInputError is returned when illegal base64 data is encountered."""

    def __init__(self, offset: int):
        self.offset = offset
        super().__init__(f"illegal base64 data at input byte {offset}")

    def Error(self) -> str:
        """Return the error message."""
        return str(self)


# =============================================================================
# Encoding
# =============================================================================

# Standard base64 alphabet
_STD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_URL_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


class Encoding:
    """An Encoding is a radix 64 encoding/decoding scheme, defined by a 64-character alphabet."""

    __slots__ = ("_alphabet", "_padding", "_strict", "_decode_map")

    def __init__(self, alphabet: str, padding: str | None = "=", strict: bool = False):
        """Create a new Encoding with the given alphabet.

        Args:
            alphabet: A 64-character string defining the encoding
            padding: The padding character (None for no padding)
            strict: If True, disallow trailing newlines

        """
        if len(alphabet) != 64:
            raise ValueError("encoding alphabet must be 64 characters")
        self._alphabet = alphabet
        self._padding = padding
        self._strict = strict
        self._decode_map: dict[int, int] | None = None

    def Encode(self, dst: bytearray, src: bytes) -> int:
        """Encode src using this encoding, writing bytes to dst.

        Args:
            dst: Destination buffer
            src: Source bytes to encode

        Returns:
            Number of bytes written to dst

        """
        encoded = self._encode_bytes(src)
        dst[: len(encoded)] = encoded
        return len(encoded)

    def EncodeToString(self, src: bytes) -> str:
        """Return the base64 encoding of src.

        Args:
            src: Source bytes to encode

        Returns:
            The encoded string

        Example:
            >>> StdEncoding.EncodeToString(b"Hello")
            'SGVsbG8='

        """
        return self._encode_bytes(src).decode("ascii")

    def EncodedLen(self, n: int) -> int:
        """Return the length in bytes of the base64 encoding of an input buffer of length n.

        Args:
            n: Input length

        Returns:
            Encoded length

        """
        if self._padding is None:
            return (n * 8 + 5) // 6
        return (n + 2) // 3 * 4

    def Decode(self, dst: bytearray, src: bytes) -> tuple[int, Exception | None]:
        """Decode src using this encoding, writing bytes to dst.

        Args:
            dst: Destination buffer
            src: Source bytes to decode

        Returns:
            Tuple of (number of bytes written, error or None)

        """
        try:
            decoded = self._decode_bytes(src)
            dst[: len(decoded)] = decoded
            return len(decoded), None
        except Exception as e:
            return 0, e

    def DecodeString(self, s: str) -> tuple[bytes, Exception | None]:
        """Return the bytes represented by the base64 string s.

        Args:
            s: The encoded string

        Returns:
            Tuple of (decoded bytes, error or None)

        Example:
            >>> data, err = StdEncoding.DecodeString("SGVsbG8=")
            >>> data
            b'Hello'

        """
        try:
            decoded = self._decode_bytes(s.encode("ascii"))
            return decoded, None
        except Exception as e:
            return b"", e

    def DecodedLen(self, n: int) -> int:
        """Return the maximum length in bytes of the decoded data.

        Args:
            n: Encoded length

        Returns:
            Maximum decoded length

        """
        if self._padding is None:
            return n * 6 // 8
        return n // 4 * 3

    def WithPadding(self, padding: str | None) -> Encoding:
        """Return a new Encoding identical to enc except with a specified padding character.

        Use None to disable padding.

        Args:
            padding: New padding character or None

        Returns:
            New Encoding with the specified padding

        """
        return Encoding(self._alphabet, padding, self._strict)

    def Strict(self) -> Encoding:
        """Return a new Encoding identical to enc except with strict decoding enabled.

        Returns:
            New Encoding with strict mode

        """
        return Encoding(self._alphabet, self._padding, True)

    def _encode_bytes(self, src: bytes) -> bytes:
        """Internal encoding implementation."""
        if not src:
            return b""

        # Use Python's base64 if using standard alphabets
        if self._alphabet == _STD_ALPHABET:
            if self._padding:
                return _base64.b64encode(src)
            else:
                return _base64.b64encode(src).rstrip(b"=")
        elif self._alphabet == _URL_ALPHABET:
            if self._padding:
                return _base64.urlsafe_b64encode(src)
            else:
                return _base64.urlsafe_b64encode(src).rstrip(b"=")

        # Custom alphabet encoding
        result = []
        alphabet = self._alphabet.encode("ascii")

        # Process 3 bytes at a time
        for i in range(0, len(src), 3):
            chunk = src[i : i + 3]

            # Convert to 24-bit number
            n = 0
            for b in chunk:
                n = (n << 8) | b

            # Pad with zeros if needed
            padding_bits = (3 - len(chunk)) * 8
            n <<= padding_bits

            # Extract 6-bit groups
            chars_to_write = len(chunk) + 1
            for j in range(4):
                if j < chars_to_write:
                    idx = (n >> (18 - j * 6)) & 0x3F
                    result.append(alphabet[idx : idx + 1])
                elif self._padding:
                    result.append(self._padding.encode("ascii"))

        return b"".join(result)

    def _decode_bytes(self, src: bytes) -> bytes:
        """Internal decoding implementation."""
        if not src:
            return b""

        # Strip whitespace if not strict
        if not self._strict:
            src = src.replace(b"\n", b"").replace(b"\r", b"")

        # Use Python's base64 if using standard alphabets
        if self._alphabet == _STD_ALPHABET:
            # Add padding if missing
            missing_padding = len(src) % 4
            if missing_padding:
                src = src + b"=" * (4 - missing_padding)
            try:
                return _base64.b64decode(src)
            except Exception as e:
                raise CorruptInputError(0) from e
        elif self._alphabet == _URL_ALPHABET:
            # Add padding if missing
            missing_padding = len(src) % 4
            if missing_padding:
                src = src + b"=" * (4 - missing_padding)
            try:
                return _base64.urlsafe_b64decode(src)
            except Exception as e:
                raise CorruptInputError(0) from e

        # Custom alphabet decoding
        if self._decode_map is None:
            self._decode_map = {c: i for i, c in enumerate(self._alphabet.encode("ascii"))}
        decode_map = self._decode_map

        # Remove padding
        src = src.rstrip(b"=") if self._padding else src

        result = []

        # Process 4 characters at a time
        for i in range(0, len(src), 4):
            chunk = src[i : i + 4]

            # Convert characters to 6-bit values
            n = 0
            valid_chars = 0
            for j, c in enumerate(chunk):
                if c in decode_map:
                    n = (n << 6) | decode_map[c]
                    valid_chars += 1
                else:
                    raise CorruptInputError(i + j)

            # Pad remaining bits
            n <<= (4 - valid_chars) * 6

            # Extract bytes
            bytes_to_write = valid_chars - 1
            for j in range(bytes_to_write):
                result.append(bytes([(n >> (16 - j * 8)) & 0xFF]))

        return b"".join(result)


# =============================================================================
# Predefined Encodings
# =============================================================================

# StdEncoding is the standard base64 encoding, as defined in RFC 4648.
StdEncoding = Encoding(_STD_ALPHABET, "=")

# URLEncoding is the alternate base64 encoding defined in RFC 4648.
# It is typically used in URLs and file names.
URLEncoding = Encoding(_URL_ALPHABET, "=")

# RawStdEncoding is the standard raw, unpadded base64 encoding.
RawStdEncoding = Encoding(_STD_ALPHABET, None)

# RawURLEncoding is the unpadded alternate base64 encoding.
RawURLEncoding = Encoding(_URL_ALPHABET, None)


# =============================================================================
# Constructor Functions
# =============================================================================


def NewEncoding(encoder: str) -> Encoding:
    """Create a new Encoding defined by the given alphabet.

    The alphabet must be a 64-byte string that does not contain
    the padding character or newline.

    Args:
        encoder: A 64-character alphabet string

    Returns:
        A new Encoding

    Example:
        >>> enc = NewEncoding("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")

    """
    return Encoding(encoder)


# =============================================================================
# Encoder/Decoder Wrappers (for io.Writer/Reader compatibility)
# =============================================================================


class Encoder:
    """An Encoder wraps a writer, encoding input to base64 before writing."""

    def __init__(self, enc: Encoding, writer: Any) -> None:
        """Create a new Encoder.

        Args:
            enc: The encoding to use
            writer: A writer with a write() method

        """
        self._enc = enc
        self._writer = writer
        self._buf = bytearray()

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        """Write encoded data.

        Args:
            p: Data to encode and write

        Returns:
            Tuple of (bytes written from p, error)

        """
        try:
            encoded = self._enc.EncodeToString(p)
            self._writer.write(encoded)
            return len(p), None
        except Exception as e:
            return 0, e

    def Close(self) -> Exception | None:
        """Flush any pending output to the underlying writer.

        Returns:
            Error if any, or None

        """
        return None


class Decoder:
    """A Decoder wraps a reader, decoding base64 input as it reads."""

    def __init__(self, enc: Encoding, reader: Any) -> None:
        """Create a new Decoder.

        Args:
            enc: The encoding to use
            reader: A reader with a read() method

        """
        self._enc = enc
        self._reader = reader
        self._buf = b""

    def Read(self, p: bytearray) -> tuple[int, Exception | None]:
        """Read and decode data.

        Args:
            p: Buffer to read into

        Returns:
            Tuple of (bytes read, error)

        """
        try:
            # Read encoded data
            encoded = self._reader.read(self._enc.EncodedLen(len(p)))
            if not encoded:
                return 0, None

            # Decode
            decoded, err = self._enc.DecodeString(
                encoded if isinstance(encoded, str) else encoded.decode()
            )
            if err:
                return 0, err

            # Copy to output
            n = min(len(decoded), len(p))
            p[:n] = decoded[:n]
            return n, None
        except Exception as e:
            return 0, e


def NewEncoder(enc: Encoding, w: Any) -> Encoder:
    """Create a new base64 stream encoder.

    Args:
        enc: The encoding to use
        w: The underlying writer

    Returns:
        A new Encoder

    """
    return Encoder(enc, w)


def NewDecoder(enc: Encoding, r: Any) -> Decoder:
    """Create a new base64 stream decoder.

    Args:
        enc: The encoding to use
        r: The underlying reader

    Returns:
        A new Decoder

    """
    return Decoder(enc, r)
