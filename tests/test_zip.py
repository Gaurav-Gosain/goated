"""Tests for goated.std.zip module (archive/zip)."""

import os
import tempfile
from datetime import datetime
from io import BytesIO

from goated.std import zip as gozip


class TestConstants:
    """Test zip constants."""

    def test_store_constant(self):
        import zipfile

        assert gozip.Store == zipfile.ZIP_STORED

    def test_deflate_constant(self):
        import zipfile

        assert gozip.Deflate == zipfile.ZIP_DEFLATED


class TestFileHeader:
    """Test FileHeader class."""

    def test_default_values(self):
        fh = gozip.FileHeader()
        assert fh.Name == ""
        assert fh.Comment == ""
        assert fh.Method == gozip.Deflate

    def test_set_values(self):
        fh = gozip.FileHeader(
            Name="test.txt",
            Comment="A test file",
            Method=gozip.Store,
        )
        assert fh.Name == "test.txt"
        assert fh.Comment == "A test file"
        assert fh.Method == gozip.Store

    def test_file_info(self):
        now = datetime.now()
        fh = gozip.FileHeader(
            Name="path/to/file.txt",
            UncompressedSize64=100,
            Modified=now,
        )
        info = fh.FileInfo()
        assert info.Name() == "file.txt"
        assert info.Size() == 100
        assert info.ModTime() == now
        assert not info.IsDir()

    def test_file_info_directory(self):
        fh = gozip.FileHeader(Name="mydir/")
        info = fh.FileInfo()
        assert info.IsDir()

    def test_mode(self):
        fh = gozip.FileHeader()
        fh.ExternalAttrs = 0o644 << 16
        assert fh.Mode() == 0o644

    def test_set_mode(self):
        fh = gozip.FileHeader()
        fh.SetMode(0o755)
        assert fh.Mode() == 0o755


class TestFileInfo:
    """Test FileInfo class."""

    def test_file_info_methods(self):
        now = datetime.now()
        info = gozip.FileInfo(
            name="test.txt",
            size=1024,
            mode=0o644,
            mod_time=now,
            is_dir=False,
        )
        assert info.Name() == "test.txt"
        assert info.Size() == 1024
        assert info.Mode() == 0o644
        assert info.ModTime() == now
        assert not info.IsDir()


class TestWriter:
    """Test zip Writer."""

    def test_create_empty_zip(self):
        buf = BytesIO()
        w = gozip.NewWriter(buf)
        result = w.Close()
        assert result.is_ok()
        assert len(buf.getvalue()) > 0

    def test_create_file(self):
        buf = BytesIO()
        w = gozip.NewWriter(buf)

        result = w.Create("hello.txt")
        assert result.is_ok()

        f = result.unwrap()
        f.write(b"Hello, World!")
        f.close()

        w.Close()

        assert len(buf.getvalue()) > 0

    def test_create_multiple_files(self):
        buf = BytesIO()
        w = gozip.NewWriter(buf)

        for name in ["file1.txt", "file2.txt", "file3.txt"]:
            result = w.Create(name)
            assert result.is_ok()
            f = result.unwrap()
            f.write(f"Content of {name}".encode())
            f.close()

        w.Close()

        buf.seek(0)
        import zipfile

        with zipfile.ZipFile(buf, "r") as zf:
            assert len(zf.namelist()) == 3

    def test_create_header(self):
        buf = BytesIO()
        w = gozip.NewWriter(buf)

        fh = gozip.FileHeader(
            Name="custom.txt",
            Comment="Custom file",
            Method=gozip.Store,
        )

        result = w.CreateHeader(fh)
        assert result.is_ok()

        f = result.unwrap()
        f.write(b"Custom content")
        f.close()

        w.Close()

    def test_set_comment(self):
        buf = BytesIO()
        w = gozip.NewWriter(buf)
        w.SetComment("Archive comment")
        w.Close()

        buf.seek(0)
        import zipfile

        with zipfile.ZipFile(buf, "r") as zf:
            assert zf.comment == b"Archive comment"

    def test_context_manager(self):
        buf = BytesIO()
        with gozip.NewWriter(buf) as w:
            result = w.Create("test.txt")
            f = result.unwrap()
            f.write(b"test")
            f.close()

        assert len(buf.getvalue()) > 0


