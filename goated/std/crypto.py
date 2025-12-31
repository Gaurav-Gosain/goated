r"""Go crypto package bindings - Direct mapping style.

This module provides Python bindings for Go's crypto packages including
sha256, sha512, sha1, and md5.

Example:
    >>> from goated.std import crypto
    >>>
    >>> crypto.sha256.Sum("hello world")
    'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
    >>> crypto.sha256.SumBytes(b"hello world")
    b'\\xb9M\'\\xb9\\x93M>\\x08...'

"""

from __future__ import annotations

import hashlib
import secrets
import string

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "sha256",
    "sha512",
    "sha1",
    "md5",
    "GenerateRandomBytes",
    "GenerateRandomString",
]


class _SHA256:
    """SHA-256 hash functions."""

    Size = 32
    BlockSize = 64

    @staticmethod
    def Sum(data: str | bytes) -> str:
        """Returns the SHA256 checksum of data as a hex string."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def SumBytes(data: str | bytes) -> bytes:
        """Returns the SHA256 checksum of data as bytes."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).digest()

    @staticmethod
    def New() -> hashlib._Hash:
        """Returns a new SHA256 hash."""
        return hashlib.sha256()


class _SHA512:
    """SHA-512 hash functions."""

    Size = 64
    BlockSize = 128

    @staticmethod
    def Sum(data: str | bytes) -> str:
        """Returns the SHA512 checksum of data as a hex string."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def SumBytes(data: str | bytes) -> bytes:
        """Returns the SHA512 checksum of data as bytes."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha512(data).digest()

    @staticmethod
    def New() -> hashlib._Hash:
        """Returns a new SHA512 hash."""
        return hashlib.sha512()


class _SHA1:
    """SHA-1 hash functions."""

    Size = 20
    BlockSize = 64

    @staticmethod
    def Sum(data: str | bytes) -> str:
        """Returns the SHA1 checksum of data as a hex string."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha1(data).hexdigest()

    @staticmethod
    def SumBytes(data: str | bytes) -> bytes:
        """Returns the SHA1 checksum of data as bytes."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha1(data).digest()

    @staticmethod
    def New() -> hashlib._Hash:
        """Returns a new SHA1 hash."""
        return hashlib.sha1()


class _MD5:
    """MD5 hash functions."""

    Size = 16
    BlockSize = 64

    @staticmethod
    def Sum(data: str | bytes) -> str:
        """Returns the MD5 checksum of data as a hex string."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def SumBytes(data: str | bytes) -> bytes:
        """Returns the MD5 checksum of data as bytes."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.md5(data).digest()

    @staticmethod
    def New() -> hashlib._Hash:
        """Returns a new MD5 hash."""
        return hashlib.md5()


sha256 = _SHA256()
sha512 = _SHA512()
sha1 = _SHA1()
md5 = _MD5()


def GenerateRandomBytes(n: int) -> Result[bytes, GoError]:
    """GenerateRandomBytes returns n cryptographically secure random bytes."""
    try:
        return Ok(secrets.token_bytes(n))
    except Exception as e:
        return Err(GoError(str(e), "crypto/rand.Error"))


def GenerateRandomString(n: int) -> Result[str, GoError]:
    """GenerateRandomString returns a cryptographically secure random string of length n."""
    try:
        alphabet = string.ascii_letters + string.digits
        return Ok("".join(secrets.choice(alphabet) for _ in range(n)))
    except Exception as e:
        return Err(GoError(str(e), "crypto/rand.Error"))
