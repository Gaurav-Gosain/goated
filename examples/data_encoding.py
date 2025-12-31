#!/usr/bin/env python3
"""Data encoding examples using goated stdlib packages.

Demonstrates:
- JSON encoding/decoding
- CSV reading/writing
- XML marshaling/unmarshaling
- Binary encoding (big/little endian, varints)
- Base64 and Hex encoding
"""

from io import BytesIO, StringIO

from goated.std import base64, binary, csv, hex, json, xml


def demo_json():
    """Demonstrate JSON encoding/decoding."""
    print("=== JSON Encoding ===\n")

    # Marshal (encode)
    data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "tags": ["developer", "python", "go"],
        "active": True,
    }

    result = json.Marshal(data)
    if result.is_ok():
        encoded = result.unwrap()
        print(f"Marshal: {encoded}")

    # Marshal with indent
    result = json.MarshalIndent(data, "", "  ")
    if result.is_ok():
        encoded = result.unwrap()
        print(f"\nMarshalIndent:\n{encoded}")

    # Unmarshal (decode)
    json_str = b'{"message": "Hello", "count": 42}'
    result = json.Unmarshal(json_str)
    if result.is_ok():
        decoded = result.unwrap()
        print(f"\nUnmarshal: {decoded}")

    # Validation
    valid = b'{"valid": true}'
    invalid = b"{invalid json}"
    print("\nValid JSON check:")
    print(f"  '{valid.decode()}': {json.Valid(valid)}")
    print(f"  '{invalid.decode()}': {json.Valid(invalid)}")
    print()


def demo_csv():
    """Demonstrate CSV reading/writing."""
    print("=== CSV Encoding ===\n")

    # Write CSV
    buf = StringIO()
    writer = csv.NewWriter(buf)

    records = [
        ["Name", "Age", "City"],
        ["Alice", "30", "New York"],
        ["Bob", "25", "Los Angeles"],
        ["Charlie", "35", "Chicago"],
    ]

    for record in records:
        writer.Write(record)
    writer.Flush()

    csv_data = buf.getvalue()
    print(f"Written CSV:\n{csv_data}")

    # Read CSV
    reader = csv.NewReader(StringIO(csv_data))

    print("Read records:")
    while True:
        result = reader.Read()
        if result.is_err():
            err = result.err()
            assert err is not None
            if err.go_type == "io.EOF":
                break
            print(f"Error: {err}")
            break
        record = result.unwrap()
        print(f"  {record}")

    # Read all at once
    reader = csv.NewReader(StringIO(csv_data))
    result = reader.ReadAll()
    if result.is_ok():
        all_records = result.unwrap()
        print(f"\nReadAll: {len(all_records)} records")
    print()


def demo_xml():
    """Demonstrate XML marshaling/unmarshaling."""
    print("=== XML Encoding ===\n")

    # Marshal
    data = {
        "person": {
            "name": "John",
            "age": 30,
            "email": "john@example.com",
        }
    }

    result = xml.Marshal(data)
    if result.is_ok():
        encoded = result.unwrap()
        print(f"Marshal: {encoded}")

    # Marshal with indent
    result = xml.MarshalIndent(data, "", "  ")
    if result.is_ok():
        encoded = result.unwrap()
        print(f"\nMarshalIndent:\n{encoded}")

    # Unmarshal
    xml_data = b"<root><message>Hello, XML!</message><count>42</count></root>"
    result = xml.Unmarshal(xml_data)
    if result.is_ok():
        decoded = result.unwrap()
        print(f"\nUnmarshal: {decoded}")

    # Escape special characters
    text = "Tom & Jerry <friends>"
    escaped = xml.Escape(text)
    print(f"\nEscape '{text}': {escaped}")
    print()


def demo_binary_byte_order():
    """Demonstrate binary encoding with byte order."""
    print("=== Binary Encoding - Byte Order ===\n")

    print("Big Endian (network byte order):")

    # Uint16
    buf = bytearray(2)
    binary.BigEndian.PutUint16(buf, 0x0102)
    print(f"  PutUint16(0x0102): {list(buf)}")

    value = binary.BigEndian.Uint16(bytes([0x01, 0x02]))
    print(f"  Uint16([0x01, 0x02]): 0x{value:04x} ({value})")

    # Uint32
    buf = bytearray(4)
    binary.BigEndian.PutUint32(buf, 0x01020304)
    print(f"  PutUint32(0x01020304): {list(buf)}")

    # Uint64
    buf = bytearray(8)
    binary.BigEndian.PutUint64(buf, 0x0102030405060708)
    print(f"  PutUint64(0x0102030405060708): {list(buf)}")

    print("\nLittle Endian:")

    # Uint16
    buf = bytearray(2)
    binary.LittleEndian.PutUint16(buf, 0x0102)
    print(f"  PutUint16(0x0102): {list(buf)}")

    value = binary.LittleEndian.Uint16(bytes([0x02, 0x01]))
    print(f"  Uint16([0x02, 0x01]): 0x{value:04x} ({value})")

    # Append operations
    data = b"prefix"
    data = binary.BigEndian.AppendUint16(data, 0x1234)
    print(f"\nAppendUint16 to 'prefix': {list(data)}")
    print()


