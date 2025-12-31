package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"bytes"
	"unsafe"
)

//export goated_bytes_Contains
func goated_bytes_Contains(s *C.char, sLen C.longlong, substr *C.char, substrLen C.longlong) C.bool {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	substrBytes := C.GoBytes(unsafe.Pointer(substr), C.int(substrLen))
	return C.bool(bytes.Contains(sBytes, substrBytes))
}

//export goated_bytes_Count
func goated_bytes_Count(s *C.char, sLen C.longlong, sep *C.char, sepLen C.longlong) C.longlong {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	sepBytes := C.GoBytes(unsafe.Pointer(sep), C.int(sepLen))
	return C.longlong(bytes.Count(sBytes, sepBytes))
}

//export goated_bytes_HasPrefix
func goated_bytes_HasPrefix(s *C.char, sLen C.longlong, prefix *C.char, prefixLen C.longlong) C.bool {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	prefixBytes := C.GoBytes(unsafe.Pointer(prefix), C.int(prefixLen))
	return C.bool(bytes.HasPrefix(sBytes, prefixBytes))
}

//export goated_bytes_HasSuffix
func goated_bytes_HasSuffix(s *C.char, sLen C.longlong, suffix *C.char, suffixLen C.longlong) C.bool {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	suffixBytes := C.GoBytes(unsafe.Pointer(suffix), C.int(suffixLen))
	return C.bool(bytes.HasSuffix(sBytes, suffixBytes))
}

//export goated_bytes_Index
func goated_bytes_Index(s *C.char, sLen C.longlong, sep *C.char, sepLen C.longlong) C.longlong {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	sepBytes := C.GoBytes(unsafe.Pointer(sep), C.int(sepLen))
	return C.longlong(bytes.Index(sBytes, sepBytes))
}

//export goated_bytes_LastIndex
func goated_bytes_LastIndex(s *C.char, sLen C.longlong, sep *C.char, sepLen C.longlong) C.longlong {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	sepBytes := C.GoBytes(unsafe.Pointer(sep), C.int(sepLen))
	return C.longlong(bytes.LastIndex(sBytes, sepBytes))
}

//export goated_bytes_Equal
func goated_bytes_Equal(a *C.char, aLen C.longlong, b *C.char, bLen C.longlong) C.bool {
	aBytes := C.GoBytes(unsafe.Pointer(a), C.int(aLen))
	bBytes := C.GoBytes(unsafe.Pointer(b), C.int(bLen))
	return C.bool(bytes.Equal(aBytes, bBytes))
}

//export goated_bytes_Compare
func goated_bytes_Compare(a *C.char, aLen C.longlong, b *C.char, bLen C.longlong) C.int {
	aBytes := C.GoBytes(unsafe.Pointer(a), C.int(aLen))
	bBytes := C.GoBytes(unsafe.Pointer(b), C.int(bLen))
	return C.int(bytes.Compare(aBytes, bBytes))
}

//export goated_bytes_ToLower
func goated_bytes_ToLower(s *C.char, sLen C.longlong, outLen *C.longlong) *C.char {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	result := bytes.ToLower(sBytes)
	*outLen = C.longlong(len(result))
	return (*C.char)(C.CBytes(result))
}

//export goated_bytes_ToUpper
func goated_bytes_ToUpper(s *C.char, sLen C.longlong, outLen *C.longlong) *C.char {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	result := bytes.ToUpper(sBytes)
	*outLen = C.longlong(len(result))
	return (*C.char)(C.CBytes(result))
}

//export goated_bytes_TrimSpace
func goated_bytes_TrimSpace(s *C.char, sLen C.longlong, outLen *C.longlong) *C.char {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	result := bytes.TrimSpace(sBytes)
	*outLen = C.longlong(len(result))
	return (*C.char)(C.CBytes(result))
}

//export goated_bytes_Repeat
func goated_bytes_Repeat(s *C.char, sLen C.longlong, count C.longlong, outLen *C.longlong) *C.char {
	if count < 0 {
		*outLen = 0
		return nil
	}
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	result := bytes.Repeat(sBytes, int(count))
	*outLen = C.longlong(len(result))
	return (*C.char)(C.CBytes(result))
}

//export goated_bytes_Replace
func goated_bytes_Replace(s *C.char, sLen C.longlong, old *C.char, oldLen C.longlong, new *C.char, newLen C.longlong, n C.longlong, outLen *C.longlong) *C.char {
	sBytes := C.GoBytes(unsafe.Pointer(s), C.int(sLen))
	oldBytes := C.GoBytes(unsafe.Pointer(old), C.int(oldLen))
	newBytes := C.GoBytes(unsafe.Pointer(new), C.int(newLen))
	result := bytes.Replace(sBytes, oldBytes, newBytes, int(n))
	*outLen = C.longlong(len(result))
	return (*C.char)(C.CBytes(result))
}

//export goated_free_bytes
func goated_free_bytes(b *C.char) {
	if b != nil {
		C.free(unsafe.Pointer(b))
	}
}
