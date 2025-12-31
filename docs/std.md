# goated.std - Standard Library Reference

Go standard library bindings for Python. Functions maintain Go naming conventions (PascalCase).

## Overview

This module provides Python bindings to Go's standard library. Each function is a direct mapping to its Go equivalent, giving you Go's performance with Python's ease of use.

### Performance Notes

| Category | Speedup vs Python | Best For |
|----------|-------------------|----------|
| JSON | 5-7x | Large payloads (>1KB) |
| Hashing | 7-10x | Files, bulk data |
| Compression | 5-8x | Files >10KB |
| Strings | 3-6x | Batch operations |
| Regex | 5-10x | Complex patterns, large text |

**FFI Overhead**: Each call has ~1-5μs overhead. Use GOATED for:
- Data larger than 1KB
- Batch operations
- CPU-intensive work (hashing, compression, parsing)

### Thread Safety

All `goated.std` functions are thread-safe. They can be called concurrently from multiple threads or goroutines without additional synchronization.

### Error Handling

Functions that can fail return `Result[T, GoError]`:

```python
from goated.std import strconv
from goated import Ok, Err

result = strconv.Atoi("42")
match result:
    case Ok(value):
        print(f"Parsed: {value}")
    case Err(error):
        print(f"Error: {error}")

# Or use unwrap methods
value = strconv.Atoi("42").unwrap()  # Raises on error
value = strconv.Atoi("invalid").unwrap_or(0)  # Default on error
```

## Table of Contents

