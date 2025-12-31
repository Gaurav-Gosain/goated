"""Tests for goated.std.binary module (encoding/binary)."""

from io import BytesIO

from goated.std import binary


class TestConstants:
    """Test binary constants."""

    def test_max_varint_len16(self):
        assert binary.MaxVarintLen16 == 3

    def test_max_varint_len32(self):
        assert binary.MaxVarintLen32 == 5

    def test_max_varint_len64(self):
        assert binary.MaxVarintLen64 == 10


class TestByteOrder:
    """Test ByteOrder class."""

    def test_big_endian_name(self):
        assert binary.BigEndian.String() == "BigEndian"

    def test_little_endian_name(self):
        assert binary.LittleEndian.String() == "LittleEndian"


class TestBigEndianUint16:
    """Test BigEndian Uint16 operations."""

    def test_uint16(self):
        b = bytes([0x01, 0x02])
        assert binary.BigEndian.Uint16(b) == 0x0102

    def test_put_uint16(self):
        b = bytearray(2)
        binary.BigEndian.PutUint16(b, 0x0102)
        assert b == bytearray([0x01, 0x02])

    def test_append_uint16(self):
        b = b"prefix"
        result = binary.BigEndian.AppendUint16(b, 0x0102)
        assert result == b"prefix\x01\x02"


class TestBigEndianUint32:
    """Test BigEndian Uint32 operations."""

    def test_uint32(self):
        b = bytes([0x01, 0x02, 0x03, 0x04])
        assert binary.BigEndian.Uint32(b) == 0x01020304

    def test_put_uint32(self):
        b = bytearray(4)
        binary.BigEndian.PutUint32(b, 0x01020304)
        assert b == bytearray([0x01, 0x02, 0x03, 0x04])

    def test_append_uint32(self):
        b = b""
        result = binary.BigEndian.AppendUint32(b, 0x01020304)
        assert result == bytes([0x01, 0x02, 0x03, 0x04])


class TestBigEndianUint64:
    """Test BigEndian Uint64 operations."""

    def test_uint64(self):
        b = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])
        assert binary.BigEndian.Uint64(b) == 0x0102030405060708

    def test_put_uint64(self):
        b = bytearray(8)
        binary.BigEndian.PutUint64(b, 0x0102030405060708)
        assert b == bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])

    def test_append_uint64(self):
        b = b""
        result = binary.BigEndian.AppendUint64(b, 256)
        assert len(result) == 8


class TestLittleEndianUint16:
    """Test LittleEndian Uint16 operations."""

    def test_uint16(self):
        b = bytes([0x02, 0x01])
        assert binary.LittleEndian.Uint16(b) == 0x0102

    def test_put_uint16(self):
        b = bytearray(2)
        binary.LittleEndian.PutUint16(b, 0x0102)
        assert b == bytearray([0x02, 0x01])


class TestLittleEndianUint32:
    """Test LittleEndian Uint32 operations."""

    def test_uint32(self):
        b = bytes([0x04, 0x03, 0x02, 0x01])
        assert binary.LittleEndian.Uint32(b) == 0x01020304

    def test_put_uint32(self):
        b = bytearray(4)
        binary.LittleEndian.PutUint32(b, 0x01020304)
        assert b == bytearray([0x04, 0x03, 0x02, 0x01])


class TestLittleEndianUint64:
    """Test LittleEndian Uint64 operations."""

    def test_uint64(self):
        b = bytes([0x08, 0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01])
        assert binary.LittleEndian.Uint64(b) == 0x0102030405060708

    def test_put_uint64(self):
        b = bytearray(8)
        binary.LittleEndian.PutUint64(b, 0x0102030405060708)
        assert b == bytearray([0x08, 0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01])


class TestWrite:
    """Test Write function."""

    def test_write_bytes(self):
        buf = BytesIO()
        result = binary.Write(buf, binary.BigEndian, b"hello")
        assert result.is_ok()
        assert buf.getvalue() == b"hello"

    def test_write_small_int(self):
        buf = BytesIO()
        result = binary.Write(buf, binary.BigEndian, 42)
        assert result.is_ok()
        assert buf.getvalue() == bytes([42])

    def test_write_uint16_int(self):
        buf = BytesIO()
        result = binary.Write(buf, binary.BigEndian, 0x0102)
        assert result.is_ok()
        assert buf.getvalue() == bytes([0x01, 0x02])

    def test_write_uint32_int(self):
        buf = BytesIO()
        result = binary.Write(buf, binary.BigEndian, 0x01020304)
        assert result.is_ok()
        assert buf.getvalue() == bytes([0x01, 0x02, 0x03, 0x04])

    def test_write_float(self):
        buf = BytesIO()
        result = binary.Write(buf, binary.BigEndian, 3.14)
        assert result.is_ok()
        assert len(buf.getvalue()) == 8

    def test_write_list(self):
        buf = BytesIO()
        result = binary.Write(buf, binary.BigEndian, [1, 2, 3])
        assert result.is_ok()
        assert len(buf.getvalue()) == 3


class TestRead:
    """Test Read function."""

    def test_read_list(self):
        buf = BytesIO(bytes(8 * 2))
        data = [0, 0]
        result = binary.Read(buf, binary.BigEndian, data)
        assert result.is_ok()

    def test_read_eof(self):
        buf = BytesIO(b"")
        data = [0]
        result = binary.Read(buf, binary.BigEndian, data)
        assert result.is_err()
        assert result.err().go_type == "io.EOF"


