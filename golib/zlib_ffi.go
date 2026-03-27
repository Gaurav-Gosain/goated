package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"bytes"
	"compress/zlib"
	"hash/adler32"
	"hash/crc32"
	"io"
	"unsafe"
)

//export goated_zlib_compress
func goated_zlib_compress(data *C.char, dataLen C.int, level C.int, outLen *C.int) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), dataLen)
	var buf bytes.Buffer
	w, err := zlib.NewWriterLevel(&buf, int(level))
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

//export goated_zlib_decompress
func goated_zlib_decompress(data *C.char, dataLen C.int, outLen *C.int, errOut **C.char) *C.char {
	input := C.GoBytes(unsafe.Pointer(data), dataLen)
	r, err := zlib.NewReader(bytes.NewReader(input))
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

//export goated_crc32_checksum
func goated_crc32_checksum(data *C.char, dataLen C.int) C.uint {
	input := C.GoBytes(unsafe.Pointer(data), dataLen)
	return C.uint(crc32.ChecksumIEEE(input))
}

//export goated_adler32_checksum
func goated_adler32_checksum(data *C.char, dataLen C.int) C.uint {
	input := C.GoBytes(unsafe.Pointer(data), dataLen)
	return C.uint(adler32.Checksum(input))
}
