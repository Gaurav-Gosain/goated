"""Tests for Go path/filepath package bindings."""

from goated.std import filepath


class TestAbs:
    def test_abs_relative(self):
        result = filepath.Abs(".")
        assert result.is_ok()
        abs_path = result.unwrap()
        assert abs_path.startswith("/")
        assert len(abs_path) > 1

    def test_abs_already_absolute(self):
        result = filepath.Abs("/tmp")
        assert result.is_ok()
        assert result.unwrap() == "/tmp"

    def test_abs_with_dotdot(self):
        result = filepath.Abs("/a/b/../c")
        assert result.is_ok()
        assert result.unwrap() == "/a/c"


class TestBase:
    def test_base_simple(self):
        assert filepath.Base("/a/b/c") == "c"

    def test_base_with_extension(self):
        assert filepath.Base("/home/user/file.txt") == "file.txt"

    def test_base_trailing_slash(self):
        assert filepath.Base("/a/b/c/") == "c"

    def test_base_single_element(self):
        assert filepath.Base("file.txt") == "file.txt"

    def test_base_root(self):
        assert filepath.Base("/") == "/"

    def test_base_empty(self):
        assert filepath.Base("") == "."


class TestClean:
    def test_clean_double_slash(self):
        assert filepath.Clean("a//b") == "a/b"

    def test_clean_dot(self):
        assert filepath.Clean("a/./b") == "a/b"

    def test_clean_dotdot(self):
        assert filepath.Clean("a/b/../c") == "a/c"

    def test_clean_complex(self):
        assert filepath.Clean("/a/b/c/./../../g") == "/a/g"

    def test_clean_empty(self):
        assert filepath.Clean("") == "."

    def test_clean_already_clean(self):
        assert filepath.Clean("/a/b/c") == "/a/b/c"


class TestDir:
    def test_dir_simple(self):
        assert filepath.Dir("/a/b/c") == "/a/b"

    def test_dir_file(self):
        assert filepath.Dir("/home/user/file.txt") == "/home/user"

    def test_dir_single_file(self):
        assert filepath.Dir("file.txt") == "."

    def test_dir_root(self):
        assert filepath.Dir("/") == "/"

    def test_dir_empty(self):
        assert filepath.Dir("") == "."


class TestEvalSymlinks:
    def test_evalsymlinks_regular_path(self):
        result = filepath.EvalSymlinks("/tmp")
        assert result.is_ok()

    def test_evalsymlinks_nonexistent(self):
        result = filepath.EvalSymlinks("/nonexistent/path/12345")
        assert result.is_err()


class TestExt:
    def test_ext_simple(self):
        assert filepath.Ext("file.txt") == ".txt"

    def test_ext_multiple_dots(self):
        assert filepath.Ext("archive.tar.gz") == ".gz"

    def test_ext_no_extension(self):
        assert filepath.Ext("README") == ""

    def test_ext_hidden_file(self):
        # Go considers everything after first dot as extension
        assert filepath.Ext(".gitignore") == ".gitignore"

    def test_ext_path_with_extension(self):
        assert filepath.Ext("/home/user/document.pdf") == ".pdf"


class TestFromSlash:
    def test_fromslash_simple(self):
        result = filepath.FromSlash("a/b/c")
        assert result == "a/b/c"  # On Unix, slash is the separator

    def test_fromslash_multiple(self):
        result = filepath.FromSlash("a//b")
        assert result == "a//b"

    def test_fromslash_empty(self):
        assert filepath.FromSlash("") == ""


class TestHasPrefix:
    def test_hasprefix_true(self):
        assert filepath.HasPrefix("/home/user/file", "/home") is True

    def test_hasprefix_false(self):
        assert filepath.HasPrefix("/home/user/file", "/var") is False

    def test_hasprefix_exact(self):
        assert filepath.HasPrefix("/home", "/home") is True

    def test_hasprefix_empty(self):
        assert filepath.HasPrefix("/home", "") is True


class TestIsAbs:
    def test_isabs_absolute(self):
        assert filepath.IsAbs("/home/user") is True

    def test_isabs_relative(self):
        assert filepath.IsAbs("home/user") is False

    def test_isabs_dot(self):
        assert filepath.IsAbs("./file") is False

    def test_isabs_root(self):
        assert filepath.IsAbs("/") is True

    def test_isabs_empty(self):
        assert filepath.IsAbs("") is False


class TestIsLocal:
    def test_islocal_simple(self):
        assert filepath.IsLocal("a/b/c") is True

    def test_islocal_absolute(self):
        assert filepath.IsLocal("/a/b/c") is False

    def test_islocal_dotdot(self):
        assert filepath.IsLocal("../a") is False

    def test_islocal_empty(self):
        assert filepath.IsLocal("") is False

    def test_islocal_dot(self):
        # "." is considered local in Go
        assert filepath.IsLocal(".") is True


class TestLocalize:
    def test_localize_simple(self):
        result = filepath.Localize("a/b/c")
        assert result.is_ok()
        assert result.unwrap() == "a/b/c"

    def test_localize_invalid(self):
        # Empty or invalid paths should error
        result = filepath.Localize("")
        assert result.is_err()


class TestMatch:
    def test_match_star(self):
        result = filepath.Match("*.txt", "file.txt")
        assert result.is_ok()
        assert result.unwrap() is True

    def test_match_star_no_match(self):
        result = filepath.Match("*.txt", "file.pdf")
        assert result.is_ok()
        assert result.unwrap() is False

    def test_match_question(self):
        result = filepath.Match("file?.txt", "file1.txt")
        assert result.is_ok()
        assert result.unwrap() is True

    def test_match_bracket(self):
        result = filepath.Match("file[0-9].txt", "file5.txt")
        assert result.is_ok()
        assert result.unwrap() is True

    def test_match_bad_pattern(self):
        result = filepath.Match("[", "file")
        assert result.is_err()


class TestRel:
    def test_rel_simple(self):
        result = filepath.Rel("/a/b", "/a/b/c/d")
        assert result.is_ok()
        assert result.unwrap() == "c/d"

    def test_rel_same(self):
        result = filepath.Rel("/a/b", "/a/b")
        assert result.is_ok()
        assert result.unwrap() == "."

    def test_rel_parent(self):
        result = filepath.Rel("/a/b/c", "/a/b")
        assert result.is_ok()
        assert result.unwrap() == ".."

    def test_rel_sibling(self):
        result = filepath.Rel("/a/b", "/a/c")
        assert result.is_ok()
        assert result.unwrap() == "../c"


class TestToSlash:
    def test_toslash_simple(self):
        assert filepath.ToSlash("a/b/c") == "a/b/c"

    def test_toslash_empty(self):
        assert filepath.ToSlash("") == ""


class TestVolumeName:
    def test_volumename_unix(self):
        # On Unix, volume name is always empty
        assert filepath.VolumeName("/home/user") == ""

    def test_volumename_empty(self):
        assert filepath.VolumeName("") == ""
