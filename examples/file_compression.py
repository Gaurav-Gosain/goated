#!/usr/bin/env python3
"""File compression examples using goated.std.gzip and goated.std.zip.

Demonstrates:
- Gzip compression/decompression
- Creating and reading ZIP archives
- Working with file headers
"""

import os
import tempfile
from io import BytesIO

from goated.std import gzip
from goated.std import zip as gozip


def demo_gzip_basics():
    """Demonstrate basic gzip operations."""
    print("=== Gzip Basics ===\n")

    original = b"Hello, World! " * 100  # Some repetitive data
    print(f"Original size: {len(original)} bytes")

    # Compress data
    buf = BytesIO()
    writer = gzip.NewWriter(buf)
    writer.Write(original)
    writer.Close()

    compressed = buf.getvalue()
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Compression ratio: {len(compressed) / len(original):.2%}")

    # Decompress data
    buf = BytesIO(compressed)
    reader_result = gzip.NewReader(buf)
    if reader_result.is_ok():
        reader = reader_result.unwrap()
        decompressed = reader.Read().unwrap()
        reader.Close()
        print(f"Decompressed size: {len(decompressed)} bytes")
        print(f"Data matches: {decompressed == original}")
    print()


def demo_gzip_with_header():
    """Demonstrate gzip with custom header."""
    print("=== Gzip with Header ===\n")

    data = b"Important data with metadata"

    # Create gzip with header info
    buf = BytesIO()
    writer = gzip.NewWriter(buf)
    writer.Header.Name = "data.txt"
    writer.Header.Comment = "My important data file"
    writer.Write(data)
    writer.Close()

    # Read back and check header
    buf.seek(0)
    reader = gzip.NewReader(buf).unwrap()
    print(f"Name: {reader.Header.Name}")
    print(f"Comment: {reader.Header.Comment}")
    content = reader.Read().unwrap()
    print(f"Content: {content.decode()}")
    reader.Close()
    print()


def demo_gzip_levels():
    """Demonstrate different compression levels."""
    print("=== Gzip Compression Levels ===\n")

    data = b"The quick brown fox jumps over the lazy dog. " * 50
    print(f"Original size: {len(data)} bytes\n")

    levels = [
        (gzip.NoCompression, "NoCompression"),
        (gzip.BestSpeed, "BestSpeed"),
        (gzip.DefaultCompression, "DefaultCompression"),
        (gzip.BestCompression, "BestCompression"),
    ]

    for level, name in levels:
        buf = BytesIO()
        writer = gzip.NewWriterLevel(buf, level).unwrap()
        writer.Write(data)
        writer.Close()
        size = len(buf.getvalue())
        print(f"{name:20}: {size:4} bytes ({size / len(data):.1%})")
    print()


def demo_zip_create():
    """Demonstrate creating ZIP archives."""
    print("=== Creating ZIP Archives ===\n")

    buf = BytesIO()

    # Create a new ZIP writer
    w = gozip.NewWriter(buf)

    # Add files to the archive
    files = {
        "hello.txt": b"Hello, World!",
        "data/numbers.txt": b"1\n2\n3\n4\n5\n",
        "data/config.json": b'{"version": "1.0", "debug": true}',
    }

    for name, content in files.items():
        result = w.Create(name)
        if result.is_ok():
            f = result.unwrap()
            f.write(content)
            f.close()
            print(f"Added: {name} ({len(content)} bytes)")

    # Set archive comment
    w.SetComment("Created with goated.std.zip")
    w.Close()

    print(f"\nArchive size: {len(buf.getvalue())} bytes")
    print()


def demo_zip_create_header():
    """Demonstrate creating ZIP with custom file headers."""
    print("=== ZIP with Custom Headers ===\n")

    from datetime import datetime

    buf = BytesIO()
    w = gozip.NewWriter(buf)

    # Create a file with custom header
    header = gozip.FileHeader(
        Name="script.py",
        Comment="Python script file",
        Method=gozip.Deflate,
        Modified=datetime.now(),
    )
    header.SetMode(0o755)  # Executable

    result = w.CreateHeader(header)
    if result.is_ok():
        f = result.unwrap()
        f.write(b'#!/usr/bin/env python3\nprint("Hello!")\n')
        f.close()

    # Create a stored (uncompressed) file
    header2 = gozip.FileHeader(
        Name="readme.txt",
        Method=gozip.Store,  # No compression
    )

    result = w.CreateHeader(header2)
    if result.is_ok():
        f = result.unwrap()
        f.write(b"This file is stored without compression.")
        f.close()

    w.Close()

    print("Created archive with custom headers")
    print(f"Archive size: {len(buf.getvalue())} bytes")
    print()