- [String & Bytes](#string--bytes): strings, bytes, strconv, unicode, utf8
- [Encoding](#encoding): base64, hex, binary, json, csv, gzip, xml
- [Cryptography](#cryptography): hash (SHA256, MD5, etc.)
- [Paths](#paths): path, filepath
- [Time](#time): time
- [I/O](#io): io, bufio
- [OS](#os): os, goos
- [Network](#network): net, url
- [Regular Expressions](#regular-expressions): regexp
- [Sorting](#sorting): sort
- [Random](#random): rand
- [Logging](#logging): log
- [HTML](#html): html
- [MIME](#mime): mime
- [Templates](#templates): template
- [Testing](#testing): testing
- [Archive](#archive): zip

---

## String & Bytes

### strings (Go: `strings`)

```python
from goated.std import strings

strings.Contains("hello", "ell")      # True
strings.Split("a,b,c", ",")           # ["a", "b", "c"]
strings.Join(["a", "b"], "-")         # "a-b"
strings.ToUpper("hello")              # "HELLO"
strings.ToLower("HELLO")              # "hello"
strings.TrimSpace("  hi  ")           # "hi"
strings.Replace("foo", "o", "0", -1)  # "f00"
strings.HasPrefix("hello", "he")      # True
strings.HasSuffix("hello", "lo")      # True
strings.Index("hello", "l")           # 2
strings.Count("hello", "l")           # 2
strings.Repeat("go", 3)               # "gogogo"
strings.Fields("a b  c")              # ["a", "b", "c"]

# Builder for efficient concatenation
b = strings.Builder()
b.WriteString("hello")
b.WriteString(" world")
str(b)  # "hello world"
```

### bytes (Go: `bytes`)

Same API as strings, but operates on `bytes`:

```python
from goated.std import bytes as gobytes

gobytes.Contains(b"hello", b"ell")    # True
gobytes.Split(b"a,b,c", b",")         # [b"a", b"b", b"c"]
gobytes.ToUpper(b"hello")             # b"HELLO"
gobytes.Equal(b"a", b"a")             # True
gobytes.Compare(b"a", b"b")           # -1
```

### strconv (Go: `strconv`)

```python
from goated.std import strconv

strconv.Atoi("42")                    # Result[int, GoError]
strconv.Itoa(42)                      # "42"
strconv.ParseInt("ff", 16, 64)        # Result[int, GoError]
strconv.ParseFloat("3.14", 64)        # Result[float, GoError]
strconv.FormatInt(255, 16)            # "ff"
strconv.Quote("hello\n")              # '"hello\\n"'
strconv.Unquote('"hello"')            # Result[str, GoError]
```

### unicode (Go: `unicode`)

```python
from goated.std import unicode

unicode.IsLetter('a')     # True
unicode.IsDigit('5')      # True
unicode.IsSpace(' ')      # True
unicode.ToUpper('a')      # 'A'
unicode.ToLower('A')      # 'a'
```

### utf8 (Go: `unicode/utf8`)

```python
from goated.std import utf8

utf8.Valid(b"hello")              # True
utf8.ValidString("hello")         # True
utf8.RuneLen('a')                 # 1
utf8.RuneLen('\u4e2d')            # 3
utf8.DecodeRune(b"\xe4\xb8\xad")  # ('\u4e2d', 3)
```

## Encoding

### base64 (Go: `encoding/base64`)

```python
from goated.std import base64

base64.StdEncoding.EncodeToString(b"hello")           # "aGVsbG8="
base64.StdEncoding.DecodeString("aGVsbG8=")           # (b"hello", None)
base64.URLEncoding.EncodeToString(b"hello")           # URL-safe encoding
base64.RawStdEncoding.EncodeToString(b"hello")        # No padding
```

### hex (Go: `encoding/hex`)

```python
from goated.std import hex

hex.EncodeToString(b"\x00\xff")   # "00ff"
hex.DecodeString("00ff")          # (b"\x00\xff", None)
```

### binary (Go: `encoding/binary`)

```python
from goated.std import binary

binary.BigEndian.Uint16(b"\x01\x02")      # 258
binary.LittleEndian.Uint16(b"\x01\x02")   # 513
binary.PutVarint(buf, 300)                # Varint encoding
binary.Varint(buf)                        # Varint decoding
```

### json (Go: `encoding/json`)

```python
from goated.std import json

json.Marshal({"key": "value"})            # b'{"key":"value"}'
json.Unmarshal(b'{"key":"value"}')        # {"key": "value"}
json.MarshalIndent(obj, "", "  ")         # Pretty print
```

### csv (Go: `encoding/csv`)

```python
from goated.std import csv
import io

r = csv.NewReader(io.StringIO("a,b,c\n1,2,3"))
r.ReadAll()  # [["a","b","c"], ["1","2","3"]]
```

### gzip (Go: `compress/gzip`)

```python
from goated.std import gzip

compressed = gzip.Compress(b"hello world")
gzip.Decompress(compressed)  # b"hello world"
```

### xml (Go: `encoding/xml`)

```python
from goated.std import xml

xml.Marshal(obj)              # XML bytes
xml.Unmarshal(xml_bytes)      # Parsed object
```

## I/O

### io (Go: `io`)

```python
from goated.std import io

io.ReadAll(reader)                    # Read entire content
io.Copy(dst, src)                     # Copy from reader to writer
io.CopyN(dst, src, n)                 # Copy n bytes
io.LimitReader(reader, n)             # Limit reads to n bytes
io.MultiReader(r1, r2)                # Concatenate readers
io.MultiWriter(w1, w2)                # Tee writes
io.TeeReader(reader, writer)          # Read and copy to writer

# In-memory readers
io.StringReader("hello")
io.BytesReader(b"hello")
io.BytesBuffer()
```

### bufio (Go: `bufio`)

```python
from goated.std import bufio, io

# Buffered reading
r = bufio.NewReader(io.StringReader("line1\nline2"))
r.ReadLine()      # (b"line1", False, None)
r.ReadString('\n')

# Scanner for line-by-line
scanner = bufio.NewScanner(io.StringReader("a\nb\nc"))
while scanner.Scan():
    print(scanner.Text())

# Split functions
bufio.ScanLines   # Split by lines
bufio.ScanWords   # Split by words
bufio.ScanBytes   # Split by bytes
bufio.ScanRunes   # Split by runes
```

### os (Go: `os`)

Exposed as `goated.std.os` (maps to `goos` internally):

```python
from goated.std import os

os.Getenv("HOME")
os.Setenv("KEY", "value")
os.Getwd()
os.Chdir("/tmp")
os.Mkdir("dir", 0o755)
os.MkdirAll("a/b/c", 0o755)
os.Remove("file")
os.RemoveAll("dir")
os.Rename("old", "new")
os.Stat("file")
os.ReadFile("file.txt")
os.WriteFile("file.txt", b"content", 0o644)

# File operations
f = os.Open("file.txt")
f = os.Create("new.txt")
f.Read(buf)
f.Write(b"data")
f.Close()
```

## Paths

### path (Go: `path`)

URL-style paths (forward slashes only):

```python
from goated.std import path

path.Join("a", "b", "c")      # "a/b/c"
path.Base("/a/b/c")           # "c"
path.Dir("/a/b/c")            # "/a/b"
path.Ext("file.txt")          # ".txt"
path.Clean("a//b/../c")       # "a/c"
path.Split("/a/b/c")          # ("/a/b/", "c")
path.IsAbs("/a/b")            # True
```

### filepath (Go: `path/filepath`)

OS-aware paths (uses `os.sep`):

```python
from goated.std import filepath

filepath.Join("a", "b", "c")          # OS-specific
filepath.Abs("relative/path")         # Result[str, GoError]
filepath.Rel("/a/b", "/a/b/c/d")      # Result[str, GoError] -> "c/d"
filepath.Walk("/dir", walk_func)      # Walk directory tree
filepath.Glob("*.py")                 # Result[list[str], GoError]
filepath.Match("*.py", "test.py")     # Result[bool, GoError]
filepath.EvalSymlinks("/path")        # Resolve symlinks
```

## Time

### time (Go: `time`)

```python
from goated.std import time

# Current time
now = time.Now()
now.Year(), now.Month(), now.Day()
now.Hour(), now.Minute(), now.Second()
now.Unix()        # Unix timestamp
now.UnixNano()    # Nanosecond precision

# Create time
t = time.Date(2024, 1, 15, 10, 30, 0, 0, time.UTC)
t = time.Unix(1705312200, 0)

# Duration
time.Second, time.Minute, time.Hour
time.ParseDuration("1h30m")           # Duration
dur = time.Duration(5 * time.Second)
dur.Seconds(), dur.Minutes()

# Arithmetic
t.Add(time.Hour)
t.Sub(other_time)                     # Duration
time.Since(t)                         # Duration since t
time.Until(t)                         # Duration until t

# Format/Parse (Go reference time: Mon Jan 2 15:04:05 MST 2006)
t.Format(time.RFC3339)
time.Parse(time.RFC3339, "2024-01-15T10:30:00Z")

# Sleep
time.Sleep(time.Second)
```

## Concurrency

### sync (Go: `sync`)

```python
from goated.std import sync

# Mutex
mu = sync.Mutex()
with mu:
    # critical section
    pass

# RWMutex
rw = sync.RWMutex()
with rw.RLock():
    # read lock
    pass
with rw:
    # write lock
    pass

# WaitGroup
wg = sync.WaitGroup()
wg.Add(1)
wg.Done()
wg.Wait()

# Once
once = sync.Once()
once.Do(init_func)

# Pool
pool = sync.Pool(new=lambda: object())
obj = pool.Get()
pool.Put(obj)

# Map (concurrent map)
m = sync.Map()
m.Store("key", "value")
m.Load("key")
m.Delete("key")
```

### context (Go: `context`)

```python
from goated.std import context

ctx = context.Background()
ctx = context.TODO()

ctx, cancel = context.WithCancel(context.Background())
cancel()  # Cancel the context

ctx, cancel = context.WithTimeout(context.Background(), 5 * time.Second)
ctx, cancel = context.WithDeadline(context.Background(), deadline_time)

ctx = context.WithValue(parent_ctx, "key", "value")
ctx.Value("key")

# Check cancellation
ctx.Done()  # Channel that closes on cancel
ctx.Err()   # context.Canceled or context.DeadlineExceeded
```

### goroutine (Go: goroutine primitives)

```python
from goated.std.goroutine import go, GoGroup, Chan, Mutex, parallel_map

# Spawn goroutine
future = go(func, arg1, arg2)
result = future.result()

# GoGroup - automatic waiting
with GoGroup() as g:
    g.go(task1)
    g.go(task2)
# Waits here

# GoGroup with concurrency limit
with GoGroup(limit=5) as g:
    for url in urls:
        g.go(fetch, url)

# Channels
ch = Chan[int](buffer=10)
ch.Send(42)
val = ch.Recv()
ch.Close()

for val in ch:  # Iterate until closed
    print(val)

# Select
from goated.std.goroutine import Select, SelectCase
idx, val, ok = Select(
    SelectCase(ch1),
    SelectCase(ch2),
)

# Parallel map
results = parallel_map(func, items)
```

### parallel (Go: parallel batch ops)

```python
from goated.std import parallel

# Parallel hashing
results = parallel.parallel_hash_sha256(list_of_bytes)

# Parallel string operations
results = parallel.parallel_map_upper(list_of_strings)
results = parallel.parallel_contains(list_of_strings, "needle")
```

## Formatting

### fmt (Go: `fmt`)

```python
from goated.std import fmt

# Print to stdout
fmt.Print("hello")
fmt.Println("hello")
fmt.Printf("Hello, %s!", "World")

# Sprint returns string
s = fmt.Sprint(1, 2, 3)           # "1 2 3"
s = fmt.Sprintf("%d + %d", 1, 2)  # "1 + 2"

# Fprint writes to writer
fmt.Fprint(writer, "hello")
fmt.Fprintf(writer, "%s", "hello")

# Errorf creates error
err = fmt.Errorf("failed: %s", reason)
err = fmt.Errorf("wrap: %w", other_err)  # Wrapped error
```

Go format verbs: `%v` (default), `%+v` (with fields), `%#v` (Go syntax), `%T` (type), `%t` (bool), `%d` (int), `%x` (hex), `%f` (float), `%s` (string), `%q` (quoted), `%p` (pointer).

## Crypto & Hash

### crypto (Go: `crypto/*`)

```python
from goated.std import crypto

crypto.sha256(b"data")        # SHA-256 hash bytes
crypto.sha512(b"data")
crypto.sha1(b"data")
crypto.md5(b"data")

crypto.GenerateRandomBytes(32)    # Cryptographically secure random
crypto.GenerateRandomString(16)   # Random alphanumeric string
```

### hash (Go: `hash/*`)

```python
from goated.std import hash

h = hash.NewSHA256()
h.Write(b"hello")
h.Write(b" world")
h.Sum()  # Final hash

h = hash.NewMD5()
h = hash.NewSHA1()
h = hash.NewSHA512()
h = hash.NewCRC32()
```

## Other

### errors (Go: `errors`)

```python
from goated.std import errors

err = errors.New("something failed")
errors.Is(err, target_err)
errors.As(err, error_type)
errors.Unwrap(wrapped_err)
errors.Join(err1, err2, err3)
```

### math (Go: `math`)

```python
from goated.std import math

math.Abs(-5)          # 5.0
math.Sqrt(16)         # 4.0
math.Pow(2, 10)       # 1024.0
math.Sin, math.Cos, math.Tan
math.Log, math.Log10, math.Log2
math.Ceil, math.Floor, math.Round
math.Min, math.Max
math.IsNaN, math.IsInf
math.Pi, math.E
```

### rand (Go: `math/rand`)

```python
from goated.std import rand

rand.Seed(42)
rand.Intn(100)        # Random int [0, 100)
rand.Int63()          # Random int64
rand.Float64()        # Random float [0.0, 1.0)
rand.Shuffle(n, swap_func)
```

### regexp (Go: `regexp`)

```python
from goated.std import regexp

re = regexp.MustCompile(r"\d+")
re.MatchString("abc123")              # True
re.FindString("abc123def")            # "123"
re.FindAllString("a1b2c3", -1)        # ["1", "2", "3"]
re.ReplaceAllString("a1b2", "X")      # "aXbX"
re.Split("a1b2c3", -1)                # ["a", "b", "c", ""]

regexp.Match(r"\d+", "123")           # True
regexp.QuoteMeta("a.b")               # r"a\.b"
```

### sort (Go: `sort`)

```python
from goated.std import sort

data = [3, 1, 4, 1, 5]
sort.Ints(data)           # Sorts in-place
sort.IntsAreSorted(data)  # True

sort.Strings(["b", "a"])
sort.Float64s([3.1, 1.4])

sort.Slice(data, lambda i, j: data[i] < data[j])
sort.Search(n, lambda i: pred(i))     # Binary search
```

### net (Go: `net`)

```python
from goated.std import net

conn = net.Dial("tcp", "example.com:80")
listener = net.Listen("tcp", ":8080")

ip = net.ParseIP("192.168.1.1")
net.LookupHost("example.com")
net.LookupIP("example.com")
```

### http (Go: `net/http`)

```python
from goated.std import http

# Client
resp = http.Get("https://example.com")
resp = http.Post(url, "application/json", body)
resp = http.PostForm(url, {"key": "value"})

client = http.Client(timeout=30)
resp = client.Get(url)

# Response
resp.StatusCode
resp.Header
resp.Body.Read()

# Server
def handler(w, r):
    w.Write(b"Hello")

mux = http.ServeMux()
mux.HandleFunc("/", handler)
http.ListenAndServe(":8080", mux)
```

### url (Go: `net/url`)

```python
from goated.std import url

u = url.Parse("https://example.com/path?q=1")
u.Scheme, u.Host, u.Path, u.RawQuery

url.QueryEscape("a b")        # "a+b"
url.QueryUnescape("a+b")      # "a b"
url.PathEscape("/a/b")
```

### html (Go: `html`)

```python
from goated.std import html

html.EscapeString("<script>")     # "&lt;script&gt;"
html.UnescapeString("&lt;")       # "<"
```

### mime (Go: `mime`)

```python
from goated.std import mime

mime.TypeByExtension(".json")     # "application/json"
mime.ExtensionsByType("text/html")
```

### log (Go: `log`)

```python
from goated.std import log

log.Print("message")
log.Printf("value: %d", 42)
log.Println("message")
log.Fatal("error")        # Prints and exits
log.Panic("error")        # Prints and panics

log.SetPrefix("[APP] ")
log.SetFlags(log.Ldate | log.Ltime)
```

### testing (Go: `testing`)

```python
from goated.std import testing

t = testing.T()
t.Error("failed")
t.Errorf("expected %d", 42)
t.Fatal("critical failure")
t.Skip("skipping test")
t.Log("debug info")

testing.Assert(condition, "message")
testing.AssertEqual(a, b)
testing.AssertNil(err)
```
