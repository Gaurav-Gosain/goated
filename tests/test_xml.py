from goated.std import xml


class TestMarshal:
    def test_marshal_dict(self):
        data = {"name": "test", "value": 123}
        result = xml.Marshal(data)
        assert result.is_ok()
        output = result.unwrap()
        assert "<name>test</name>" in output
        assert "<value>123</value>" in output

    def test_marshal_list(self):
        data = ["a", "b", "c"]
        result = xml.Marshal(data)
        assert result.is_ok()
        output = result.unwrap()
        assert "<item>a</item>" in output
        assert "<item>b</item>" in output

    def test_marshal_string(self):
        result = xml.Marshal("hello")
        assert result.is_ok()

    def test_marshal_number(self):
        result = xml.Marshal(42)
        assert result.is_ok()


class TestMarshalIndent:
    def test_marshal_indent(self):
        data = {"name": "test"}
        result = xml.MarshalIndent(data, "", "  ")
        assert result.is_ok()
        output = result.unwrap()
        assert "\n" in output


class TestUnmarshal:
    def test_unmarshal_simple(self):
        data = "<root><name>test</name><value>123</value></root>"
        result = xml.Unmarshal(data)
        assert result.is_ok()

    def test_unmarshal_bytes(self):
        data = b"<root><item>hello</item></root>"
        result = xml.Unmarshal(data)
        assert result.is_ok()

    def test_unmarshal_invalid(self):
        result = xml.Unmarshal("<invalid>")
        assert result.is_err()


class TestEscape:
    def test_escape_ampersand(self):
        result = xml.Escape("a & b")
        assert "&amp;" in result

    def test_escape_less_than(self):
        result = xml.Escape("a < b")
        assert "&lt;" in result

    def test_escape_greater_than(self):
        result = xml.Escape("a > b")
        assert "&gt;" in result

    def test_escape_quotes(self):
        result = xml.Escape('say "hello"')
        assert "&quot;" in result


class TestEscapeText:
    def test_escape_text_returns_bytes(self):
        result = xml.EscapeText("a & b")
        assert isinstance(result, bytes)
        assert b"&amp;" in result


class TestDecoder:
    def test_decoder_decode(self):
        data = "<root><name>test</name></root>"
        decoder = xml.Decoder(data)

        result = decoder.Decode()
        assert result.is_ok()


class TestEncoder:
    def test_encoder_encode(self):
        encoder = xml.Encoder()

        result = encoder.Encode({"name": "test"})
        assert result.is_ok()

        flush_result = encoder.Flush()
        assert flush_result.is_ok()
        assert len(flush_result.unwrap()) > 0


class TestRoundTrip:
    def test_roundtrip_dict(self):
        original = {"name": "test", "count": "42"}
        marshaled = xml.Marshal(original).unwrap()
        result = xml.Unmarshal(marshaled)
        assert result.is_ok()


class TestComplexStructures:
    def test_nested_dict(self):
        data = {"person": {"name": "John", "age": "30"}}
        result = xml.Marshal(data)
        assert result.is_ok()
        output = result.unwrap()
        assert "<person>" in output
        assert "<name>John</name>" in output

    def test_mixed_content(self):
        data = {"items": ["a", "b", "c"], "count": "3"}
        result = xml.Marshal(data)
        assert result.is_ok()