class TestReader:
    """Test zip Reader."""

    def test_read_zip(self):
        buf = BytesIO()
        import zipfile

        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("test.txt", "Hello")

        buf.seek(0)
        result = gozip.NewReader(buf, len(buf.getvalue()))
        assert result.is_ok()

        reader = result.unwrap()
        assert len(reader.File) == 1
        assert reader.File[0].FileHeader.Name == "test.txt"

    def test_read_file_content(self):
        buf = BytesIO()
        import zipfile

        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("hello.txt", "Hello, World!")

        buf.seek(0)
        result = gozip.NewReader(buf, len(buf.getvalue()))
        reader = result.unwrap()

        file_result = reader.File[0].Read()
        assert file_result.is_ok()
        assert file_result.unwrap() == b"Hello, World!"

    def test_open_file(self):
        buf = BytesIO()
        import zipfile

        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("data.txt", "Some data")

        buf.seek(0)
        result = gozip.NewReader(buf, len(buf.getvalue()))
        reader = result.unwrap()

        open_result = reader.Open("data.txt")
        assert open_result.is_ok()

        f = open_result.unwrap()
        assert f.read() == b"Some data"

    def test_open_nonexistent_file(self):
        buf = BytesIO()
        import zipfile

        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("exists.txt", "content")

        buf.seek(0)
        result = gozip.NewReader(buf, len(buf.getvalue()))
        reader = result.unwrap()

        open_result = reader.Open("notfound.txt")
        assert open_result.is_err()

    def test_read_comment(self):
        buf = BytesIO()
        import zipfile

        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("test.txt", "content")
            zf.comment = b"Archive comment"

        buf.seek(0)
        result = gozip.NewReader(buf, len(buf.getvalue()))
        reader = result.unwrap()
        assert reader.Comment == "Archive comment"

    def test_close(self):
        buf = BytesIO()
        import zipfile

        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("test.txt", "content")

        buf.seek(0)
        result = gozip.NewReader(buf, len(buf.getvalue()))
        reader = result.unwrap()

        close_result = reader.Close()
        assert close_result.is_ok()


class TestOpenReader:
    """Test OpenReader function."""

    def test_open_reader(self):
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
            path = f.name

        try:
            import zipfile

            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("test.txt", "Hello from file")

            result = gozip.OpenReader(path)
            assert result.is_ok()

            reader = result.unwrap()
            assert len(reader.File) == 1

            content = reader.File[0].Read()
            assert content.unwrap() == b"Hello from file"

            reader.Close()
        finally:
            os.unlink(path)

    def test_open_reader_not_found(self):
        result = gozip.OpenReader("/nonexistent/path/file.zip")
        assert result.is_err()
        assert result.err().go_type == "os.ErrNotExist"


class TestRoundTrip:
    """Test writing and reading zip files."""

    def test_roundtrip_single_file(self):
        buf = BytesIO()

        w = gozip.NewWriter(buf)
        f_result = w.Create("message.txt")
        f = f_result.unwrap()
        f.write(b"Round trip test!")
        f.close()
        w.Close()

        buf.seek(0)
        r_result = gozip.NewReader(buf, len(buf.getvalue()))
        r = r_result.unwrap()

        assert len(r.File) == 1
        content = r.File[0].Read().unwrap()
        assert content == b"Round trip test!"

    def test_roundtrip_multiple_files(self):
        files = {
            "a.txt": b"Content A",
            "b.txt": b"Content B",
            "dir/c.txt": b"Content C",
        }

        buf = BytesIO()
        w = gozip.NewWriter(buf)

        for name, content in files.items():
            f = w.Create(name).unwrap()
            f.write(content)
            f.close()

        w.Close()

        buf.seek(0)
        r = gozip.NewReader(buf, len(buf.getvalue())).unwrap()

        assert len(r.File) == 3

        for file in r.File:
            expected = files[file.FileHeader.Name]
            actual = file.Read().unwrap()
            assert actual == expected


class TestBadZip:
    """Test handling of invalid zip files."""

    def test_invalid_zip_data(self):
        buf = BytesIO(b"not a zip file")
        result = gozip.NewReader(buf, 14)
        assert result.is_err()
        assert result.err().go_type == "zip.ErrFormat"


class TestModuleExports:
    """Test module exports."""

    def test_exports(self):
        assert hasattr(gozip, "OpenReader")
        assert hasattr(gozip, "NewReader")
        assert hasattr(gozip, "NewWriter")
        assert hasattr(gozip, "Reader")
        assert hasattr(gozip, "Writer")
        assert hasattr(gozip, "File")
        assert hasattr(gozip, "FileHeader")
        assert hasattr(gozip, "ReadCloser")
        assert hasattr(gozip, "Deflate")
        assert hasattr(gozip, "Store")
