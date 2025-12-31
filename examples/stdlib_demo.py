#!/usr/bin/env python3
"""Comprehensive demo of Go stdlib bindings."""

from goated.std import base64, errors, fmt, hex, io, sort, strings, sync, time


def demo_strings():
    print("=== strings package ===")

    s = "Hello, World!"
    print(f"Contains 'World': {strings.Contains(s, 'World')}")
    print(f"HasPrefix 'Hello': {strings.HasPrefix(s, 'Hello')}")
    print(f"ToUpper: {strings.ToUpper(s)}")
    print(f"Replace: {strings.Replace(s, 'World', 'Go', 1)}")
    print(f"Split: {strings.Split('a,b,c', ',')}")
    print(f"Join: {strings.Join(['a', 'b', 'c'], '-')}")
    print(f"TrimSpace: '{strings.TrimSpace('  hello  ')}'")
    print()


def demo_sort():
    print("=== sort package ===")

    ints = [64, 34, 25, 12, 22, 11, 90]
    print(f"Before: {ints}")
    sort.Ints(ints)
    print(f"After Ints(): {ints}")
    print(f"IntsAreSorted: {sort.IntsAreSorted(ints)}")
    print(f"SearchInts(25): {sort.SearchInts(ints, 25)}")

    words = ["banana", "apple", "cherry"]
    sort.Strings(words)
    print(f"Sorted strings: {words}")

    data = sort.IntSlice([5, 2, 8, 1, 9])
    sort.Sort(sort.Reverse(data))
    print(f"Reverse sorted: {list(data)}")
    print()


def demo_time():
    print("=== time package ===")

    now = time.Now()
    print(f"Now: {now}")
    print(f"Year: {now.Year()}, Month: {now.Month()}, Day: {now.Day()}")
    print(f"Hour: {now.Hour()}, Minute: {now.Minute()}")
    print(f"Weekday: {now.Weekday()}")
    print(f"Unix timestamp: {now.Unix()}")

    duration = time.ParseDuration("2h30m")
    print(f"Parsed duration: {duration}")
    print(f"In hours: {duration.Hours()}")

    future = now.Add(duration)
    print(f"2h30m from now: {future}")
    print()


def demo_base64():
    print("=== base64 package ===")

    data = b"Hello, World!"

    encoded = base64.StdEncoding.EncodeToString(data)
    print(f"Encoded: {encoded}")

    decoded, err = base64.StdEncoding.DecodeString(encoded)
    print(f"Decoded: {decoded}")

    url_encoded = base64.URLEncoding.EncodeToString(data)
    print(f"URL Encoded: {url_encoded}")

    raw_encoded = base64.RawStdEncoding.EncodeToString(data)
    print(f"Raw (no padding): {raw_encoded}")
    print()


def demo_hex():
    print("=== hex package ===")

    data = b"Hello"

    encoded = hex.EncodeToString(data)
    print(f"Hex encoded: {encoded}")

    decoded, err = hex.DecodeString(encoded)
    print(f"Decoded: {decoded}")

    print("\nHex dump:")
    print(hex.Dump(b"Hello, World! This is a hex dump demo."))
    print()


def demo_fmt():
    print("=== fmt package ===")

    print(fmt.Sprintf("Hello, %s!", "World"))
    print(fmt.Sprintf("Integer: %d, Float: %.2f", 42, 3.14159))
    print(fmt.Sprintf("Binary: %b, Hex: %x", 255, 255))
    print(fmt.Sprintf("Quoted: %q", "hello\tworld"))
    print(fmt.Sprintf("Type: %T", [1, 2, 3]))
    print(fmt.Sprintf("Boolean: %t", True))

    print(f"Sprint: {fmt.Sprint('a', 1, 'b', 2)}")
    print(f"Sprintln: {fmt.Sprintln('hello', 'world')}", end="")
    print()


def demo_errors():
    print("=== errors package ===")

    err1 = errors.New("file not found")
    print(f"Error: {err1}")

    err2 = errors.Wrap(err1, "failed to open config")
    print(f"Wrapped: {err2}")

    print(f"Is same error: {errors.Is(err2, err1)}")
    print(f"Root cause: {errors.Cause(err2)}")

    joined = errors.Join(errors.New("error 1"), errors.New("error 2"), errors.New("error 3"))
    print(f"Joined errors:\n{joined}")
    print()


def demo_io():
    print("=== io package ===")

    src = io.StringReader("Hello, World!")
    dst = io.StringBuilder()

    n, err = io.Copy(dst, src)
    print(f"Copied {n} bytes: {dst.String()}")

    reader = io.BytesReader(b"Test data for reading")
    data, err = io.ReadAll(reader)
    print(f"ReadAll: {data}")

    r, w = io.Pipe()
    w.Write(b"Pipe data")
    w.Close()

    buf = bytearray(20)
    n, _ = r.Read(buf)
    print(f"From pipe: {bytes(buf[:n])}")
    print()


def demo_sync():
    print("=== sync package ===")

    mu = sync.Mutex()
    counter = [0]

    def increment():
        mu.Lock()
        try:
            counter[0] += 1
        finally:
            mu.Unlock()

    import threading

    threads = [threading.Thread(target=increment) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Counter after 100 increments: {counter[0]}")

    once = sync.Once()
    initialized = [False]

    def init():
        initialized[0] = True
        print("Initialized!")

    once.Do(init)
    once.Do(init)
    once.Do(init)
    print(f"Only ran once: {initialized[0]}")

    m = sync.Map()
    m.Store("key1", "value1")
    m.Store("key2", "value2")

    val, ok = m.Load("key1")
    print(f"Map load: {val}, found: {ok}")
    print()


def main():
    demo_strings()
    demo_sort()
    demo_time()
    demo_base64()
    demo_hex()
    demo_fmt()
    demo_errors()
    demo_io()
    demo_sync()

    print("=== All demos completed! ===")


if __name__ == "__main__":
    main()
