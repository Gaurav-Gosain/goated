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
	"unsafe"
)

//export goated_crypto_sha256_Sum
func goated_crypto_sha256_Sum(data *C.char, dataLen C.longlong, outLen *C.longlong) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), C.int(dataLen))
	hash := sha256.Sum256(input)
	*outLen = C.longlong(len(hash))
	return (*C.char)(C.CBytes(hash[:]))
}

//export goated_crypto_sha256_SumHex
func goated_crypto_sha256_SumHex(data *C.char, dataLen C.longlong) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), C.int(dataLen))
	hash := sha256.Sum256(input)
	return C.CString(hex.EncodeToString(hash[:]))
}

//export goated_crypto_sha512_Sum
func goated_crypto_sha512_Sum(data *C.char, dataLen C.longlong, outLen *C.longlong) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), C.int(dataLen))
	hash := sha512.Sum512(input)
	*outLen = C.longlong(len(hash))
	return (*C.char)(C.CBytes(hash[:]))
}

//export goated_crypto_sha512_SumHex
func goated_crypto_sha512_SumHex(data *C.char, dataLen C.longlong) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), C.int(dataLen))
	hash := sha512.Sum512(input)
	return C.CString(hex.EncodeToString(hash[:]))
}

//export goated_crypto_sha1_Sum
func goated_crypto_sha1_Sum(data *C.char, dataLen C.longlong, outLen *C.longlong) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), C.int(dataLen))
	hash := sha1.Sum(input)
	*outLen = C.longlong(len(hash))
	return (*C.char)(C.CBytes(hash[:]))
}

//export goated_crypto_sha1_SumHex
func goated_crypto_sha1_SumHex(data *C.char, dataLen C.longlong) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), C.int(dataLen))
	hash := sha1.Sum(input)
	return C.CString(hex.EncodeToString(hash[:]))
}

//export goated_crypto_md5_Sum
func goated_crypto_md5_Sum(data *C.char, dataLen C.longlong, outLen *C.longlong) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), C.int(dataLen))
	hash := md5.Sum(input)
	*outLen = C.longlong(len(hash))
	return (*C.char)(C.CBytes(hash[:]))
}

//export goated_crypto_md5_SumHex
func goated_crypto_md5_SumHex(data *C.char, dataLen C.longlong) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), C.int(dataLen))
	hash := md5.Sum(input)
	return C.CString(hex.EncodeToString(hash[:]))
}