def demo_binary_varints():
    """Demonstrate variable-length integer encoding."""
    print("=== Binary Encoding - Varints ===\n")

    print("Unsigned varints (Uvarint):")
    test_values = [0, 1, 127, 128, 255, 256, 16383, 16384, 2**20]

    for val in test_values:
        buf = bytearray(10)
        n = binary.PutUvarint(buf, val)
        decoded, m = binary.Uvarint(bytes(buf[:n]))
        print(f"  {val:>10}: {n} bytes -> {list(buf[:n])} -> {decoded}")

    print("\nSigned varints (Varint):")
    test_values = [0, 1, -1, 63, -64, 64, -65, 1000, -1000]

    for val in test_values:
        buf = bytearray(10)
        n = binary.PutVarint(buf, val)
        decoded, m = binary.Varint(bytes(buf[:n]))
        print(f"  {val:>6}: {n} bytes -> {list(buf[:n])} -> {decoded}")
    print()


def demo_binary_read_write():
    """Demonstrate binary Read/Write functions."""
    print("=== Binary Read/Write ===\n")

    # Write various types
    buf = BytesIO()

    binary.Write(buf, binary.BigEndian, b"HDR")  # Header
    binary.Write(buf, binary.BigEndian, 0x0102)  # Uint16
    binary.Write(buf, binary.BigEndian, 3.14159)  # Float64

    data = buf.getvalue()
    print(f"Written data: {list(data)} ({len(data)} bytes)")

    # Size calculation
    print("\nSize calculations:")
    print(f"  Size(b'hello'): {binary.Size(b'hello')}")
    print(f"  Size(42): {binary.Size(42)}")
    print(f"  Size(0x0102): {binary.Size(0x0102)}")
    print(f"  Size(3.14): {binary.Size(3.14)}")
    print(f"  Size([1, 2, 3]): {binary.Size([1, 2, 3])}")
    print()


def demo_base64_encoding():
    """Demonstrate Base64 encoding."""
    print("=== Base64 Encoding ===\n")

    data = b"Hello, World! This is a test."

    # Standard encoding
    encoded = base64.StdEncoding.EncodeToString(data)
    print(f"Original: {data}")
    print(f"StdEncoding: {encoded}")

    decoded, _ = base64.StdEncoding.DecodeString(encoded)
    print(f"Decoded: {decoded}")

    # URL-safe encoding
    url_encoded = base64.URLEncoding.EncodeToString(data)
    print(f"\nURLEncoding: {url_encoded}")

    # Raw (no padding) encoding
    raw_encoded = base64.RawStdEncoding.EncodeToString(data)
    print(f"RawStdEncoding (no padding): {raw_encoded}")

    raw_url_encoded = base64.RawURLEncoding.EncodeToString(data)
    print(f"RawURLEncoding: {raw_url_encoded}")
    print()


def demo_hex_encoding():
    """Demonstrate hexadecimal encoding."""
    print("=== Hex Encoding ===\n")

    data = b"Hello, Hex!"

    # Encode
    encoded = hex.EncodeToString(data)
    print(f"Original: {data}")
    print(f"Hex encoded: {encoded}")

    # Decode
    decoded, _ = hex.DecodeString(encoded)
    print(f"Decoded: {decoded}")

    # Length calculation
    print(f"\nEncodedLen(10): {hex.EncodedLen(10)}")
    print(f"DecodedLen(20): {hex.DecodedLen(20)}")

    # Hex dump
    print("\nHex dump of 'Hello, World!':")
    print(hex.Dump(b"Hello, World!"))

    # Longer dump
    print("Hex dump of longer data:")
    long_data = bytes(range(64))
    print(hex.Dump(long_data))


def demo_encoding_roundtrip():
    """Demonstrate encoding roundtrips."""
    print("=== Encoding Roundtrips ===\n")

    original = {"message": "Test data", "values": [1, 2, 3]}

    # JSON roundtrip
    json_str = json.Marshal(original).unwrap()
    json_decoded = json.Unmarshal(json_str.encode()).unwrap()
    print(f"JSON roundtrip: {original == json_decoded}")

    # Base64 roundtrip
    b64_str = base64.StdEncoding.EncodeToString(b"secret data")
    b64_decoded, _ = base64.StdEncoding.DecodeString(b64_str)
    print(f"Base64 roundtrip: {b64_decoded == b'secret data'}")

    # Hex roundtrip
    hex_str = hex.EncodeToString(b"hex data")
    hex_decoded, _ = hex.DecodeString(hex_str)
    print(f"Hex roundtrip: {hex_decoded == b'hex data'}")

    # Binary varint roundtrip
    buf = bytearray(10)
    binary.PutVarint(buf, -12345)
    val, _ = binary.Varint(bytes(buf))
    print(f"Varint roundtrip: {val == -12345}")
    print()


def main():
    print("=" * 60)
    print("  goated - Data Encoding Examples")
    print("=" * 60)
    print()

    demo_json()
    demo_csv()
    demo_xml()
    demo_binary_byte_order()
    demo_binary_varints()
    demo_binary_read_write()
    demo_base64_encoding()
    demo_hex_encoding()
    demo_encoding_roundtrip()

    print("=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
