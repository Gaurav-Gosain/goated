from __future__ import annotations

import random as _random
from collections.abc import Callable
from typing import TypeVar

__all__ = [
    "Seed",
    "Int",
    "Intn",
    "Int31",
    "Int31n",
    "Int63",
    "Int63n",
    "Uint32",
    "Uint64",
    "Float32",
    "Float64",
    "NormFloat64",
    "ExpFloat64",
    "Perm",
    "Shuffle",
    "Read",
    "NewSource",
    "New",
    "Rand",
    "Source",
]

_rng = _random.Random()


def Seed(seed: int) -> None:
    """Seed uses the provided seed value to initialize the default Source."""
    _rng.seed(seed)


def Int() -> int:
    """Int returns a non-negative pseudo-random int."""
    return _rng.randint(0, (1 << 63) - 1)


def Intn(n: int) -> int:
    """Intn returns a non-negative pseudo-random number in [0,n)."""
    if n <= 0:
        raise ValueError("invalid argument to Intn")
    return _rng.randint(0, n - 1)


def Int31() -> int:
    """Int31 returns a non-negative pseudo-random 31-bit integer."""
    return _rng.randint(0, (1 << 31) - 1)


def Int31n(n: int) -> int:
    """Int31n returns a non-negative pseudo-random number in [0,n)."""
    if n <= 0:
        raise ValueError("invalid argument to Int31n")
    return _rng.randint(0, min(n - 1, (1 << 31) - 1))


def Int63() -> int:
    """Int63 returns a non-negative pseudo-random 63-bit integer."""
    return _rng.randint(0, (1 << 63) - 1)


def Int63n(n: int) -> int:
    """Int63n returns a non-negative pseudo-random number in [0,n)."""
    if n <= 0:
        raise ValueError("invalid argument to Int63n")
    return _rng.randint(0, n - 1)


def Uint32() -> int:
    """Uint32 returns a pseudo-random 32-bit value."""
    return _rng.randint(0, (1 << 32) - 1)


def Uint64() -> int:
    """Uint64 returns a pseudo-random 64-bit value."""
    return _rng.randint(0, (1 << 64) - 1)


def Float32() -> float:
    """Float32 returns a pseudo-random number in [0.0,1.0)."""
    return _rng.random()


def Float64() -> float:
    """Float64 returns a pseudo-random number in [0.0,1.0)."""
    return _rng.random()


def NormFloat64() -> float:
    """NormFloat64 returns a normally distributed float64 in [-inf, +inf]."""
    return _rng.gauss(0, 1)


def ExpFloat64() -> float:
    """ExpFloat64 returns an exponentially distributed float64 in (0, +inf]."""
    return _rng.expovariate(1)


T = TypeVar("T")


def Perm(n: int) -> list[int]:
    """Perm returns a pseudo-random permutation of the integers [0,n)."""
    result = list(range(n))
    _rng.shuffle(result)
    return result


def Shuffle(n: int, swap: Callable[[int, int], None]) -> None:
    """Shuffle pseudo-randomizes the order of elements using swap func."""
    for i in range(n - 1, 0, -1):
        j = _rng.randint(0, i)
        swap(i, j)


def Read(p: bytearray) -> tuple[int, None]:
    """Read generates len(p) random bytes and writes them into p."""
    for i in range(len(p)):
        p[i] = _rng.randint(0, 255)
    return len(p), None


class Source:
    """Source represents a source of uniformly-distributed pseudo-random int64 values."""

    def __init__(self, seed: int = 0):
        self._rng = _random.Random(seed)

    def Int63(self) -> int:
        return self._rng.randint(0, (1 << 63) - 1)

    def Seed(self, seed: int) -> None:
        self._rng.seed(seed)


class Rand:
    """Rand is a source of random numbers."""

    def __init__(self, src: Source):
        self._src = src
        self._rng = src._rng

    def Int(self) -> int:
        return self._rng.randint(0, (1 << 63) - 1)

    def Intn(self, n: int) -> int:
        if n <= 0:
            raise ValueError("invalid argument to Intn")
        return self._rng.randint(0, n - 1)

    def Int31(self) -> int:
        return self._rng.randint(0, (1 << 31) - 1)

    def Int31n(self, n: int) -> int:
        if n <= 0:
            raise ValueError("invalid argument to Int31n")
        return self._rng.randint(0, min(n - 1, (1 << 31) - 1))

    def Int63(self) -> int:
        return self._rng.randint(0, (1 << 63) - 1)

    def Int63n(self, n: int) -> int:
        if n <= 0:
            raise ValueError("invalid argument to Int63n")
        return self._rng.randint(0, n - 1)

    def Uint32(self) -> int:
        return self._rng.randint(0, (1 << 32) - 1)

    def Uint64(self) -> int:
        return self._rng.randint(0, (1 << 64) - 1)

    def Float32(self) -> float:
        return self._rng.random()

    def Float64(self) -> float:
        return self._rng.random()

    def NormFloat64(self) -> float:
        return self._rng.gauss(0, 1)

    def ExpFloat64(self) -> float:
        return self._rng.expovariate(1)

    def Perm(self, n: int) -> list[int]:
        result = list(range(n))
        self._rng.shuffle(result)
        return result

    def Shuffle(self, n: int, swap: Callable[[int, int], None]) -> None:
        for i in range(n - 1, 0, -1):
            j = self._rng.randint(0, i)
            swap(i, j)

    def Read(self, p: bytearray) -> tuple[int, None]:
        for i in range(len(p)):
            p[i] = self._rng.randint(0, 255)
        return len(p), None

    def Seed(self, seed: int) -> None:
        self._src.Seed(seed)


def NewSource(seed: int) -> Source:
    """NewSource returns a new pseudo-random Source seeded with the given value."""
    return Source(seed)


def New(src: Source) -> Rand:
    """New returns a new Rand that uses random values from src."""
    return Rand(src)
