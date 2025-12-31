# GOATED Architecture

This document describes the internal architecture of GOATED, including the FFI design, memory management, and the M:N scheduler.

## Overview

GOATED bridges Python and Go through a carefully designed FFI layer that prioritizes safety, performance, and ease of use.

```mermaid
flowchart TB
    subgraph Python["Python Layer"]
        API[goated.std.*]
        Runtime[goated.runtime]
        Result[Result Types]
    end
    
    subgraph FFI["FFI Bridge"]
        ctypes[ctypes bindings]
        Handles[Handle Registry]
    end
    
    subgraph Go["Go Layer"]
        Stdlib[Go stdlib]
        Shared[libgoated.so]
    end
    
    API --> ctypes
    Runtime --> ctypes
    ctypes --> Handles
    Handles --> Shared
    Shared --> Stdlib
```

## FFI Design

### Handle-Based Approach

GOATED uses a **handle-based** FFI design instead of passing raw pointers. This ensures memory safety across the Python-Go boundary.

```mermaid
sequenceDiagram
    participant P as Python
    participant H as Handle Registry
    participant G as Go Runtime
    
    P->>G: Call function (returns []byte)
    G->>H: Store result, get handle ID
    H-->>P: Return handle (uint64)
    P->>H: Request data by handle
    H-->>P: Return copy of data
    P->>H: Release handle
    H->>G: Free Go memory
```

**Why handles instead of raw pointers?**

1. **GC Safety**: Go's garbage collector can move objects. Handles prevent dangling pointers.
2. **Lifecycle Control**: Python controls when Go memory is freed.
3. **Thread Safety**: Handle operations are atomic.
4. **Debugging**: Handles can be tracked and validated.

### Memory Management

```mermaid
flowchart LR
    subgraph Python
        PyObj[Python Object]
        Ref[Handle Reference]
    end
    
    subgraph HandleRegistry
        Map["map[uint64]interface{}"]
        Counter[Atomic Counter]
    end
    
    subgraph Go
        GoData[Go Data]
    end
    
    PyObj --> Ref
    Ref -->|"ID"| Map
    Map -->|"stores"| GoData
    
    PyObj -.->|"destructor"| Ref
    Ref -.->|"release"| Map
    Map -.->|"delete"| GoData
```

**Lifecycle:**

1. Go function returns data → stored in registry → handle ID returned to Python
2. Python wraps handle in object with `__del__` destructor
3. When Python object is garbage collected → handle released → Go memory freed

## Concurrency Architecture

### M:N Scheduler

GOATED implements an M:N scheduler that maps M goroutines to N OS threads, inspired by Go's runtime.

```mermaid
flowchart TB
    subgraph UserCode["User Code"]
        G1[go func1]
        G2[go func2]
        G3[go func3]
        G4[go func4]
    end
    
    subgraph Scheduler["M:N Scheduler"]
        Q1[Worker Queue 1]
        Q2[Worker Queue 2]
        GQ[Global Queue]
    end
    
    subgraph Threads["OS Threads"]
        T1[Thread 1]
        T2[Thread 2]
    end
    
    G1 --> GQ
    G2 --> GQ
    G3 --> GQ
    G4 --> GQ
    
    GQ --> Q1
    GQ --> Q2
    
    Q1 --> T1
    Q2 --> T2
    
    Q1 <-.->|"steal"| Q2
```

### Work Stealing

When a worker's local queue is empty, it can steal work from other workers:

```mermaid
sequenceDiagram
    participant W1 as Worker 1
    participant Q1 as Queue 1
    participant Q2 as Queue 2
    participant W2 as Worker 2
    
    W1->>Q1: Pop task
    Q1-->>W1: Empty!
    W1->>Q2: Try steal half
    Q2-->>W1: Return N/2 tasks
    W1->>W1: Execute stolen tasks
```

**Optimizations:**

- **Fast Path**: Direct submission to `ThreadPoolExecutor` (zero Python overhead)
- **Lazy Stealing**: Work stealing only activates under load imbalance
- **Batch Operations**: Reduces lock contention for bulk submissions
- **Lock-Free Counters**: Atomic task counting on free-threaded Python

### Channel Implementation

Channels provide Go-style communication between goroutines:

