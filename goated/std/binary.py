from __future__ import annotations

import struct
from typing import IO, Any

from goated.result import Err, GoError, Ok, Result

__all__ = [
    "Read",
    "Write",
    "Size",
    "PutVarint",
    "PutUvarint",
    "Varint",
    "Uvarint",
    "ReadVarint",
    "ReadUvarint",
    "BigEndian",
    "LittleEndian",
    "ByteOrder",
    "MaxVarintLen16",
    "MaxVarintLen32",
    "MaxVarintLen64",
]

MaxVarintLen16 = 3
MaxVarintLen32 = 5
MaxVarintLen64 = 10


class ByteOrder:
    """ByteOrder specifies how to convert byte slices into integers."""

    def __init__(self, name: str, format_prefix: str):
        self._name = name
        self._prefix = format_prefix

    def Uint16(self, b: bytes) -> int:
        """Uint16 returns the uint16 in b."""
        result: int = struct.unpack(f"{self._prefix}H", b[:2])[0]
        return result

    def Uint32(self, b: bytes) -> int:
        """Uint32 returns the uint32 in b."""
        result: int = struct.unpack(f"{self._prefix}I", b[:4])[0]
        return result

    def Uint64(self, b: bytes) -> int:
        """Uint64 returns the uint64 in b."""
        result: int = struct.unpack(f"{self._prefix}Q", b[:8])[0]
        return result

    def PutUint16(self, b: bytearray, v: int) -> None:
        """PutUint16 encodes v into b."""
        data = struct.pack(f"{self._prefix}H", v)
        b[:2] = data

    def PutUint32(self, b: bytearray, v: int) -> None:
        """PutUint32 encodes v into b."""
        data = struct.pack(f"{self._prefix}I", v)
        b[:4] = data

    def PutUint64(self, b: bytearray, v: int) -> None:
        """PutUint64 encodes v into b."""
        data = struct.pack(f"{self._prefix}Q", v)
        b[:8] = data

    def AppendUint16(self, b: bytes, v: int) -> bytes:
        """AppendUint16 appends v to b."""
        return b + struct.pack(f"{self._prefix}H", v)

    def AppendUint32(self, b: bytes, v: int) -> bytes:
        """AppendUint32 appends v to b."""
        return b + struct.pack(f"{self._prefix}I", v)

    def AppendUint64(self, b: bytes, v: int) -> bytes:
        """AppendUint64 appends v to b."""
        return b + struct.pack(f"{self._prefix}Q", v)

    def String(self) -> str:
        """String returns the name of the byte order."""
        return self._name


BigEndian = ByteOrder("BigEndian", ">")
LittleEndian = ByteOrder("LittleEndian", "<")


def Read(r: IO[bytes], order: ByteOrder, data: Any) -> Result[None, GoError]:
    """Read reads structured binary data from r into data."""
    try:
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, int):
                    b = r.read(8)
                    if len(b) < 8:
                        return Err(GoError("unexpected EOF", "io.EOF"))
                    data[i] = order.Uint64(b)
        elif hasattr(data, "__dict__"):
            for name, value in data.__dict__.items():
                if isinstance(value, int):
                    b = r.read(8)
                    if len(b) < 8:
                        return Err(GoError("unexpected EOF", "io.EOF"))
                    setattr(data, name, order.Uint64(b))
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "binary.ReadError"))


def Write(w: IO[bytes], order: ByteOrder, data: Any) -> Result[None, GoError]:
    """Write writes the binary representation of data to w."""
    try:
        if isinstance(data, bytes):
            w.write(data)
        elif isinstance(data, int):
            if data < 0:
                w.write(struct.pack(f"{order._prefix}q", data))
            elif data <= 0xFF:
                w.write(struct.pack("B", data))
            elif data <= 0xFFFF:
                w.write(struct.pack(f"{order._prefix}H", data))
            elif data <= 0xFFFFFFFF:
                w.write(struct.pack(f"{order._prefix}I", data))
            else:
                w.write(struct.pack(f"{order._prefix}Q", data))
        elif isinstance(data, float):
            w.write(struct.pack(f"{order._prefix}d", data))
        elif isinstance(data, (list, tuple)):
            for item in data:
                Write(w, order, item)
        elif hasattr(data, "__dict__"):
            for value in data.__dict__.values():
                Write(w, order, value)
        return Ok(None)
    except Exception as e:
        return Err(GoError(str(e), "binary.WriteError"))


