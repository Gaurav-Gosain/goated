package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"bytes"
	"compress/gzip"
	"crypto/sha256"
	"encoding/base64"
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"io"
	"regexp"
	"runtime"
	"strings"
	"sync"
	"unsafe"
)

// ============================================================================
// Batch Gzip Compress - compress N items in parallel with goroutines
// ============================================================================

//export goated_batch_gzip_compress
func goated_batch_gzip_compress(
	data **C.char, dataLens *C.int, count C.int, level C.int,
	results **C.char, resultLens *C.int,
) {
	n := int(count)
	lev := int(level)
	dataSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(data)), n)
	lenSlice := unsafe.Slice((*C.int)(unsafe.Pointer(dataLens)), n)
	resSlice := unsafe.Slice((**C.char)(unsafe.Pointer(results)), n)
	resLenSlice := unsafe.Slice((*C.int)(unsafe.Pointer(resultLens)), n)

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
				input := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				var buf bytes.Buffer
				w, err := gzip.NewWriterLevel(&buf, lev)
				if err != nil {
					resSlice[j] = nil
					resLenSlice[j] = 0
					continue
				}
				w.Write(input)
				w.Close()
				out := buf.Bytes()
				resSlice[j] = (*C.char)(C.CBytes(out))
				resLenSlice[j] = C.int(len(out))
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Batch Gzip Decompress
// ============================================================================

//export goated_batch_gzip_decompress
func goated_batch_gzip_decompress(
	data **C.char, dataLens *C.int, count C.int,
	results **C.char, resultLens *C.int,
) {
	n := int(count)
	dataSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(data)), n)
	lenSlice := unsafe.Slice((*C.int)(unsafe.Pointer(dataLens)), n)
	resSlice := unsafe.Slice((**C.char)(unsafe.Pointer(results)), n)
	resLenSlice := unsafe.Slice((*C.int)(unsafe.Pointer(resultLens)), n)

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
				input := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				r, err := gzip.NewReader(bytes.NewReader(input))
				if err != nil {
					resSlice[j] = nil
					resLenSlice[j] = 0
					continue
				}
				out, err := io.ReadAll(r)
				r.Close()
				if err != nil {
					resSlice[j] = nil
					resLenSlice[j] = 0
					continue
				}
				resSlice[j] = (*C.char)(C.CBytes(out))
				resLenSlice[j] = C.int(len(out))
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Batch Base64 Encode
// ============================================================================

//export goated_batch_base64_encode
func goated_batch_base64_encode(
	data **C.char, dataLens *C.int, count C.int,
	results **C.char,
) {
	n := int(count)
	dataSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(data)), n)
	lenSlice := unsafe.Slice((*C.int)(unsafe.Pointer(dataLens)), n)
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
				input := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				encoded := base64.StdEncoding.EncodeToString(input)
				resSlice[j] = C.CString(encoded)
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Batch Base64 Decode
// ============================================================================

//export goated_batch_base64_decode
func goated_batch_base64_decode(
	data **C.char, count C.int,
	results **C.char, resultLens *C.int,
) {
	n := int(count)
	dataSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(data)), n)
	resSlice := unsafe.Slice((**C.char)(unsafe.Pointer(results)), n)
	resLenSlice := unsafe.Slice((*C.int)(unsafe.Pointer(resultLens)), n)

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
				input := C.GoString(dataSlice[j])
				decoded, err := base64.StdEncoding.DecodeString(input)
				if err != nil {
					resSlice[j] = nil
					resLenSlice[j] = 0
					continue
				}
				resSlice[j] = (*C.char)(C.CBytes(decoded))
				resLenSlice[j] = C.int(len(decoded))
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Batch JSON Validate - validate N JSON strings in parallel
// ============================================================================

//export goated_batch_json_valid
func goated_batch_json_valid(
	data **C.char, dataLens *C.int, count C.int,
	results *C.bool,
) {
	n := int(count)
	dataSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(data)), n)
	lenSlice := unsafe.Slice((*C.int)(unsafe.Pointer(dataLens)), n)
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
				b := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				resSlice[j] = C.bool(json.Valid(b))
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Batch Regex Match - match N strings against compiled pattern in parallel
// ============================================================================

//export goated_batch_regexp_match
func goated_batch_regexp_match(
	patternHandle C.ulonglong,
	texts **C.char, count C.int,
	results *C.bool,
) {
	re, ok := getHandle[*regexp.Regexp](uint64(patternHandle))
	if !ok {
		return
	}

	n := int(count)
	textSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(texts)), n)
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
				text := C.GoString(textSlice[j])
				resSlice[j] = C.bool(re.MatchString(text))
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Batch Regex Find All - find all matches in N strings in parallel
// ============================================================================

//export goated_batch_regexp_find_all
func goated_batch_regexp_find_all(
	patternHandle C.ulonglong,
	texts **C.char, count C.int,
	results **C.char,
) {
	re, ok := getHandle[*regexp.Regexp](uint64(patternHandle))
	if !ok {
		return
	}

	n := int(count)
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
				matches := re.FindAllString(text, -1)
				// Join with \x00 separator for Python to split
				resSlice[j] = C.CString(strings.Join(matches, "\x00"))
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Pipeline: CSV Read + SHA256 each row (common ETL pattern)
// ============================================================================

//export goated_pipeline_csv_hash
func goated_pipeline_csv_hash(
	csvData *C.char, csvLen C.int,
	column C.int,
	results **C.char,
	errOut **C.char,
) C.int {
	input := C.GoStringN(csvData, C.int(csvLen))
	reader := csv.NewReader(strings.NewReader(input))
	records, err := reader.ReadAll()
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}

	n := len(records)
	col := int(column)
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
				if col < len(records[j]) {
					hash := sha256.Sum256([]byte(records[j][col]))
					resSlice[j] = C.CString(hex.EncodeToString(hash[:]))
				} else {
					resSlice[j] = C.CString("")
				}
			}
		}(start, end)
	}
	wg.Wait()
	*errOut = nil
	return C.int(n)
}

// ============================================================================
// Batch Multi-Hash: compute multiple hash algorithms on each item
// ============================================================================

//export goated_batch_multi_hash
func goated_batch_multi_hash(
	data **C.char, dataLens *C.int, count C.int,
	sha256Results **C.char,
) {
	n := int(count)
	dataSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(data)), n)
	lenSlice := unsafe.Slice((*C.int)(unsafe.Pointer(dataLens)), n)
	sha256Slice := unsafe.Slice((**C.char)(unsafe.Pointer(sha256Results)), n)

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
				b := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				h := sha256.Sum256(b)
				sha256Slice[j] = C.CString(hex.EncodeToString(h[:]))
			}
		}(start, end)
	}
	wg.Wait()
}

// ============================================================================
// Free batch binary results
// ============================================================================

//export goated_batch_free_buffers
func goated_batch_free_buffers(results **C.char, count C.int) {
	n := int(count)
	resSlice := unsafe.Slice((**C.char)(unsafe.Pointer(results)), n)
	for i := 0; i < n; i++ {
		if resSlice[i] != nil {
			C.free(unsafe.Pointer(resSlice[i]))
		}
	}
}
