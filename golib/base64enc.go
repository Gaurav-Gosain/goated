package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"encoding/base64"
	"unsafe"
)

//export goated_base64_std_encode
func goated_base64_std_encode(data *C.char, dataLen C.int) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), dataLen)
	return C.CString(base64.StdEncoding.EncodeToString(input))
}

//export goated_base64_std_decode
func goated_base64_std_decode(data *C.char, outLen *C.int, errOut **C.char) *C.char {
	result, err := base64.StdEncoding.DecodeString(C.GoString(data))
	if err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}
	*errOut = nil
	*outLen = C.int(len(result))
	return (*C.char)(C.CBytes(result))
}

//export goated_base64_url_encode
func goated_base64_url_encode(data *C.char, dataLen C.int) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), dataLen)
	return C.CString(base64.URLEncoding.EncodeToString(input))
}

//export goated_base64_url_decode
func goated_base64_url_decode(data *C.char, outLen *C.int, errOut **C.char) *C.char {
	result, err := base64.URLEncoding.DecodeString(C.GoString(data))
	if err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}
	*errOut = nil
	*outLen = C.int(len(result))
	return (*C.char)(C.CBytes(result))
}
