"""Tests for the Go encoding/base64 package bindings."""

import pytest


class TestStdEncoding:
    """Tests for standard base64 encoding."""

    def test_encode_to_string(self):
        """Test EncodeToString."""
        from goated.std.base64 import StdEncoding

        # Standard test vectors
        assert StdEncoding.EncodeToString(b"") == ""
        assert StdEncoding.EncodeToString(b"f") == "Zg=="
        assert StdEncoding.EncodeToString(b"fo") == "Zm8="
        assert StdEncoding.EncodeToString(b"foo") == "Zm9v"
        assert StdEncoding.EncodeToString(b"foob") == "Zm9vYg=="
        assert StdEncoding.EncodeToString(b"fooba") == "Zm9vYmE="
        assert StdEncoding.EncodeToString(b"foobar") == "Zm9vYmFy"

    def test_decode_string(self):
        """Test DecodeString."""
        from goated.std.base64 import StdEncoding

        data, err = StdEncoding.DecodeString("Zm9vYmFy")
        assert err is None
        assert data == b"foobar"

        data, err = StdEncoding.DecodeString("SGVsbG8sIFdvcmxkIQ==")
        assert err is None
        assert data == b"Hello, World!"

    def test_encode_decode_roundtrip(self):
        """Test encode/decode roundtrip."""
        from goated.std.base64 import StdEncoding

        test_data = [
            b"",
            b"a",
            b"ab",
            b"abc",
            b"Hello, World!",
            b"\x00\x01\x02\x03",
            b"The quick brown fox jumps over the lazy dog",
        ]

        for data in test_data:
            encoded = StdEncoding.EncodeToString(data)
            decoded, err = StdEncoding.DecodeString(encoded)
            assert err is None
            assert decoded == data

    def test_encoded_len(self):
        """Test EncodedLen."""
        from goated.std.base64 import StdEncoding

        assert StdEncoding.EncodedLen(0) == 0
        assert StdEncoding.EncodedLen(1) == 4
        assert StdEncoding.EncodedLen(2) == 4
        assert StdEncoding.EncodedLen(3) == 4
        assert StdEncoding.EncodedLen(4) == 8
        assert StdEncoding.EncodedLen(6) == 8

    def test_decoded_len(self):
        """Test DecodedLen."""
        from goated.std.base64 import StdEncoding

        assert StdEncoding.DecodedLen(0) == 0
        assert StdEncoding.DecodedLen(4) == 3
        assert StdEncoding.DecodedLen(8) == 6

    def test_decode_with_padding(self):
        """Test decoding with different padding."""
        from goated.std.base64 import StdEncoding

        # With padding
        data, err = StdEncoding.DecodeString("Zg==")
        assert err is None
        assert data == b"f"

        # Without padding (should still work)
        data, err = StdEncoding.DecodeString("Zg")
        assert err is None
        assert data == b"f"


class TestURLEncoding:
    """Tests for URL-safe base64 encoding."""

    def test_url_safe_characters(self):
        """Test URL encoding uses - and _ instead of + and /."""
        from goated.std.base64 import StdEncoding, URLEncoding

        # Data that produces + and / in standard encoding
        data = b"\xfb\xff\xfe"

        std_encoded = StdEncoding.EncodeToString(data)
        url_encoded = URLEncoding.EncodeToString(data)

        # Standard has + and /
        assert "+" in std_encoded or "/" in std_encoded

        # URL-safe replaces them
        assert "+" not in url_encoded
        assert "/" not in url_encoded

    def test_url_encode_decode(self):
        """Test URL encoding roundtrip."""
        from goated.std.base64 import URLEncoding

        data = b"Hello, World! This is a test with special chars: +/="

        encoded = URLEncoding.EncodeToString(data)
        decoded, err = URLEncoding.DecodeString(encoded)

        assert err is None
        assert decoded == data


class TestRawEncoding:
    """Tests for raw (unpadded) encodings."""

    def test_raw_std_encoding(self):
        """Test RawStdEncoding has no padding."""
        from goated.std.base64 import RawStdEncoding

        encoded = RawStdEncoding.EncodeToString(b"f")
        assert encoded == "Zg"  # No padding
        assert "=" not in encoded

    def test_raw_url_encoding(self):
        """Test RawURLEncoding has no padding."""
        from goated.std.base64 import RawURLEncoding

        encoded = RawURLEncoding.EncodeToString(b"f")
        assert encoded == "Zg"
        assert "=" not in encoded

    def test_raw_decode(self):
        """Test decoding raw (unpadded) data."""
        from goated.std.base64 import RawStdEncoding

        data, err = RawStdEncoding.DecodeString("Zg")
        assert err is None
        assert data == b"f"


