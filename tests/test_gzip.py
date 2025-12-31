import io

from goated.std import gzip


class TestCompress:
    def test_compress_basic(self):
        data = b"Hello, World!"
        result = gzip.Compress(data)
        assert result.is_ok()
        compressed = result.unwrap()
        assert len(compressed) > 0
        assert compressed[:2] == b"\x1f\x8b"

    def test_compress_empty(self):
        result = gzip.Compress(b"")
        assert result.is_ok()

    def test_compress_large(self):
        data = b"x" * 10000
        result = gzip.Compress(data)
        assert result.is_ok()
        compressed = result.unwrap()
        assert len(compressed) < len(data)


class TestDecompress:
    def test_decompress_basic(self):
        data = b"Hello, World!"
        compressed = gzip.Compress(data).unwrap()
        result = gzip.Decompress(compressed)
        assert result.is_ok()
        assert result.unwrap() == data

    def test_decompress_invalid(self):
        result = gzip.Decompress(b"not gzip data")
        assert result.is_err()


class TestRoundTrip:
    def test_roundtrip(self):
        original = b"The quick brown fox jumps over the lazy dog"
        compressed = gzip.Compress(original).unwrap()
        decompressed = gzip.Decompress(compressed).unwrap()
        assert decompressed == original

    def test_roundtrip_unicode(self):
        original = "日本語テスト".encode()
        compressed = gzip.Compress(original).unwrap()
        decompressed = gzip.Decompress(compressed).unwrap()
        assert decompressed == original


class TestNewReader:
    def test_new_reader(self):
        data = b"Test data"
        compressed = gzip.Compress(data).unwrap()
        buf = io.BytesIO(compressed)

        result = gzip.NewReader(buf)
        assert result.is_ok()
        reader = result.unwrap()

        read_result = reader.Read(1024)
        assert read_result.is_ok()
        assert read_result.unwrap() == data

        close_result = reader.Close()
        assert close_result.is_ok()


class TestNewWriter:
    def test_new_writer(self):
        buf = io.BytesIO()
        writer = gzip.NewWriter(buf)

        result = writer.Write(b"Test data")
        assert result.is_ok()
        n = result.unwrap()
        assert n == 9

        close_result = writer.Close()
        assert close_result.is_ok()

        compressed = buf.getvalue()
        decompressed = gzip.Decompress(compressed).unwrap()
        assert decompressed == b"Test data"


class TestNewWriterLevel:
    def test_best_compression(self):
        buf = io.BytesIO()
        result = gzip.NewWriterLevel(buf, gzip.BestCompression)
        assert result.is_ok()
        writer = result.unwrap()

        writer.Write(b"Test data " * 100)
        writer.Close()

    def test_best_speed(self):
        buf = io.BytesIO()
        result = gzip.NewWriterLevel(buf, gzip.BestSpeed)
        assert result.is_ok()

    def test_invalid_level(self):
        buf = io.BytesIO()
        result = gzip.NewWriterLevel(buf, 100)
        assert result.is_err()


class TestWriterFlush:
    def test_flush(self):
        buf = io.BytesIO()
        writer = gzip.NewWriter(buf)

        writer.Write(b"Part 1")
        flush_result = writer.Flush()
        assert flush_result.is_ok()

        intermediate_len = len(buf.getvalue())

        writer.Write(b"Part 2")
        writer.Close()

        final_len = len(buf.getvalue())
        assert final_len > intermediate_len


class TestWriterReset:
    def test_reset(self):
        buf1 = io.BytesIO()
        writer = gzip.NewWriter(buf1)
        writer.Write(b"First")
        writer.Close()

        buf2 = io.BytesIO()
        writer.Reset(buf2)
        writer.Write(b"Second")
        writer.Close()

        assert len(buf1.getvalue()) > 0
        assert len(buf2.getvalue()) > 0
        assert gzip.Decompress(buf2.getvalue()).unwrap() == b"Second"


class TestConstants:
    def test_compression_levels(self):
        assert gzip.NoCompression == 0
        assert gzip.BestSpeed == 1
        assert gzip.BestCompression == 9
        assert gzip.DefaultCompression == -1
        assert gzip.HuffmanOnly == -2