def Size(v: Any) -> int:
    """Size returns how many bytes Write would generate to encode the value v."""
    if isinstance(v, bytes):
        return len(v)
    elif isinstance(v, int):
        if v < 0 or v > 0xFFFFFFFF:
            return 8
        elif v <= 0xFF:
            return 1
        elif v <= 0xFFFF:
            return 2
        else:
            return 4
    elif isinstance(v, float):
        return 8
    elif isinstance(v, (list, tuple)):
        return sum(Size(item) for item in v)
    elif hasattr(v, "__dict__"):
        return sum(Size(val) for val in v.__dict__.values())
    return 0


def PutVarint(buf: bytearray, x: int) -> int:
    """PutVarint encodes an int64 into buf and returns the number of bytes written."""
    ux = (x << 1) ^ (x >> 63)
    return PutUvarint(buf, ux)


def PutUvarint(buf: bytearray, x: int) -> int:
    """PutUvarint encodes a uint64 into buf and returns the number of bytes written."""
    i = 0
    while x >= 0x80:
        buf[i] = (x & 0x7F) | 0x80
        x >>= 7
        i += 1
    buf[i] = x & 0xFF
    return i + 1


def Varint(buf: bytes) -> tuple[int, int]:
    """Varint decodes an int64 from buf and returns it and the number of bytes read."""
    ux, n = Uvarint(buf)
    x = ux >> 1
    if ux & 1:
        x = ~x
    return x, n


def Uvarint(buf: bytes) -> tuple[int, int]:
    """Uvarint decodes a uint64 from buf and returns it and the number of bytes read."""
    x = 0
    s = 0
    for i, b in enumerate(buf):
        if i == MaxVarintLen64:
            return 0, -(i + 1)
        if b < 0x80:
            if i == MaxVarintLen64 - 1 and b > 1:
                return 0, -(i + 1)
            return x | (b << s), i + 1
        x |= (b & 0x7F) << s
        s += 7
    return 0, 0


def ReadVarint(r: IO[bytes]) -> Result[int, GoError]:
    """ReadVarint reads an encoded signed integer from r."""
    result = ReadUvarint(r)
    if result.is_err():
        return result
    ux = result.unwrap()
    x = ux >> 1
    if ux & 1:
        x = ~x
    return Ok(x)


def ReadUvarint(r: IO[bytes]) -> Result[int, GoError]:
    """ReadUvarint reads an encoded unsigned integer from r."""
    x = 0
    s = 0
    for i in range(MaxVarintLen64):
        b = r.read(1)
        if not b:
            return Err(GoError("unexpected EOF", "io.EOF"))
        byte = b[0]
        if byte < 0x80:
            if i == MaxVarintLen64 - 1 and byte > 1:
                return Err(GoError("overflow", "binary.Overflow"))
            return Ok(x | (byte << s))
        x |= (byte & 0x7F) << s
        s += 7
    return Err(GoError("overflow", "binary.Overflow"))


def AppendVarint(b: bytes, x: int) -> bytes:
    """AppendVarint appends the varint-encoded form of x to b."""
    ux = (x << 1) ^ (x >> 63)
    return AppendUvarint(b, ux)


def AppendUvarint(b: bytes, x: int) -> bytes:
    """AppendUvarint appends the varint-encoded form of x to b."""
    result = bytearray(b)
    while x >= 0x80:
        result.append((x & 0x7F) | 0x80)
        x >>= 7
    result.append(x)
    return bytes(result)
