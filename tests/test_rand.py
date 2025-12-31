import pytest

from goated.std import rand


class TestSeed:
    def test_seed_reproducible(self):
        rand.Seed(42)
        first = rand.Int()

        rand.Seed(42)
        second = rand.Int()

        assert first == second


class TestInt:
    def test_int_non_negative(self):
        for _ in range(100):
            assert rand.Int() >= 0


class TestIntn:
    def test_intn_range(self):
        for _ in range(100):
            n = rand.Intn(10)
            assert 0 <= n < 10

    def test_intn_one(self):
        assert rand.Intn(1) == 0

    def test_intn_invalid(self):
        with pytest.raises(ValueError):
            rand.Intn(0)

        with pytest.raises(ValueError):
            rand.Intn(-1)


class TestInt31:
    def test_int31_range(self):
        for _ in range(100):
            n = rand.Int31()
            assert 0 <= n < (1 << 31)


class TestInt31n:
    def test_int31n_range(self):
        for _ in range(100):
            n = rand.Int31n(100)
            assert 0 <= n < 100


class TestInt63:
    def test_int63_range(self):
        for _ in range(100):
            n = rand.Int63()
            assert 0 <= n < (1 << 63)


class TestInt63n:
    def test_int63n_range(self):
        for _ in range(100):
            n = rand.Int63n(1000)
            assert 0 <= n < 1000


class TestUint32:
    def test_uint32_range(self):
        for _ in range(100):
            n = rand.Uint32()
            assert 0 <= n < (1 << 32)


class TestUint64:
    def test_uint64_range(self):
        for _ in range(100):
            n = rand.Uint64()
            assert 0 <= n < (1 << 64)


class TestFloat32:
    def test_float32_range(self):
        for _ in range(100):
            f = rand.Float32()
            assert 0.0 <= f < 1.0


class TestFloat64:
    def test_float64_range(self):
        for _ in range(100):
            f = rand.Float64()
            assert 0.0 <= f < 1.0


class TestNormFloat64:
    def test_norm_float64_exists(self):
        values = [rand.NormFloat64() for _ in range(1000)]
        mean = sum(values) / len(values)
        assert -1 < mean < 1


class TestExpFloat64:
    def test_exp_float64_positive(self):
        for _ in range(100):
            f = rand.ExpFloat64()
            assert f > 0


class TestPerm:
    def test_perm_length(self):
        p = rand.Perm(10)
        assert len(p) == 10

    def test_perm_contains_all(self):
        p = rand.Perm(10)
        assert sorted(p) == list(range(10))

    def test_perm_zero(self):
        p = rand.Perm(0)
        assert p == []


class TestShuffle:
    def test_shuffle(self):
        data = list(range(10))
        original = data.copy()

        def swap(i, j):
            data[i], data[j] = data[j], data[i]

        rand.Shuffle(len(data), swap)

        assert sorted(data) == original


class TestRead:
    def test_read_length(self):
        buf = bytearray(16)
        n, err = rand.Read(buf)
        assert n == 16
        assert err is None

    def test_read_random(self):
        buf = bytearray(16)
        rand.Read(buf)
        assert any(b != 0 for b in buf)


class TestSource:
    def test_new_source(self):
        src = rand.NewSource(42)
        assert src is not None

    def test_source_int63(self):
        src = rand.NewSource(42)
        n = src.Int63()
        assert 0 <= n < (1 << 63)

    def test_source_seed(self):
        src = rand.NewSource(42)
        first = src.Int63()

        src.Seed(42)
        second = src.Int63()

        assert first == second


class TestRand:
    def test_new_rand(self):
        src = rand.NewSource(42)
        r = rand.New(src)
        assert r is not None

    def test_rand_methods(self):
        src = rand.NewSource(42)
        r = rand.New(src)

        assert r.Int() >= 0
        assert 0 <= r.Intn(10) < 10
        assert 0 <= r.Int31() < (1 << 31)
        assert 0 <= r.Int63() < (1 << 63)
        assert 0 <= r.Uint32() < (1 << 32)
        assert 0 <= r.Uint64() < (1 << 64)
        assert 0.0 <= r.Float32() < 1.0
        assert 0.0 <= r.Float64() < 1.0

    def test_rand_perm(self):
        src = rand.NewSource(42)
        r = rand.New(src)
        p = r.Perm(10)
        assert sorted(p) == list(range(10))

    def test_rand_read(self):
        src = rand.NewSource(42)
        r = rand.New(src)
        buf = bytearray(16)
        n, err = r.Read(buf)
        assert n == 16
        assert err is None

    def test_rand_reproducible(self):
        src1 = rand.NewSource(42)
        r1 = rand.New(src1)

        src2 = rand.NewSource(42)
        r2 = rand.New(src2)

        for _ in range(10):
            assert r1.Int() == r2.Int()