class TestSize:
    """Test Size function."""

    def test_size_bytes(self):
        assert binary.Size(b"hello") == 5

    def test_size_small_int(self):
        assert binary.Size(42) == 1

    def test_size_uint16_int(self):
        assert binary.Size(0x0102) == 2

    def test_size_uint32_int(self):
        assert binary.Size(0x01020304) == 4

    def test_size_large_int(self):
        assert binary.Size(0x0102030405060708) == 8

    def test_size_negative_int(self):
        assert binary.Size(-1) == 8

    def test_size_float(self):
        assert binary.Size(3.14) == 8

    def test_size_list(self):
        assert binary.Size([1, 2, 3]) == 3

    def test_size_empty(self):
        assert binary.Size(b"") == 0


class TestPutUvarint:
    """Test PutUvarint function."""

    def test_put_uvarint_small(self):
        buf = bytearray(10)
        n = binary.PutUvarint(buf, 1)
        assert n == 1
        assert buf[0] == 1

    def test_put_uvarint_127(self):
        buf = bytearray(10)
        n = binary.PutUvarint(buf, 127)
        assert n == 1
        assert buf[0] == 127

    def test_put_uvarint_128(self):
        buf = bytearray(10)
        n = binary.PutUvarint(buf, 128)
        assert n == 2
        assert buf[0] == 0x80
        assert buf[1] == 1

    def test_put_uvarint_300(self):
        buf = bytearray(10)
        n = binary.PutUvarint(buf, 300)
        assert n == 2


class TestUvarint:
    """Test Uvarint function."""

    def test_uvarint_small(self):
        buf = bytes([1])
        val, n = binary.Uvarint(buf)
        assert val == 1
        assert n == 1

    def test_uvarint_127(self):
        buf = bytes([127])
        val, n = binary.Uvarint(buf)
        assert val == 127
        assert n == 1

    def test_uvarint_128(self):
        buf = bytes([0x80, 0x01])
        val, n = binary.Uvarint(buf)
        assert val == 128
        assert n == 2

    def test_uvarint_empty(self):
        buf = bytes([])
        val, n = binary.Uvarint(buf)
        assert val == 0
        assert n == 0


class TestPutVarint:
    """Test PutVarint function."""

    def test_put_varint_positive(self):
        buf = bytearray(10)
        n = binary.PutVarint(buf, 1)
        assert n >= 1

    def test_put_varint_negative(self):
        buf = bytearray(10)
        n = binary.PutVarint(buf, -1)
        assert n >= 1

    def test_put_varint_zero(self):
        buf = bytearray(10)
        n = binary.PutVarint(buf, 0)
        assert n == 1
        assert buf[0] == 0


class TestVarint:
    """Test Varint function."""

    def test_varint_positive(self):
        buf = bytearray(10)
        binary.PutVarint(buf, 42)
        val, n = binary.Varint(bytes(buf))
        assert val == 42

    def test_varint_negative(self):
        buf = bytearray(10)
        binary.PutVarint(buf, -42)
        val, n = binary.Varint(bytes(buf))
        assert val == -42

    def test_varint_zero(self):
        buf = bytes([0])
        val, n = binary.Varint(buf)
        assert val == 0
        assert n == 1


class TestReadUvarint:
    """Test ReadUvarint function."""

    def test_read_uvarint(self):
        buf = BytesIO(bytes([128, 1]))
        result = binary.ReadUvarint(buf)
        assert result.is_ok()
        assert result.unwrap() == 128

    def test_read_uvarint_eof(self):
        buf = BytesIO(b"")
        result = binary.ReadUvarint(buf)
        assert result.is_err()
        assert result.err().go_type == "io.EOF"


class TestReadVarint:
    """Test ReadVarint function."""

    def test_read_varint(self):
        buf = bytearray(10)
        binary.PutVarint(buf, -100)
        reader = BytesIO(bytes(buf))

        result = binary.ReadVarint(reader)
        assert result.is_ok()
        assert result.unwrap() == -100


class TestRoundTrip:
    """Test roundtrip encoding/decoding."""

    def test_uvarint_roundtrip(self):
        for val in [0, 1, 127, 128, 255, 256, 65535, 2**20]:
            buf = bytearray(10)
            n = binary.PutUvarint(buf, val)
            decoded, m = binary.Uvarint(bytes(buf[:n]))
            assert decoded == val
            assert n == m

    def test_varint_roundtrip(self):
        for val in [0, 1, -1, 127, -128, 1000, -1000]:
            buf = bytearray(10)
            n = binary.PutVarint(buf, val)
            decoded, m = binary.Varint(bytes(buf[:n]))
            assert decoded == val


class TestModuleExports:
    """Test module exports."""

    def test_exports(self):
        assert hasattr(binary, "Read")
        assert hasattr(binary, "Write")
        assert hasattr(binary, "Size")
        assert hasattr(binary, "PutVarint")
        assert hasattr(binary, "PutUvarint")
        assert hasattr(binary, "Varint")
        assert hasattr(binary, "Uvarint")
        assert hasattr(binary, "ReadVarint")
        assert hasattr(binary, "ReadUvarint")
        assert hasattr(binary, "BigEndian")
        assert hasattr(binary, "LittleEndian")
        assert hasattr(binary, "ByteOrder")
        assert hasattr(binary, "MaxVarintLen16")
        assert hasattr(binary, "MaxVarintLen32")
        assert hasattr(binary, "MaxVarintLen64")
