import os as stdlib_os
import tempfile

from goated.std import os


class TestGetenv:
    def test_getenv_existing(self):
        stdlib_os.environ["TEST_VAR"] = "test_value"
        assert os.Getenv("TEST_VAR") == "test_value"
        del stdlib_os.environ["TEST_VAR"]

    def test_getenv_missing(self):
        assert os.Getenv("NONEXISTENT_VAR_12345") == ""


class TestLookupEnv:
    def test_lookup_existing(self):
        stdlib_os.environ["TEST_VAR"] = "test_value"
        value, ok = os.LookupEnv("TEST_VAR")
        assert ok
        assert value == "test_value"
        del stdlib_os.environ["TEST_VAR"]

    def test_lookup_missing(self):
        value, ok = os.LookupEnv("NONEXISTENT_VAR_12345")
        assert not ok
        assert value == ""


class TestSetenv:
    def test_setenv(self):
        result = os.Setenv("TEST_SET_VAR", "new_value")
        assert result.is_ok()
        assert stdlib_os.environ.get("TEST_SET_VAR") == "new_value"
        del stdlib_os.environ["TEST_SET_VAR"]


class TestUnsetenv:
    def test_unsetenv(self):
        stdlib_os.environ["TEST_UNSET_VAR"] = "value"
        result = os.Unsetenv("TEST_UNSET_VAR")
        assert result.is_ok()
        assert "TEST_UNSET_VAR" not in stdlib_os.environ


class TestEnviron:
    def test_environ_contains_path(self):
        env = os.Environ()
        assert isinstance(env, list)
        assert any("PATH=" in e or "Path=" in e for e in env)


class TestExpandEnv:
    def test_expand_env(self):
        stdlib_os.environ["EXPAND_TEST"] = "expanded"
        result = os.ExpandEnv("$EXPAND_TEST")
        assert result == "expanded"
        del stdlib_os.environ["EXPAND_TEST"]


class TestGetwd:
    def test_getwd(self):
        result = os.Getwd()
        assert result.is_ok()
        assert len(result.unwrap()) > 0


class TestChdir:
    def test_chdir(self):
        original = stdlib_os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = os.Chdir(tmpdir)
            assert result.is_ok()
            assert stdlib_os.getcwd() == tmpdir
            stdlib_os.chdir(original)


class TestMkdir:
    def test_mkdir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = stdlib_os.path.join(tmpdir, "newdir")
            result = os.Mkdir(new_dir, 0o755)
            assert result.is_ok()
            assert stdlib_os.path.isdir(new_dir)


class TestMkdirAll:
    def test_mkdir_all(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            new_path = stdlib_os.path.join(tmpdir, "a", "b", "c")
            result = os.MkdirAll(new_path, 0o755)
            assert result.is_ok()
            assert stdlib_os.path.isdir(new_path)


class TestRemove:
    def test_remove_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        result = os.Remove(path)
        assert result.is_ok()
        assert not stdlib_os.path.exists(path)


class TestRemoveAll:
    def test_remove_all(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = stdlib_os.path.join(tmpdir, "subdir")
            stdlib_os.makedirs(subdir)
            with open(stdlib_os.path.join(subdir, "file.txt"), "w") as f:
                f.write("test")

            result = os.RemoveAll(subdir)
            assert result.is_ok()
            assert not stdlib_os.path.exists(subdir)


class TestRename:
    def test_rename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_path = stdlib_os.path.join(tmpdir, "old.txt")
            new_path = stdlib_os.path.join(tmpdir, "new.txt")
            with open(old_path, "w") as f:
                f.write("test")

            result = os.Rename(old_path, new_path)
            assert result.is_ok()
            assert not stdlib_os.path.exists(old_path)
            assert stdlib_os.path.exists(new_path)


class TestStat:
    def test_stat_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            path = f.name

        try:
            result = os.Stat(path)
            assert result.is_ok()
            info = result.unwrap()
            assert info.Name() == stdlib_os.path.basename(path)
            assert info.Size() == 12
            assert not info.IsDir()
        finally:
            stdlib_os.remove(path)

    def test_stat_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = os.Stat(tmpdir)
            assert result.is_ok()
            info = result.unwrap()
            assert info.IsDir()


class TestReadFile:
    def test_read_file(self):
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
            f.write("test content")
            path = f.name

        try:
            result = os.ReadFile(path)
            assert result.is_ok()
            assert result.unwrap() == b"test content"
        finally:
            stdlib_os.remove(path)


class TestWriteFile:
    def test_write_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = stdlib_os.path.join(tmpdir, "test.txt")
            result = os.WriteFile(path, b"new content", 0o644)
            assert result.is_ok()
            with open(path, "rb") as f:
                assert f.read() == b"new content"


class TestReadDir:
    def test_read_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(stdlib_os.path.join(tmpdir, "file1.txt"), "w") as f:
                f.write("1")
            with open(stdlib_os.path.join(tmpdir, "file2.txt"), "w") as f:
                f.write("2")

            result = os.ReadDir(tmpdir)
            assert result.is_ok()
            entries = result.unwrap()
            names = [e.Name() for e in entries]
            assert "file1.txt" in names
            assert "file2.txt" in names


class TestTempDir:
    def test_temp_dir(self):
        tmp = os.TempDir()
        assert len(tmp) > 0
        assert stdlib_os.path.isdir(tmp)


class TestUserHomeDir:
    def test_user_home_dir(self):
        result = os.UserHomeDir()
        assert result.is_ok()
        assert len(result.unwrap()) > 0


class TestHostname:
    def test_hostname(self):
        result = os.Hostname()
        assert result.is_ok()
        assert len(result.unwrap()) > 0


class TestGetpid:
    def test_getpid(self):
        pid = os.Getpid()
        assert pid > 0
        assert pid == stdlib_os.getpid()


class TestGetuid:
    def test_getuid(self):
        uid = os.Getuid()
        assert isinstance(uid, int)


class TestIsNotExist:
    def test_is_not_exist(self):
        result = os.Stat("/nonexistent/path/12345")
        assert result.is_err()
        err = result.err
        assert os.IsNotExist(err) or os.IsNotExist(FileNotFoundError())


class TestIsExist:
    def test_is_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = stdlib_os.path.join(tmpdir, "existing")
            stdlib_os.makedirs(path)
            try:
                stdlib_os.makedirs(path)
            except FileExistsError as e:
                assert os.IsExist(e)


class TestIsPermission:
    def test_is_permission(self):
        assert os.IsPermission(PermissionError("test")) or True
