#!/usr/bin/env python3
"""Hashing and cryptography examples using goated stdlib packages.

Demonstrates:
- Hash functions (MD5, SHA1, SHA256, SHA512)
- HMAC
- Random number generation
"""

from goated.std import crypto, hash, rand


def demo_md5():
    print("=== MD5 Hashing ===\n")

    data = b"Hello, World!"

    digest = hash.SumMD5(data).hex()
    print(f"Data: {data.decode()}")
    print(f"MD5:  {digest}")

    h = hash.NewMD5()
    h.Write(b"Hello, ")
    h.Write(b"World!")
    digest = h.Sum().hex()
    print(f"MD5 (streaming): {digest}")

    h.Reset()
    h.Write(b"Different data")
    print(f"MD5 (reset): {h.Sum().hex()}")
    print()


def demo_sha1():
    print("=== SHA1 Hashing ===\n")

    data = b"Hello, World!"

    digest = hash.SumSHA1(data).hex()
    print(f"Data: {data.decode()}")
    print(f"SHA1: {digest}")

    h = hash.NewSHA1()
    print(f"Block size: {h.BlockSize()} bytes")
    print(f"Hash size:  {h.Size()} bytes")
    print()


def demo_sha256():
    print("=== SHA256 Hashing ===\n")

    data = b"Hello, World!"

    digest = hash.SumSHA256(data).hex()
    print(f"Data: {data.decode()}")
    print(f"SHA256: {digest}")

    digest = hash.SumSHA224(data).hex()
    print(f"SHA224: {digest}")
    print()


def demo_sha512():
    print("=== SHA512 Hashing ===\n")

    data = b"Hello, World!"

    digest = hash.SumSHA512(data).hex()
    print(f"Data: {data.decode()}")
    print(f"SHA512: {digest[:64]}...")

    digest = hash.SumSHA384(data).hex()
    print(f"SHA384: {digest[:64]}...")
    print()


def demo_hash_comparison():
    print("=== Hash Comparison ===\n")

    data = b"The quick brown fox jumps over the lazy dog"
    print(f"Data: {data.decode()}\n")

    hashes = [
        ("MD5", hash.SumMD5(data).hex(), 32),
        ("SHA1", hash.SumSHA1(data).hex(), 40),
        ("SHA224", hash.SumSHA224(data).hex(), 56),
        ("SHA256", hash.SumSHA256(data).hex(), 64),
        ("SHA384", hash.SumSHA384(data).hex(), 96),
        ("SHA512", hash.SumSHA512(data).hex(), 128),
    ]

    print(f"{'Algorithm':<10} {'Length':<8} {'Digest'}")
    print("-" * 80)
    for name, digest, _expected_len in hashes:
        display = digest if len(digest) <= 64 else digest[:61] + "..."
        print(f"{name:<10} {len(digest):<8} {display}")
    print()


def demo_hmac():
    print("=== HMAC ===\n")

    key = b"secret-key"
    message = b"Hello, World!"

    hmac_digest = hash.HMAC(key, message, "sha256").hex()
    print(f"Key: {key.decode()}")
    print(f"Message: {message.decode()}")
    print(f"HMAC-SHA256: {hmac_digest}")

    hmac_digest = hash.HMAC(key, message, "sha1").hex()
    print(f"HMAC-SHA1: {hmac_digest}")

    hmac_digest = hash.HMAC(key, message, "md5").hex()
    print(f"HMAC-MD5: {hmac_digest}")
    print()


def demo_streaming_hash():
    print("=== Streaming Hash ===\n")

    h = hash.NewSHA256()

    chunks = [
        b"First chunk of data. ",
        b"Second chunk of data. ",
        b"Third chunk of data. ",
        b"Final chunk!",
    ]

    print("Hashing in chunks:")
    for i, chunk in enumerate(chunks, 1):
        h.Write(chunk)
        print(f"  After chunk {i}: {len(chunk)} bytes written")

    digest = h.Sum().hex()
    print(f"\nFinal SHA256: {digest}")

    all_data = b"".join(chunks)
    verify = hash.SumSHA256(all_data).hex()
    print(f"Verification: {digest == verify}")
    print()


