package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"bytes"
	"encoding/json"
)

//export goated_json_marshal_string
func goated_json_marshal_string(jsonStr *C.char, jsonLen C.int, outLen *C.int, errOut **C.char) *C.char {
	src := []byte(C.GoStringN(jsonStr, jsonLen))

	// Validate and compact the JSON
	var buf bytes.Buffer
	if err := json.Compact(&buf, src); err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}

	result := buf.Bytes()
	*errOut = nil
	*outLen = C.int(len(result))
	return C.CString(string(result))
}

//export goated_json_unmarshal_string
func goated_json_unmarshal_string(data *C.char, dataLen C.int, outLen *C.int, errOut **C.char) *C.char {
	src := []byte(C.GoStringN(data, dataLen))

	// Validate by unmarshalling, then re-serialize compact
	var v interface{}
	if err := json.Unmarshal(src, &v); err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}

	result, err := json.Marshal(v)
	if err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}

	*errOut = nil
	*outLen = C.int(len(result))
	return C.CString(string(result))
}
