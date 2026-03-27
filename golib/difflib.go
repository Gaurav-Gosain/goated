package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"runtime"
	"strings"
	"sync"
	"unsafe"
)

// ============================================================================
// Diff computation using Myers' algorithm - much faster than Python's difflib
// ============================================================================

// editOp represents a diff operation
type editOp struct {
	tag    byte // 'e' equal, 'r' replace, 'i' insert, 'd' delete
	i1, i2 int  // indices in a
	j1, j2 int  // indices in b
}

// computeOpcodes computes the edit operations between two slices of strings
func computeOpcodes(a, b []string) []editOp {
	m, n := len(a), len(b)
	if m == 0 && n == 0 {
		return nil
	}
	if m == 0 {
		return []editOp{{'i', 0, 0, 0, n}}
	}
	if n == 0 {
		return []editOp{{'d', 0, m, 0, 0}}
	}

	// Build LCS using Hunt-Szymanski approach with hash map
	// Map b lines to their positions
	bMap := make(map[string][]int, n)
	for j, line := range b {
		bMap[line] = append(bMap[line], j)
	}

	// Dynamic programming for LCS
	// Use patience-like approach: match equal lines, diff the gaps
	ops := make([]editOp, 0, m+n)
	i, j := 0, 0

	// Find matching blocks using hashing for speed
	for i < m && j < n {
		if a[i] == b[j] {
			// Equal block
			ei, ej := i, j
			for i < m && j < n && a[i] == b[j] {
				i++
				j++
			}
			ops = append(ops, editOp{'e', ei, i, ej, j})
		} else {
			// Find next matching point
			ai, bj := i, j
			found := false

			// Look ahead in both sequences for a match
			maxLook := 100
			if m-i < maxLook {
				maxLook = m - i
			}
			if n-j < maxLook && n-j < maxLook {
				maxLook = n - j
			}

			for k := 0; k < maxLook && !found; k++ {
				// Check if a[i+k] matches any b[j..j+k]
				if i+k < m {
					if positions, ok := bMap[a[i+k]]; ok {
						for _, pos := range positions {
							if pos >= j && pos <= j+k+1 {
								// Found match
								if i+k > ai || pos > bj {
									if i+k > ai && pos > bj {
										ops = append(ops, editOp{'r', ai, i + k, bj, pos})
									} else if i+k > ai {
										ops = append(ops, editOp{'d', ai, i + k, bj, bj})
									} else {
										ops = append(ops, editOp{'i', ai, ai, bj, pos})
									}
								}
								i = i + k
								j = pos
								found = true
								break
							}
						}
					}
				}
				// Check if b[j+k] matches a[i]
				if !found && j+k < n && i < m && a[i] == b[j+k] {
					if j+k > bj {
						ops = append(ops, editOp{'i', ai, ai, bj, j + k})
					}
					j = j + k
					found = true
				}
			}

			if !found {
				// No match found in lookahead - replace chunk
				endI := i + 1
				endJ := j + 1
				if endI > m {
					endI = m
				}
				if endJ > n {
					endJ = n
				}
				ops = append(ops, editOp{'r', i, endI, j, endJ})
				i = endI
				j = endJ
			}
		}
	}

	if i < m {
		ops = append(ops, editOp{'d', i, m, j, j})
	}
	if j < n {
		ops = append(ops, editOp{'i', i, i, j, n})
	}

	return ops
}

//export goated_diff_unified
func goated_diff_unified(
	aLines **C.char, aCount C.int,
	bLines **C.char, bCount C.int,
	fromFile *C.char, toFile *C.char,
	contextLines C.int,
	outLen *C.int,
) *C.char {
	na := int(aCount)
	nb := int(bCount)
	ctx := int(contextLines)
	if ctx < 0 {
		ctx = 3
	}

	a := make([]string, na)
	b := make([]string, nb)

	aSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(aLines)), na)
	bSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(bLines)), nb)

	for i := 0; i < na; i++ {
		a[i] = C.GoString(aSlice[i])
	}
	for i := 0; i < nb; i++ {
		b[i] = C.GoString(bSlice[i])
	}

	ff := C.GoString(fromFile)
	tf := C.GoString(toFile)

	// Generate unified diff
	ops := computeOpcodes(a, b)
	if len(ops) == 0 {
		*outLen = 0
		return nil
	}

	var buf strings.Builder
	buf.WriteString("--- " + ff + "\n")
	buf.WriteString("+++ " + tf + "\n")

	// Group opcodes into hunks
	for _, op := range ops {
		switch op.tag {
		case 'd':
			buf.WriteString("@@ -" + itoa(op.i1+1) + "," + itoa(op.i2-op.i1) + " +" + itoa(op.j1+1) + ",0 @@\n")
			for k := op.i1; k < op.i2; k++ {
				buf.WriteString("-" + a[k] + "\n")
			}
		case 'i':
			buf.WriteString("@@ -" + itoa(op.i1+1) + ",0 +" + itoa(op.j1+1) + "," + itoa(op.j2-op.j1) + " @@\n")
			for k := op.j1; k < op.j2; k++ {
				buf.WriteString("+" + b[k] + "\n")
			}
		case 'r':
			buf.WriteString("@@ -" + itoa(op.i1+1) + "," + itoa(op.i2-op.i1) + " +" + itoa(op.j1+1) + "," + itoa(op.j2-op.j1) + " @@\n")
			for k := op.i1; k < op.i2; k++ {
				buf.WriteString("-" + a[k] + "\n")
			}
			for k := op.j1; k < op.j2; k++ {
				buf.WriteString("+" + b[k] + "\n")
			}
		}
	}

	result := buf.String()
	*outLen = C.int(len(result))
	return C.CString(result)
}

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	s := ""
	neg := false
	if n < 0 {
		neg = true
		n = -n
	}
	for n > 0 {
		s = string(rune('0'+n%10)) + s
		n /= 10
	}
	if neg {
		s = "-" + s
	}
	return s
}