def demo_zip_read():
    """Demonstrate reading ZIP archives."""
    print("=== Reading ZIP Archives ===\n")

    # First, create a ZIP archive
    buf = BytesIO()
    w = gozip.NewWriter(buf)

    w.Create("file1.txt").unwrap().write(b"Content of file 1")
    w.Create("file2.txt").unwrap().write(b"Content of file 2")
    w.Create("subdir/file3.txt").unwrap().write(b"Content of file 3")
    w.SetComment("Test archive")
    w.Close()

    # Now read it back
    buf.seek(0)
    result = gozip.NewReader(buf, len(buf.getvalue()))

    if result.is_ok():
        reader = result.unwrap()

        print(f"Archive comment: {reader.Comment}")
        print(f"Number of files: {len(reader.File)}\n")

        for f in reader.File:
            header = f.FileHeader
            info = header.FileInfo()

            print(f"File: {header.Name}")
            print(f"  Size: {info.Size()} bytes")
            print(f"  Is Directory: {info.IsDir()}")

            # Read content
            content_result = f.Read()
            if content_result.is_ok():
                content = content_result.unwrap()
                print(f"  Content: {content.decode()!r}")
            print()

        reader.Close()


def demo_zip_file_operations():
    """Demonstrate ZIP file operations."""
    print("=== ZIP File Operations ===\n")

    # Create temp file
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Create ZIP file on disk
        with open(tmp_path, "wb") as f:
            w = gozip.NewWriter(f)
            w.Create("document.txt").unwrap().write(b"Important document content")
            w.Create("image.dat").unwrap().write(bytes(range(256)))
            w.Close()

        print(f"Created: {tmp_path}")
        print(f"File size: {os.path.getsize(tmp_path)} bytes\n")

        # Open and read using OpenReader
        result = gozip.OpenReader(tmp_path)
        if result.is_ok():
            reader = result.unwrap()

            print("Files in archive:")
            for f in reader.File:
                print(f"  - {f.FileHeader.Name}")

            # Open specific file
            open_result = reader.Open("document.txt")
            if open_result.is_ok():
                file_handle = open_result.unwrap()
                content = file_handle.read()
                print(f"\ndocument.txt content: {content.decode()}")
                file_handle.close()

            reader.Close()
    finally:
        os.unlink(tmp_path)
    print()


def demo_roundtrip():
    """Demonstrate compression roundtrip."""
    print("=== Compression Roundtrip ===\n")

    # Original data
    original_files = {
        "README.md": b"# My Project\n\nThis is a test project.",
        "src/main.py": b'print("Hello, World!")',
        "src/utils.py": b"def add(a, b): return a + b",
        "data/config.yaml": b"name: test\nversion: 1.0",
    }

    # Create archive
    archive_buf = BytesIO()
    w = gozip.NewWriter(archive_buf)
    for name, content in original_files.items():
        f = w.Create(name).unwrap()
        f.write(content)
        f.close()
    w.Close()

    archive_data = archive_buf.getvalue()
    print(f"Archive created: {len(archive_data)} bytes")

    # Extract and verify
    archive_buf = BytesIO(archive_data)
    reader = gozip.NewReader(archive_buf, len(archive_data)).unwrap()

    extracted_files = {}
    for f in reader.File:
        content = f.Read().unwrap()
        extracted_files[f.FileHeader.Name] = content
    reader.Close()

    # Verify
    print("\nVerification:")
    all_match = True
    for name, original_content in original_files.items():
        extracted_content = extracted_files.get(name)
        matches = extracted_content == original_content
        status = "OK" if matches else "MISMATCH"
        print(f"  {name}: {status}")
        all_match = all_match and matches

    print(f"\nAll files match: {all_match}")
    print()


def main():
    print("=" * 60)
    print("  goated.std.gzip & goated.std.zip - Compression Examples")
    print("=" * 60)
    print()

    demo_gzip_basics()
    demo_gzip_with_header()
    demo_gzip_levels()
    demo_zip_create()
    demo_zip_create_header()
    demo_zip_read()
    demo_zip_file_operations()
    demo_roundtrip()

    print("=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
