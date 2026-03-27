package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"path/filepath"
	"runtime"
	"sync"
	"unsafe"
)

//export goated_fnmatch
func goated_fnmatch(pattern *C.char, name *C.char) C.bool {
	matched, _ := filepath.Match(C.GoString(pattern), C.GoString(name))
	return C.bool(matched)
}

//export goated_batch_fnmatch
func goated_batch_fnmatch(
	pattern *C.char,
	names **C.char, count C.int,
	results *C.bool,
) {
	pat := C.GoString(pattern)
	n := int(count)
	nameSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(names)), n)
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
				matched, _ := filepath.Match(pat, C.GoString(nameSlice[j]))
				resSlice[j] = C.bool(matched)
			}
		}(start, end)
	}
	wg.Wait()
}

//export goated_fnmatch_filter
func goated_fnmatch_filter(
	names **C.char, count C.int,
	pattern *C.char,
) C.ulonglong {
	pat := C.GoString(pattern)
	n := int(count)
	nameSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(names)), n)

	var matches []string
	for j := 0; j < n; j++ {
		name := C.GoString(nameSlice[j])
		if matched, _ := filepath.Match(pat, name); matched {
			matches = append(matches, name)
		}
	}
	return C.ulonglong(newHandle(matches))
}
