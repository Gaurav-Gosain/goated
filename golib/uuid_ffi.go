package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"crypto/rand"
	"fmt"
	"runtime"
	"sync"
	"unsafe"
)

//export goated_uuid4
func goated_uuid4() *C.char {
	var uuid [16]byte
	rand.Read(uuid[:])
	uuid[6] = (uuid[6] & 0x0f) | 0x40 // version 4
	uuid[8] = (uuid[8] & 0x3f) | 0x80 // variant 10
	s := fmt.Sprintf("%08x-%04x-%04x-%04x-%012x",
		uuid[0:4], uuid[4:6], uuid[6:8], uuid[8:10], uuid[10:16])
	return C.CString(s)
}

//export goated_batch_uuid4
func goated_batch_uuid4(count C.int, results **C.char) {
	n := int(count)
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
				var uuid [16]byte
				rand.Read(uuid[:])
				uuid[6] = (uuid[6] & 0x0f) | 0x40
				uuid[8] = (uuid[8] & 0x3f) | 0x80
				s := fmt.Sprintf("%08x-%04x-%04x-%04x-%012x",
					uuid[0:4], uuid[4:6], uuid[6:8], uuid[8:10], uuid[10:16])
				resSlice[j] = C.CString(s)
			}
		}(start, end)
	}
	wg.Wait()
}
