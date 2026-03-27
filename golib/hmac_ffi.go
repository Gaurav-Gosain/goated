package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"crypto/hmac"
	"crypto/sha1"
	"crypto/sha256"
	"crypto/sha512"
	"encoding/hex"
	"unsafe"
)

//export goated_hmac_sha256
func goated_hmac_sha256(key *C.char, keyLen C.int, msg *C.char, msgLen C.int) *C.char {
	k := C.GoBytes(unsafe.Pointer(key), keyLen)
	m := C.GoBytes(unsafe.Pointer(msg), msgLen)
	mac := hmac.New(sha256.New, k)
	mac.Write(m)
	return C.CString(hex.EncodeToString(mac.Sum(nil)))
}

//export goated_hmac_sha512
func goated_hmac_sha512(key *C.char, keyLen C.int, msg *C.char, msgLen C.int) *C.char {
	k := C.GoBytes(unsafe.Pointer(key), keyLen)
	m := C.GoBytes(unsafe.Pointer(msg), msgLen)
	mac := hmac.New(sha512.New, k)
	mac.Write(m)
	return C.CString(hex.EncodeToString(mac.Sum(nil)))
}

//export goated_hmac_sha1
func goated_hmac_sha1(key *C.char, keyLen C.int, msg *C.char, msgLen C.int) *C.char {
	k := C.GoBytes(unsafe.Pointer(key), keyLen)
	m := C.GoBytes(unsafe.Pointer(msg), msgLen)
	mac := hmac.New(sha1.New, k)
	mac.Write(m)
	return C.CString(hex.EncodeToString(mac.Sum(nil)))
}
