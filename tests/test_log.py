import io
import sys

import pytest

from goated.std import log


class TestPrint:
    def test_print(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        log.Print("test message")
        output = buf.getvalue()
        assert "test message" in output

    def test_print_multiple_args(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        log.Print("hello", "world")
        output = buf.getvalue()
        assert "hello" in output
        assert "world" in output


class TestPrintf:
    def test_printf(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        log.Printf("value: %d", 42)
        output = buf.getvalue()
        assert "value: 42" in output

    def test_printf_multiple(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        log.Printf("%s: %d", "count", 10)
        output = buf.getvalue()
        assert "count: 10" in output


class TestPrintln:
    def test_println(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        log.Println("line message")
        output = buf.getvalue()
        assert "line message" in output
        assert output.endswith("\n")


class TestPanic:
    def test_panic(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        with pytest.raises(RuntimeError) as exc_info:
            log.Panic("panic message")
        assert "panic message" in str(exc_info.value)

    def test_panicf(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        with pytest.raises(RuntimeError) as exc_info:
            log.Panicf("error code: %d", 500)
        assert "error code: 500" in str(exc_info.value)

    def test_panicln(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        with pytest.raises(RuntimeError) as exc_info:
            log.Panicln("panic", "line")
        assert "panic" in str(exc_info.value)


class TestSetPrefix:
    def test_set_prefix(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        log.SetPrefix("[TEST] ")
        log.Print("message")
        output = buf.getvalue()
        assert "[TEST]" in output

    def test_prefix(self):
        log.SetPrefix("[PREFIX] ")
        assert log.Prefix() == "[PREFIX] "
        log.SetPrefix("")


class TestSetFlags:
    def test_set_flags(self):
        log.SetFlags(log.Ldate | log.Ltime)
        assert log.Flags() == (log.Ldate | log.Ltime)

    def test_flags_date(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        log.SetFlags(log.Ldate)
        log.SetPrefix("")
        log.Print("test")
        output = buf.getvalue()
        assert "/" in output


class TestNew:
    def test_new_logger(self):
        buf = io.StringIO()
        logger = log.New(buf, "[CUSTOM] ", log.LstdFlags)

        logger.Print("custom message")
        output = buf.getvalue()
        assert "[CUSTOM]" in output
        assert "custom message" in output

    def test_new_logger_methods(self):
        buf = io.StringIO()
        logger = log.New(buf, "", 0)

        logger.Print("print")
        logger.Printf("printf %d", 1)
        logger.Println("println")

        output = buf.getvalue()
        assert "print" in output
        assert "printf 1" in output
        assert "println" in output


class TestLoggerSetters:
    def test_logger_set_output(self):
        buf1 = io.StringIO()
        buf2 = io.StringIO()
        logger = log.New(buf1, "", 0)

        logger.Print("first")
        logger.SetOutput(buf2)
        logger.Print("second")

        assert "first" in buf1.getvalue()
        assert "second" in buf2.getvalue()

    def test_logger_set_prefix(self):
        buf = io.StringIO()
        logger = log.New(buf, "", 0)

        logger.SetPrefix("[NEW] ")
        logger.Print("test")

        assert "[NEW]" in buf.getvalue()

    def test_logger_set_flags(self):
        buf = io.StringIO()
        logger = log.New(buf, "", 0)

        logger.SetFlags(log.Ldate)
        assert logger.Flags() == log.Ldate


class TestDefault:
    def test_default(self):
        default_logger = log.Default()
        assert default_logger is not None


class TestWriter:
    def test_writer(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        writer = log.Writer()
        assert writer is buf


class TestOutput:
    def test_output(self):
        buf = io.StringIO()
        log.SetOutput(buf)
        log.SetFlags(0)
        log.SetPrefix("")
        err = log.Output(1, "direct output")
        assert err is None
        assert "direct output" in buf.getvalue()


class TestConstants:
    def test_constants_defined(self):
        assert log.Ldate == 1
        assert log.Ltime == 2
        assert log.Lmicroseconds == 4
        assert log.Llongfile == 8
        assert log.Lshortfile == 16
        assert log.LUTC == 32
        assert log.Lmsgprefix == 64
        assert log.LstdFlags == (log.Ldate | log.Ltime)


class TestLoggerPanic:
    def test_logger_panic(self):
        buf = io.StringIO()
        logger = log.New(buf, "", 0)
        with pytest.raises(RuntimeError):
            logger.Panic("logger panic")

    def test_logger_panicf(self):
        buf = io.StringIO()
        logger = log.New(buf, "", 0)
        with pytest.raises(RuntimeError):
            logger.Panicf("logger panic %d", 1)


class TestCleanup:
    def test_reset_defaults(self):
        log.SetOutput(sys.stderr)
        log.SetPrefix("")
        log.SetFlags(log.LstdFlags)
