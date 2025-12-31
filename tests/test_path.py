"""Tests for Go path package bindings."""

from goated.std import path


class TestBase:
    def test_base_simple(self):
        assert path.Base("/a/b/c") == "c"

    def test_base_with_extension(self):
        assert path.Base("/home/user/file.txt") == "file.txt"

    def test_base_trailing_slash(self):
        assert path.Base("/a/b/c/") == "c"

    def test_base_single_element(self):
        assert path.Base("file.txt") == "file.txt"

    def test_base_root(self):
        assert path.Base("/") == "/"

    def test_base_empty(self):
        assert path.Base("") == "."

    def test_base_all_slashes(self):
        assert path.Base("///") == "/"


class TestClean:
    def test_clean_double_slash(self):
        assert path.Clean("a//b") == "a/b"

    def test_clean_dot(self):
        assert path.Clean("a/./b") == "a/b"

    def test_clean_dotdot(self):
        assert path.Clean("a/b/../c") == "a/c"

    def test_clean_rooted_dotdot(self):
        assert path.Clean("/../a") == "/a"

    def test_clean_complex(self):
        assert path.Clean("/a/b/c/./../../g") == "/a/g"

    def test_clean_empty(self):
        assert path.Clean("") == "."

    def test_clean_already_clean(self):
        assert path.Clean("/a/b/c") == "/a/b/c"

    def test_clean_trailing_slash(self):
        assert path.Clean("/a/b/c/") == "/a/b/c"

    def test_clean_root(self):
        assert path.Clean("/") == "/"


class TestDir:
    def test_dir_simple(self):
        assert path.Dir("/a/b/c") == "/a/b"

    def test_dir_file(self):
        assert path.Dir("/home/user/file.txt") == "/home/user"

    def test_dir_single_file(self):
        assert path.Dir("file.txt") == "."

    def test_dir_root(self):
        assert path.Dir("/") == "/"

    def test_dir_empty(self):
        assert path.Dir("") == "."

    def test_dir_trailing_slash(self):
        # Go's path.Dir includes the last element when there's a trailing slash
        assert path.Dir("/a/b/c/") == "/a/b/c"


class TestExt:
    def test_ext_simple(self):
        assert path.Ext("file.txt") == ".txt"

    def test_ext_multiple_dots(self):
        assert path.Ext("archive.tar.gz") == ".gz"

    def test_ext_no_extension(self):
        assert path.Ext("README") == ""

    def test_ext_hidden_file(self):
        # Go considers everything after first dot as extension, including ".gitignore"
        assert path.Ext(".gitignore") == ".gitignore"

    def test_ext_path_with_extension(self):
        assert path.Ext("/home/user/document.pdf") == ".pdf"

    def test_ext_empty(self):
        assert path.Ext("") == ""

    def test_ext_dot_only(self):
        assert path.Ext("file.") == "."


class TestIsAbs:
    def test_isabs_absolute(self):
        assert path.IsAbs("/home/user") is True

    def test_isabs_relative(self):
        assert path.IsAbs("home/user") is False

    def test_isabs_dot(self):
        assert path.IsAbs("./file") is False

    def test_isabs_dotdot(self):
        assert path.IsAbs("../file") is False

    def test_isabs_root(self):
        assert path.IsAbs("/") is True

    def test_isabs_empty(self):
        assert path.IsAbs("") is False


class TestMatch:
    def test_match_star(self):
        result = path.Match("*.txt", "file.txt")
        assert result.is_ok()
        assert result.unwrap() is True

    def test_match_star_no_match(self):
        result = path.Match("*.txt", "file.pdf")
        assert result.is_ok()
        assert result.unwrap() is False

    def test_match_question(self):
        result = path.Match("file?.txt", "file1.txt")
        assert result.is_ok()
        assert result.unwrap() is True

    def test_match_question_no_match(self):
        result = path.Match("file?.txt", "file10.txt")
        assert result.is_ok()
        assert result.unwrap() is False

    def test_match_bracket(self):
        result = path.Match("file[0-9].txt", "file5.txt")
        assert result.is_ok()
        assert result.unwrap() is True

    def test_match_bracket_no_match(self):
        result = path.Match("file[0-9].txt", "filea.txt")
        assert result.is_ok()
        assert result.unwrap() is False

    def test_match_exact(self):
        result = path.Match("file.txt", "file.txt")
        assert result.is_ok()
        assert result.unwrap() is True

    def test_match_bad_pattern(self):
        result = path.Match("[", "file")
        assert result.is_err()

    def test_match_complex(self):
        result = path.Match("*/*/*.txt", "a/b/c.txt")
        assert result.is_ok()
        assert result.unwrap() is True