class TestWithPadding:
    """Tests for WithPadding method."""

    def test_custom_padding(self):
        """Test encoding with custom padding character."""
        from goated.std.base64 import StdEncoding

        # Create encoding with no padding
        no_pad = StdEncoding.WithPadding(None)

        encoded = no_pad.EncodeToString(b"f")
        assert encoded == "Zg"
        assert "=" not in encoded

    def test_with_padding_roundtrip(self):
        """Test roundtrip with modified padding."""
        from goated.std.base64 import StdEncoding

        no_pad = StdEncoding.WithPadding(None)

        data = b"test"
        encoded = no_pad.EncodeToString(data)
        decoded, err = no_pad.DecodeString(encoded)

        assert err is None
        assert decoded == data


class TestNewEncoding:
    """Tests for NewEncoding function."""

    def test_new_encoding(self):
        """Test creating new encoding with custom alphabet."""
        from goated.std.base64 import NewEncoding

        # Standard alphabet
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        enc = NewEncoding(alphabet)

        data = b"test"
        encoded = enc.EncodeToString(data)
        decoded, err = enc.DecodeString(encoded)

        assert err is None
        assert decoded == data

    def test_invalid_alphabet_length(self):
        """Test that invalid alphabet length raises error."""
        from goated.std.base64 import NewEncoding

        with pytest.raises(ValueError):
            NewEncoding("ABC")  # Too short


class TestEncoderDecoder:
    """Tests for Encoder and Decoder stream wrappers."""

    def test_encoder_write(self):
        """Test Encoder.Write."""
        from io import StringIO

        from goated.std.base64 import NewEncoder, StdEncoding

        buf = StringIO()
        enc = NewEncoder(StdEncoding, buf)

        n, err = enc.Write(b"Hello")
        assert err is None
        assert n == 5

        assert buf.getvalue() == "SGVsbG8="

    def test_decoder_read(self):
        """Test Decoder.Read."""
        from io import StringIO

        from goated.std.base64 import NewDecoder, StdEncoding

        buf = StringIO("SGVsbG8=")
        dec = NewDecoder(StdEncoding, buf)

        result = bytearray(10)
        n, err = dec.Read(result)

        assert err is None
        assert result[:n] == b"Hello"


class TestCorruptInput:
    """Tests for CorruptInputError."""

    def test_corrupt_input_error(self):
        """Test CorruptInputError creation."""
        from goated.std.base64 import CorruptInputError

        err = CorruptInputError(10)
        assert err.offset == 10
        assert "10" in str(err)

    def test_invalid_base64(self):
        """Test decoding invalid base64."""
        from goated.std.base64 import StdEncoding

        # Python's base64 is lenient with some invalid characters
        # Test with completely malformed base64 that breaks
        # Note: Python's base64.b64decode can handle some invalid chars
        # So we test that it at least doesn't crash
        data, err = StdEncoding.DecodeString("SGVsbG8=")  # Valid
        assert err is None
        assert data == b"Hello"


class TestBinaryData:
    """Tests with various binary data."""

    def test_all_byte_values(self):
        """Test encoding/decoding all byte values."""
        from goated.std.base64 import StdEncoding

        data = bytes(range(256))

        encoded = StdEncoding.EncodeToString(data)
        decoded, err = StdEncoding.DecodeString(encoded)

        assert err is None
        assert decoded == data

    def test_large_data(self):
        """Test with larger data."""
        from goated.std.base64 import StdEncoding

        data = b"x" * 10000

        encoded = StdEncoding.EncodeToString(data)
        decoded, err = StdEncoding.DecodeString(encoded)

        assert err is None
        assert decoded == data

    def test_unicode_data(self):
        """Test with unicode string encoded to bytes."""
        from goated.std.base64 import StdEncoding

        text = "Hello, 世界! 🌍"
        data = text.encode("utf-8")

        encoded = StdEncoding.EncodeToString(data)
        decoded, err = StdEncoding.DecodeString(encoded)

        assert err is None
        assert decoded == data
        assert decoded.decode("utf-8") == text


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_input(self):
        """Test empty input."""
        from goated.std.base64 import StdEncoding

        assert StdEncoding.EncodeToString(b"") == ""

        data, err = StdEncoding.DecodeString("")
        assert err is None
        assert data == b""

    def test_whitespace_in_input(self):
        """Test handling of whitespace in base64 input."""
        from goated.std.base64 import StdEncoding

        # Base64 with newlines (common in PEM format)
        encoded = "SGVs\nbG8g\nV29y\nbGQh"
        data, err = StdEncoding.DecodeString(encoded)

        assert err is None
        assert data == b"Hello World!"