```mermaid
flowchart LR
    subgraph Sender
        S1[Goroutine 1]
        S2[Goroutine 2]
    end
    
    subgraph Channel["Chan[T]"]
        Buffer[Ring Buffer]
        Lock[Condition]
    end
    
    subgraph Receiver
        R1[Goroutine 3]
    end
    
    S1 -->|"Send()"| Buffer
    S2 -->|"Send()"| Buffer
    Buffer -->|"Recv()"| R1
    Lock -.->|"notify"| Buffer
```

**Chan Optimizations (v0.1.0+):**

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Buffer | `queue.Queue` | `deque` + `Condition` | 1.5x faster |
| Blocking | Queue's internal lock | Direct `Condition.wait()` | Lower latency |
| Close | Sentinel value | Boolean flag + notify_all | Cleaner semantics |

## API Layers

GOATED provides three API styles to match different preferences:

```mermaid
flowchart TB
    subgraph Styles["API Styles"]
        Direct["Direct Mapping<br/>goated.std.strings.Split()"]
        Pythonic["Pythonic Wrappers<br/>goated.pythonic.strings.split()"]
        Compat["Drop-in Replacement<br/>goated.compat.json.loads()"]
    end
    
    subgraph Core["Core Layer"]
        FFI[FFI Bindings]
        Result[Result Types]
    end
    
    Direct --> FFI
    Pythonic --> Direct
    Pythonic --> Result
    Compat --> Pythonic
```

| Style | Naming | Returns | Use Case |
|-------|--------|---------|----------|
| Direct | Go PascalCase | Go types | Maximum control, Go familiarity |
| Pythonic | snake_case | `Result[T, E]` | Idiomatic Python, explicit errors |
| Compat | Python stdlib | Python types | Drop-in replacement |

## Free-Threaded Python Support

GOATED automatically detects and optimizes for Python 3.13t (free-threaded/no-GIL):

```mermaid
flowchart TB
    Start[Runtime Start]
    Check{Free-threaded?}
    GIL[GIL Mode]
    NoGIL[No-GIL Mode]
    
    Start --> Check
    Check -->|"sys._is_gil_enabled() == False"| NoGIL
    Check -->|"GIL enabled"| GIL
    
    GIL --> GILWorkers["Workers: min(32, CPU×4)"]
    NoGIL --> NoGILWorkers["Workers: CPU count"]
    
    GIL --> GILOps["Standard threading"]
    NoGIL --> NoGILOps["True parallelism<br/>Atomic operations"]
```

**Optimizations for free-threaded Python:**

- Reduced worker count (true parallelism doesn't need oversubscription)
- Atomic operations for counters and flags
- Lock-free fast paths where possible

## Code Generation

GOATED includes a code generator that automatically creates bindings from Go source:

```mermaid
flowchart LR
    subgraph Input
        GoSrc[Go Source]
        GoAST[Go AST]
    end
    
    subgraph Generator["goated-gen"]
        Parse[Parse Package]
        Filter[Filter Bindable]
        Gen[Generate Code]
    end
    
    subgraph Output
        GoFFI[Go CGO Exports]
        PyBind[Python ctypes]
    end
    
    GoSrc --> Parse
    Parse --> GoAST
    GoAST --> Filter
    Filter --> Gen
    Gen --> GoFFI
    Gen --> PyBind
```

**Bindable function criteria:**

- Exported (PascalCase name)
- Parameters: basic types, slices, strings
- Returns: basic types, slices, strings, error
- No channels, interfaces, or complex structs (yet)

## Performance Characteristics

### When GOATED Wins

| Operation | Why GOATED is Faster |
|-----------|---------------------|
| JSON parsing | Go's `encoding/json` is highly optimized |
| Hashing (SHA256) | Go's crypto uses assembly optimizations |
| Compression | Go's gzip/zip use efficient C bindings |
| String operations | Go strings are immutable, optimized |
| Regex (large text) | Go's RE2 is faster for complex patterns |

### When Python Wins

| Operation | Why Python is Faster |
|-----------|---------------------|
| Small operations | FFI overhead dominates |
| Single string ops | Python's string interning helps |
| Already-fast ops | No room for improvement |

### FFI Overhead

Each FFI call has ~1-5μs overhead. GOATED wins when:

```
Go speedup × batch size > FFI overhead
```

**Rule of thumb**: Use GOATED for operations on data > 1KB or batch operations.

## See Also

- [README.md](README.md) - Getting started guide
- [docs/std.md](docs/std.md) - API reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [CHANGELOG.md](CHANGELOG.md) - Version history