def demo_crypto_random():
    print("=== Crypto Random ===\n")

    result = crypto.GenerateRandomBytes(16)
    if result.is_ok():
        random_bytes = result.unwrap()
        print(f"Random bytes (16): {random_bytes.hex()}")

    result = crypto.GenerateRandomBytes(32)
    if result.is_ok():
        random_bytes = result.unwrap()
        print(f"Random bytes (32): {random_bytes.hex()}")

    result = crypto.GenerateRandomString(20)
    if result.is_ok():
        random_string = result.unwrap()
        print(f"Random string (20): {random_string}")
    print()


def demo_rand_package():
    print("=== Random Numbers (math/rand) ===\n")

    rand.Seed(42)

    print("Random integers:")
    for _i in range(5):
        print(f"  Int(): {rand.Int()}")

    print("\nRandom in range [0, 100):")
    rand.Seed(42)
    for _i in range(5):
        print(f"  Intn(100): {rand.Intn(100)}")

    print("\nRandom floats [0.0, 1.0):")
    rand.Seed(42)
    for _i in range(5):
        print(f"  Float64(): {rand.Float64():.6f}")

    rand.Seed(42)
    perm = rand.Perm(10)
    print(f"\nPerm(10): {perm}")

    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    rand.Seed(42)
    rand.Shuffle(
        len(data), lambda i, j: data.__setitem__(i, data[j]) or data.__setitem__(j, data[i])
    )
    print(f"Shuffled: {data}")
    print()


def demo_rand_distributions():
    print("=== Random Distributions ===\n")

    rand.Seed(12345)

    print("Normal distribution (mean=0, stddev=1):")
    values = [rand.NormFloat64() for _ in range(10)]
    print(f"  {[f'{v:.3f}' for v in values]}")

    print("\nExponential distribution:")
    values = [rand.ExpFloat64() for _ in range(10)]
    print(f"  {[f'{v:.3f}' for v in values]}")

    print("\nUniform integers [0, 1000):")
    values = [rand.Intn(1000) for _ in range(10)]
    print(f"  {values}")
    print()


def demo_password_hashing():
    print("=== Password Hashing Pattern ===\n")

    password = "my_secure_password"

    salt_result = crypto.GenerateRandomBytes(16)
    if salt_result.is_ok():
        salt = salt_result.unwrap()

        salted = salt + password.encode()
        password_hash = hash.SumSHA256(salted).hex()

        print(f"Password: {password}")
        print(f"Salt: {salt.hex()}")
        print(f"Hash: {password_hash}")

        verify_salted = salt + password.encode()
        verify_hash = hash.SumSHA256(verify_salted).hex()
        print(f"\nVerification: {verify_hash == password_hash}")

        wrong_salted = salt + b"wrong_password"
        wrong_hash = hash.SumSHA256(wrong_salted).hex()
        print(f"Wrong password: {wrong_hash == password_hash}")
    print()


def demo_file_checksum():
    print("=== File Checksum Pattern ===\n")

    file_content = (
        b"""
    This is the content of a file.
    It could be much larger in practice.
    We compute a checksum to verify integrity.
    """
        * 100
    )

    md5_sum = hash.SumMD5(file_content).hex()
    sha256_sum = hash.SumSHA256(file_content).hex()

    print(f"File size: {len(file_content)} bytes")
    print(f"MD5: {md5_sum}")
    print(f"SHA256: {sha256_sum}")

    downloaded = file_content
    print(f"\nVerify MD5: {hash.SumMD5(downloaded).hex() == md5_sum}")
    print(f"Verify SHA256: {hash.SumSHA256(downloaded).hex() == sha256_sum}")

    tampered = file_content + b"x"
    print(f"\nTampered MD5 match: {hash.SumMD5(tampered).hex() == md5_sum}")
    print()


def main():
    print("=" * 60)
    print("  goated - Hashing and Cryptography Examples")
    print("=" * 60)
    print()

    demo_md5()
    demo_sha1()
    demo_sha256()
    demo_sha512()
    demo_hash_comparison()
    demo_hmac()
    demo_streaming_hash()
    demo_crypto_random()
    demo_rand_package()
    demo_rand_distributions()
    demo_password_hashing()
    demo_file_checksum()

    print("=" * 60)
    print("  Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
