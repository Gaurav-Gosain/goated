from goated.std import hash


class TestNew:
    def test_new_md5(self):
        h = hash.New("md5")
        assert h is not None
        assert h.Size() == 16
        assert h.BlockSize() == 64

    def test_new_sha1(self):
        h = hash.New("sha1")
        assert h is not None
        assert h.Size() == 20

    def test_new_sha256(self):
        h = hash.New("sha256")
        assert h is not None
        assert h.Size() == 32

    def test_new_sha512(self):
        h = hash.New("sha512")
        assert h is not None
        assert h.Size() == 64


class TestNewMD5:
    def test_new_md5(self):
        h = hash.NewMD5()
        assert h.Size() == 16

    def test_md5_write(self):
        h = hash.NewMD5()
        n, err = h.Write(b"hello")
        assert n == 5
        assert err is None

    def test_md5_sum(self):
        h = hash.NewMD5()
        h.Write(b"hello")
        digest = h.Sum(None)
        assert len(digest) == 16


class TestNewSHA1:
    def test_new_sha1(self):
        h = hash.NewSHA1()
        assert h.Size() == 20

    def test_sha1_sum(self):
        h = hash.NewSHA1()
        h.Write(b"hello")
        digest = h.Sum(None)
        assert len(digest) == 20


class TestNewSHA256:
    def test_new_sha256(self):
        h = hash.NewSHA256()
        assert h.Size() == 32

    def test_sha256_sum(self):
        h = hash.NewSHA256()
        h.Write(b"hello")
        digest = h.Sum(None)
        assert len(digest) == 32


class TestNewSHA512:
    def test_new_sha512(self):
        h = hash.NewSHA512()
        assert h.Size() == 64


class TestNewSHA224:
    def test_new_sha224(self):
        h = hash.NewSHA224()
        assert h.Size() == 28


class TestNewSHA384:
    def test_new_sha384(self):
        h = hash.NewSHA384()
        assert h.Size() == 48


class TestHashWrite:
    def test_write_multiple(self):
        h = hash.NewSHA256()
        h.Write(b"hello ")
        h.Write(b"world")
        digest1 = h.Sum(None)

        h2 = hash.NewSHA256()
        h2.Write(b"hello world")
        digest2 = h2.Sum(None)

        assert digest1 == digest2


class TestHashReset:
    def test_reset(self):
        h = hash.NewSHA256()
        h.Write(b"some data")
        h.Reset()
        h.Write(b"hello")
        digest1 = h.Sum(None)

        h2 = hash.NewSHA256()
        h2.Write(b"hello")
        digest2 = h2.Sum(None)

        assert digest1 == digest2


class TestHashSum:
    def test_sum_with_prefix(self):
        h = hash.NewSHA256()
        h.Write(b"hello")
        digest = h.Sum(b"prefix:")

        assert digest.startswith(b"prefix:")
        assert len(digest) == 7 + 32

    def test_sum_without_prefix(self):
        h = hash.NewSHA256()
        h.Write(b"hello")
        digest = h.Sum(None)

        assert len(digest) == 32


class TestSumFunctions:
    def test_sum_md5(self):
        digest = hash.SumMD5(b"hello")
        assert len(digest) == 16

    def test_sum_sha1(self):
        digest = hash.SumSHA1(b"hello")
        assert len(digest) == 20

    def test_sum_sha256(self):
        digest = hash.SumSHA256(b"hello")
        assert len(digest) == 32

    def test_sum_sha512(self):
        digest = hash.SumSHA512(b"hello")
        assert len(digest) == 64


class TestSum:
    def test_sum_algorithm(self):
        digest = hash.Sum(b"hello", "sha256")
        assert len(digest) == 32

    def test_sum_md5(self):
        digest = hash.Sum(b"hello", "md5")
        assert len(digest) == 16


class TestNewHMAC:
    def test_new_hmac(self):
        h = hash.NewHMAC(b"secret", "sha256")
        assert h is not None

    def test_hmac_write(self):
        h = hash.NewHMAC(b"secret", "sha256")
        n, err = h.Write(b"message")
        assert n == 7
        assert err is None

    def test_hmac_sum(self):
        h = hash.NewHMAC(b"secret", "sha256")
        h.Write(b"message")
        digest = h.Sum(None)
        assert len(digest) == 32

    def test_hmac_reset(self):
        h = hash.NewHMAC(b"secret", "sha256")
        h.Write(b"message1")
        h.Reset()
        h.Write(b"message2")
        digest1 = h.Sum(None)

        h2 = hash.NewHMAC(b"secret", "sha256")
        h2.Write(b"message2")
        digest2 = h2.Sum(None)

        assert digest1 == digest2

    def test_hmac_different_keys(self):
        h1 = hash.NewHMAC(b"key1", "sha256")
        h1.Write(b"message")
        digest1 = h1.Sum(None)

        h2 = hash.NewHMAC(b"key2", "sha256")
        h2.Write(b"message")
        digest2 = h2.Sum(None)

        assert digest1 != digest2


class TestKnownValues:
    def test_md5_known(self):
        digest = hash.SumMD5(b"hello")
        expected = bytes.fromhex("5d41402abc4b2a76b9719d911017c592")
        assert digest == expected

    def test_sha256_known(self):
        digest = hash.SumSHA256(b"hello")
        expected = bytes.fromhex("2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")
        assert digest == expected
