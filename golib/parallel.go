package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"crypto/md5"
	"crypto/sha1"
	"crypto/sha256"
	"crypto/sha512"
	"encoding/hex"
	"runtime"
	"strings"
	"sync"
	"unsafe"
)

// Batch string operations using goroutines

//export goated_parallel_strings_contains_batch
func goated_parallel_strings_contains_batch(
	texts **C.char, textCount C.int,
	substr *C.char,
	results *C.bool,
) {
	goSubstr := C.GoString(substr)
	count := int(textCount)

	var wg sync.WaitGroup
	resultSlice := (*[1 << 30]C.bool)(unsafe.Pointer(results))[:count:count]
	textSlice := (*[1 << 30]*C.char)(unsafe.Pointer(texts))[:count:count]

	numWorkers := runtime.NumCPU()
	chunkSize := (count + numWorkers - 1) / numWorkers

	for i := 0; i < numWorkers; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if end > count {
			end = count
		}
		if start >= count {
			break
		}

		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			for j := start; j < end; j++ {
				text := C.GoString(textSlice[j])
				resultSlice[j] = C.bool(strings.Contains(text, goSubstr))
			}
		}(start, end)
	}
	wg.Wait()
}

//export goated_parallel_strings_toupper_batch
func goated_parallel_strings_toupper_batch(
	texts **C.char, textCount C.int,
	results **C.char,
) {
	count := int(textCount)

	var wg sync.WaitGroup
	resultSlice := (*[1 << 30]*C.char)(unsafe.Pointer(results))[:count:count]
	textSlice := (*[1 << 30]*C.char)(unsafe.Pointer(texts))[:count:count]

	numWorkers := runtime.NumCPU()
	chunkSize := (count + numWorkers - 1) / numWorkers

	for i := 0; i < numWorkers; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if end > count {
			end = count
		}
		if start >= count {
			break
		}

		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			for j := start; j < end; j++ {
				text := C.GoString(textSlice[j])
				resultSlice[j] = C.CString(strings.ToUpper(text))
			}
		}(start, end)
	}
	wg.Wait()
}

// Batch hashing - this is where goroutines really shine

//export goated_parallel_hash_md5_batch
func goated_parallel_hash_md5_batch(
	data **C.char, dataLens *C.int, count C.int,
	results **C.char,
) {
	n := int(count)

	var wg sync.WaitGroup
	resultSlice := (*[1 << 30]*C.char)(unsafe.Pointer(results))[:n:n]
	dataSlice := (*[1 << 30]*C.char)(unsafe.Pointer(data))[:n:n]
	lenSlice := (*[1 << 30]C.int)(unsafe.Pointer(dataLens))[:n:n]

	numWorkers := runtime.NumCPU()
	chunkSize := (n + numWorkers - 1) / numWorkers

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
				bytes := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				hash := md5.Sum(bytes)
				hexStr := hex.EncodeToString(hash[:])
				resultSlice[j] = C.CString(hexStr)
			}
		}(start, end)
	}
	wg.Wait()
}

//export goated_parallel_hash_sha256_batch
func goated_parallel_hash_sha256_batch(
	data **C.char, dataLens *C.int, count C.int,
	results **C.char,
) {
	n := int(count)

	var wg sync.WaitGroup
	resultSlice := (*[1 << 30]*C.char)(unsafe.Pointer(results))[:n:n]
	dataSlice := (*[1 << 30]*C.char)(unsafe.Pointer(data))[:n:n]
	lenSlice := (*[1 << 30]C.int)(unsafe.Pointer(dataLens))[:n:n]

	numWorkers := runtime.NumCPU()
	chunkSize := (n + numWorkers - 1) / numWorkers

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
				bytes := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				hash := sha256.Sum256(bytes)
				hexStr := hex.EncodeToString(hash[:])
				resultSlice[j] = C.CString(hexStr)
			}
		}(start, end)
	}
	wg.Wait()
}

//export goated_parallel_hash_sha512_batch
func goated_parallel_hash_sha512_batch(
	data **C.char, dataLens *C.int, count C.int,
	results **C.char,
) {
	n := int(count)

	var wg sync.WaitGroup
	resultSlice := (*[1 << 30]*C.char)(unsafe.Pointer(results))[:n:n]
	dataSlice := (*[1 << 30]*C.char)(unsafe.Pointer(data))[:n:n]
	lenSlice := (*[1 << 30]C.int)(unsafe.Pointer(dataLens))[:n:n]

	numWorkers := runtime.NumCPU()
	chunkSize := (n + numWorkers - 1) / numWorkers

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
				bytes := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				hash := sha512.Sum512(bytes)
				hexStr := hex.EncodeToString(hash[:])
				resultSlice[j] = C.CString(hexStr)
			}
		}(start, end)
	}
	wg.Wait()
}

//export goated_parallel_hash_sha1_batch
func goated_parallel_hash_sha1_batch(
	data **C.char, dataLens *C.int, count C.int,
	results **C.char,
) {
	n := int(count)

	var wg sync.WaitGroup
	resultSlice := (*[1 << 30]*C.char)(unsafe.Pointer(results))[:n:n]
	dataSlice := (*[1 << 30]*C.char)(unsafe.Pointer(data))[:n:n]
	lenSlice := (*[1 << 30]C.int)(unsafe.Pointer(dataLens))[:n:n]

	numWorkers := runtime.NumCPU()
	chunkSize := (n + numWorkers - 1) / numWorkers

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
				bytes := C.GoBytes(unsafe.Pointer(dataSlice[j]), lenSlice[j])
				hash := sha1.Sum(bytes)
				hexStr := hex.EncodeToString(hash[:])
				resultSlice[j] = C.CString(hexStr)
			}
		}(start, end)
	}
	wg.Wait()
}

// Parallel map operation - apply a transform to each item

//export goated_parallel_map_toupper
func goated_parallel_map_toupper(
	items **C.char, count C.int,
	results **C.char,
) {
	goated_parallel_strings_toupper_batch(items, count, results)
}

//export goated_parallel_map_tolower
func goated_parallel_map_tolower(
	items **C.char, count C.int,
	results **C.char,
) {
	n := int(count)

	var wg sync.WaitGroup
	resultSlice := (*[1 << 30]*C.char)(unsafe.Pointer(results))[:n:n]
	itemSlice := (*[1 << 30]*C.char)(unsafe.Pointer(items))[:n:n]

	numWorkers := runtime.NumCPU()
	chunkSize := (n + numWorkers - 1) / numWorkers

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
				text := C.GoString(itemSlice[j])
				resultSlice[j] = C.CString(strings.ToLower(text))
			}
		}(start, end)
	}
	wg.Wait()
}

// Get number of CPUs for Python to know parallelism level
//
//export goated_parallel_num_cpu
func goated_parallel_num_cpu() C.int {
	return C.int(runtime.NumCPU())
}

// Free batch results
//
//export goated_parallel_free_strings
func goated_parallel_free_strings(results **C.char, count C.int) {
	n := int(count)
	resultSlice := (*[1 << 30]*C.char)(unsafe.Pointer(results))[:n:n]
	for i := 0; i < n; i++ {
		if resultSlice[i] != nil {
			C.free(unsafe.Pointer(resultSlice[i]))
		}
	}
}
