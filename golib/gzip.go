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
	"io"
	"unsafe"
)

//export goated_gzip_compress
func goated_gzip_compress(data *C.char, dataLen C.int, level C.int, outLen *C.int) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), dataLen)
	var buf bytes.Buffer
	w, err := gzip.NewWriterLevel(&buf, int(level))
	if err != nil {
		*outLen = 0
		return nil
	}
	_, err = w.Write(input)
	if err != nil {
		*outLen = 0
		return nil
	}
	err = w.Close()
	if err != nil {
		*outLen = 0
		return nil
	}
	result := buf.Bytes()
	*outLen = C.int(len(result))
	return (*C.char)(C.CBytes(result))
}

//export goated_gzip_decompress
func goated_gzip_decompress(data *C.char, dataLen C.int, outLen *C.int, errOut **C.char) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), dataLen)
	r, err := gzip.NewReader(bytes.NewReader(input))
	if err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}
	defer r.Close()
	result, err := io.ReadAll(r)
	if err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}
	*errOut = nil
	*outLen = C.int(len(result))
	return (*C.char)(C.CBytes(result))
}
