from __future__ import annotations

import hashlib as _hashlib
import hmac as _hmac
from abc import ABC, abstractmethod

__all__ = [
    "Hash",
    "Hash32",
    "Hash64",
    "New",
    "NewMD5",
    "NewSHA1",
    "NewSHA256",
    "NewSHA512",
    "NewSHA224",
    "NewSHA384",
    "Sum",
    "SumMD5",
    "SumSHA1",
    "SumSHA224",
    "SumSHA256",
    "SumSHA384",
    "SumSHA512",
    "NewHMAC",
    "HMAC",
]


class Hash(ABC):
    """Hash is the common interface implemented by all hash functions."""

    @abstractmethod
    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        """Write adds more data to the running hash."""
        pass

    @abstractmethod
    def Sum(self, b: bytes | None = None) -> bytes:
        """Sum appends the current hash to b and returns the resulting slice."""
        pass

    @abstractmethod
    def Reset(self) -> None:
        """Reset resets the Hash to its initial state."""
        pass

    @abstractmethod
    def Size(self) -> int:
        """Size returns the number of bytes Sum will return."""
        pass

    @abstractmethod
    def BlockSize(self) -> int:
        """BlockSize returns the hash's underlying block size."""
        pass


class Hash32(Hash):
    """Hash32 is the common interface implemented by all 32-bit hash functions."""

    @abstractmethod
    def Sum32(self) -> int:
        """Sum32 returns the 32-bit hash."""
        pass


class Hash64(Hash):
    """Hash64 is the common interface implemented by all 64-bit hash functions."""

    @abstractmethod
    def Sum64(self) -> int:
        """Sum64 returns the 64-bit hash."""
        pass


class _HashWrapper(Hash):
    """Wraps a hashlib hash object to provide the Go Hash interface."""

    def __init__(self, name: str):
        self._name = name
        self._hash = _hashlib.new(name)

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        try:
            self._hash.update(p)
            return len(p), None
        except Exception as e:
            return 0, e

    def Sum(self, b: bytes | None = None) -> bytes:
        digest = self._hash.digest()
        if b is not None:
            return b + digest
        return digest

    def Reset(self) -> None:
        self._hash = _hashlib.new(self._name)

    def Size(self) -> int:
        return self._hash.digest_size

    def BlockSize(self) -> int:
        return self._hash.block_size


class _HMACWrapper(Hash):
    """Wraps an HMAC object to provide the Go Hash interface."""

    def __init__(self, key: bytes, hash_func: str):
        self._key = key
        self._hash_func = hash_func
        self._hmac = _hmac.new(key, digestmod=hash_func)

    def Write(self, p: bytes) -> tuple[int, Exception | None]:
        try:
            self._hmac.update(p)
            return len(p), None
        except Exception as e:
            return 0, e

    def Sum(self, b: bytes | None = None) -> bytes:
        digest = self._hmac.digest()
        if b is not None:
            return b + digest
        return digest

    def Reset(self) -> None:
        self._hmac = _hmac.new(self._key, digestmod=self._hash_func)

    def Size(self) -> int:
        return self._hmac.digest_size

    def BlockSize(self) -> int:
        return self._hmac.block_size


def New(name: str) -> Hash:
    """New returns a new Hash computing the given hash algorithm."""
    return _HashWrapper(name)


def NewMD5() -> Hash:
    """NewMD5 returns a new Hash computing the MD5 checksum."""
    return _HashWrapper("md5")


def NewSHA1() -> Hash:
    """NewSHA1 returns a new Hash computing the SHA1 checksum."""
    return _HashWrapper("sha1")


def NewSHA224() -> Hash:
    """NewSHA224 returns a new Hash computing the SHA224 checksum."""
    return _HashWrapper("sha224")


def NewSHA256() -> Hash:
    """NewSHA256 returns a new Hash computing the SHA256 checksum."""
    return _HashWrapper("sha256")


def NewSHA384() -> Hash:
    """NewSHA384 returns a new Hash computing the SHA384 checksum."""
    return _HashWrapper("sha384")


def NewSHA512() -> Hash:
    """NewSHA512 returns a new Hash computing the SHA512 checksum."""
    return _HashWrapper("sha512")


def Sum(data: bytes, algorithm: str) -> bytes:
    """Sum returns the hash of the data using the given algorithm."""
    h = _hashlib.new(algorithm)
    h.update(data)
    return h.digest()


def SumMD5(data: bytes) -> bytes:
    """SumMD5 returns the MD5 checksum of the data."""
    return _hashlib.md5(data).digest()


def SumSHA1(data: bytes) -> bytes:
    """SumSHA1 returns the SHA1 checksum of the data."""
    return _hashlib.sha1(data).digest()


def SumSHA256(data: bytes) -> bytes:
    """SumSHA256 returns the SHA256 checksum of the data."""
    return _hashlib.sha256(data).digest()


def SumSHA224(data: bytes) -> bytes:
    """SumSHA224 returns the SHA224 checksum of the data."""
    return _hashlib.sha224(data).digest()


def SumSHA384(data: bytes) -> bytes:
    """SumSHA384 returns the SHA384 checksum of the data."""
    return _hashlib.sha384(data).digest()


def SumSHA512(data: bytes) -> bytes:
    """SumSHA512 returns the SHA512 checksum of the data."""
    return _hashlib.sha512(data).digest()


def NewHMAC(key: bytes, hash_func: str = "sha256") -> Hash:
    """NewHMAC returns a new HMAC hash using the given key and hash function."""
    return _HMACWrapper(key, hash_func)


def HMAC(key: bytes, message: bytes, hash_func: str = "sha256") -> bytes:
    """HMAC returns the HMAC of message using key and hash_func.

    This is a convenience function that computes the HMAC in one call.
    """
    h = _hmac.new(key, message, digestmod=hash_func)
    return h.digest()