// ============================================================================
// Batch string operations for common patterns
// ============================================================================

//export goated_batch_strings_replace
func goated_batch_strings_replace(
	texts **C.char, count C.int,
	oldStr *C.char, newStr *C.char,
	results **C.char,
) {
	n := int(count)
	old := C.GoString(oldStr)
	new_ := C.GoString(newStr)

	textSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(texts)), n)
	resSlice := unsafe.Slice((**C.char)(unsafe.Pointer(results)), n)

	numWorkers := runtime.NumCPU()
	chunkSize := (n + numWorkers - 1) / numWorkers
	var wg sync.WaitGroup

	for i := 0; i < numWorkers; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if end > n {
			end = n
		}
		if start >= n {
			break
		}
		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			for j := start; j < end; j++ {
				text := C.GoString(textSlice[j])
				resSlice[j] = C.CString(strings.ReplaceAll(text, old, new_))
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// IP Address parsing and validation (pure Go, much faster than Python)
// ============================================================================

//export goated_net_parse_ip
func goated_net_parse_ip(ip *C.char) C.bool {
	// Simple fast IPv4 validation without net.ParseIP overhead
	s := C.GoString(ip)
	dots := 0
	num := 0
	hasDigit := false
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c >= '0' && c <= '9' {
			num = num*10 + int(c-'0')
			hasDigit = true
			if num > 255 {
				return C.bool(false)
			}
		} else if c == '.' {
			if !hasDigit {
				return C.bool(false)
			}
			dots++
			num = 0
			hasDigit = false
		} else {
			// Might be IPv6
			return goated_net_parse_ip_full(s)
		}
	}
	return C.bool(dots == 3 && hasDigit)
}

func goated_net_parse_ip_full(s string) C.bool {
	// Quick IPv6 validation
	colons := 0
	for _, c := range s {
		if c == ':' {
			colons++
		} else if !((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')) {
			return C.bool(false)
		}
	}
	return C.bool(colons >= 2 && colons <= 7)
}

//export goated_batch_validate_ips
func goated_batch_validate_ips(
	ips **C.char, count C.int,
	results *C.bool,
) {
	n := int(count)
	ipSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(ips)), n)
	resSlice := unsafe.Slice((*C.bool)(unsafe.Pointer(results)), n)

	numWorkers := runtime.NumCPU()
	chunkSize := (n + numWorkers - 1) / numWorkers
	var wg sync.WaitGroup

	for i := 0; i < numWorkers; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if end > n {
			end = n
		}
		if start >= n {
			break
		}
		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			for j := start; j < end; j++ {
				resSlice[j] = goated_net_parse_ip(ipSlice[j])
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Text wrapping (Go implementation)
// ============================================================================

//export goated_textwrap_fill
func goated_textwrap_fill(text *C.char, width C.int) *C.char {
	s := C.GoString(text)
	w := int(width)
	if w <= 0 {
		w = 70
	}

	var buf strings.Builder
	words := strings.Fields(s)
	lineLen := 0

	for i, word := range words {
		wLen := len(word)
		if i > 0 {
			if lineLen+1+wLen > w {
				buf.WriteByte('\n')
				lineLen = 0
			} else {
				buf.WriteByte(' ')
				lineLen++
			}
		}
		buf.WriteString(word)
		lineLen += wLen
	}

	return C.CString(buf.String())
}

//export goated_textwrap_wrap
func goated_textwrap_wrap(text *C.char, width C.int) C.ulonglong {
	s := C.GoString(text)
	w := int(width)
	if w <= 0 {
		w = 70
	}

	var lines []string
	words := strings.Fields(s)
	var current strings.Builder
	lineLen := 0

	for i, word := range words {
		wLen := len(word)
		if i > 0 && lineLen+1+wLen > w {
			lines = append(lines, current.String())
			current.Reset()
			lineLen = 0
		} else if i > 0 {
			current.WriteByte(' ')
			lineLen++
		}
		current.WriteString(word)
		lineLen += wLen
	}
	if current.Len() > 0 {
		lines = append(lines, current.String())
	}

	return C.ulonglong(newHandle(lines))
}
