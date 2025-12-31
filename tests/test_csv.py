import io

from goated.std import csv


class TestNewReader:
    def test_read_simple(self):
        data = "a,b,c\n1,2,3\n"
        r = csv.NewReader(io.StringIO(data))

        result = r.Read()
        assert result.is_ok()
        assert result.unwrap() == ["a", "b", "c"]

        result = r.Read()
        assert result.is_ok()
        assert result.unwrap() == ["1", "2", "3"]

    def test_read_quoted(self):
        data = '"a,b",c,d\n'
        r = csv.NewReader(io.StringIO(data))

        result = r.Read()
        assert result.is_ok()
        assert result.unwrap() == ["a,b", "c", "d"]

    def test_read_all(self):
        data = "a,b,c\n1,2,3\n4,5,6\n"
        r = csv.NewReader(io.StringIO(data))

        result = r.ReadAll()
        assert result.is_ok()
        records = result.unwrap()
        assert len(records) == 3
        assert records[0] == ["a", "b", "c"]
        assert records[1] == ["1", "2", "3"]
        assert records[2] == ["4", "5", "6"]

    def test_read_eof(self):
        data = "a,b\n"
        r = csv.NewReader(io.StringIO(data))

        r.Read()
        result = r.Read()
        assert result.is_err()

    def test_custom_comma(self):
        data = "a;b;c\n1;2;3\n"
        r = csv.NewReader(io.StringIO(data))
        r.Comma = ";"

        result = r.Read()
        assert result.is_ok()
        assert result.unwrap() == ["a", "b", "c"]


class TestNewWriter:
    def test_write_simple(self):
        buf = io.StringIO()
        w = csv.NewWriter(buf)

        result = w.Write(["a", "b", "c"])
        assert result.is_ok()

        w.Flush()
        assert buf.getvalue() == "a,b,c\n"

    def test_write_quoted(self):
        buf = io.StringIO()
        w = csv.NewWriter(buf)

        result = w.Write(["a,b", "c", "d"])
        assert result.is_ok()

        w.Flush()
        assert buf.getvalue() == '"a,b",c,d\n'

    def test_write_all(self):
        buf = io.StringIO()
        w = csv.NewWriter(buf)

        records = [["a", "b"], ["1", "2"]]
        result = w.WriteAll(records)
        assert result.is_ok()

        lines = buf.getvalue().strip().split("\n")
        assert len(lines) == 2
        assert lines[0] == "a,b"
        assert lines[1] == "1,2"

    def test_custom_comma(self):
        buf = io.StringIO()
        w = csv.NewWriter(buf)
        w.Comma = ";"

        w.Write(["a", "b", "c"])
        w.Flush()

        assert buf.getvalue() == "a;b;c\n"

    def test_custom_crlf(self):
        buf = io.StringIO()
        w = csv.NewWriter(buf)
        w.UseCRLF = False

        w.Write(["a", "b"])
        w.Flush()

        assert buf.getvalue() == "a,b\n"


class TestRoundTrip:
    def test_roundtrip(self):
        records = [
            ["Name", "Age", "City"],
            ["Alice", "30", "New York"],
            ["Bob", "25", "Los Angeles"],
        ]

        buf = io.StringIO()
        w = csv.NewWriter(buf)
        w.WriteAll(records)

        buf.seek(0)
        r = csv.NewReader(buf)
        result = r.ReadAll()

        assert result.is_ok()
        assert result.unwrap() == records


class TestSpecialCases:
    def test_empty_field(self):
        buf = io.StringIO()
        w = csv.NewWriter(buf)
        w.Write(["a", "", "c"])
        w.Flush()

        buf.seek(0)
        r = csv.NewReader(buf)
        result = r.Read()

        assert result.is_ok()
        assert result.unwrap() == ["a", "", "c"]

    def test_newline_in_field(self):
        buf = io.StringIO()
        w = csv.NewWriter(buf)
        w.Write(["a\nb", "c"])
        w.Flush()

        buf.seek(0)
        r = csv.NewReader(buf)
        result = r.Read()

        assert result.is_ok()
        assert result.unwrap() == ["a\nb", "c"]

    def test_quote_in_field(self):
        buf = io.StringIO()
        w = csv.NewWriter(buf)
        w.Write(['say "hello"', "world"])
        w.Flush()

        buf.seek(0)
        r = csv.NewReader(buf)
        result = r.Read()

        assert result.is_ok()
        assert result.unwrap() == ['say "hello"', "world"]


class TestFieldsPerRecord:
    def test_variable_fields(self):
        data = "a,b,c\n1,2\n"
        r = csv.NewReader(io.StringIO(data))
        r.FieldsPerRecord = -1

        result = r.ReadAll()
        assert result.is_ok()
        records = result.unwrap()
        assert len(records[0]) == 3
        assert len(records[1]) == 2
