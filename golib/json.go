package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"encoding/json"
)

//export goated_json_Marshal
func goated_json_Marshal(handle C.ulonglong, outLen *C.longlong, errOut **C.char) *C.char {
	obj, ok := getAny(uint64(handle))
	if !ok {
		*errOut = C.CString("invalid handle")
		*outLen = 0
		return nil
	}

	result, err := json.Marshal(obj)
	if err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}

	*errOut = nil
	*outLen = C.longlong(len(result))
	return C.CString(string(result))
}

//export goated_json_MarshalIndent
func goated_json_MarshalIndent(handle C.ulonglong, prefix *C.char, indent *C.char, outLen *C.longlong, errOut **C.char) *C.char {
	obj, ok := getAny(uint64(handle))
	if !ok {
		*errOut = C.CString("invalid handle")
		*outLen = 0
		return nil
	}

	result, err := json.MarshalIndent(obj, C.GoString(prefix), C.GoString(indent))
	if err != nil {
		*errOut = C.CString(err.Error())
		*outLen = 0
		return nil
	}

	*errOut = nil
	*outLen = C.longlong(len(result))
	return C.CString(string(result))
}

//export goated_json_Unmarshal
func goated_json_Unmarshal(data *C.char, dataLen C.longlong, errOut **C.char) C.ulonglong {
	var result interface{}
	err := json.Unmarshal([]byte(C.GoStringN(data, C.int(dataLen))), &result)
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}

	*errOut = nil
	return C.ulonglong(newHandle(result))
}

//export goated_json_Valid
func goated_json_Valid(data *C.char, dataLen C.longlong) C.bool {
	return C.bool(json.Valid([]byte(C.GoStringN(data, C.int(dataLen)))))
}

//export goated_json_Compact
func goated_json_Compact(data *C.char, dataLen C.longlong, outLen *C.longlong, errOut **C.char) *C.char {
	src := []byte(C.GoStringN(data, C.int(dataLen)))
	var dst []byte
	dst = make([]byte, 0, len(src))

	// Use json.Compact
	var buf = new(struct {
		data []byte
	})
	buf.data = make([]byte, 0, len(src))

	// Simple approach: unmarshal and marshal without indent
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

	dst = result
	*errOut = nil
	*outLen = C.longlong(len(dst))
	return C.CString(string(dst))
}

//export goated_json_GetString
func goated_json_GetString(handle C.ulonglong, key *C.char, errOut **C.char) *C.char {
	obj, ok := getAny(uint64(handle))
	if !ok {
		*errOut = C.CString("invalid handle")
		return nil
	}

	m, ok := obj.(map[string]interface{})
	if !ok {
		*errOut = C.CString("not an object")
		return nil
	}

	val, ok := m[C.GoString(key)]
	if !ok {
		*errOut = C.CString("key not found")
		return nil
	}

	str, ok := val.(string)
	if !ok {
		*errOut = C.CString("value is not a string")
		return nil
	}

	*errOut = nil
	return C.CString(str)
}

//export goated_json_GetNumber
func goated_json_GetNumber(handle C.ulonglong, key *C.char, errOut **C.char) C.double {
	obj, ok := getAny(uint64(handle))
	if !ok {
		*errOut = C.CString("invalid handle")
		return 0
	}

	m, ok := obj.(map[string]interface{})
	if !ok {
		*errOut = C.CString("not an object")
		return 0
	}

	val, ok := m[C.GoString(key)]
	if !ok {
		*errOut = C.CString("key not found")
		return 0
	}

	num, ok := val.(float64)
	if !ok {
		*errOut = C.CString("value is not a number")
		return 0
	}

	*errOut = nil
	return C.double(num)
}

//export goated_json_GetBool
func goated_json_GetBool(handle C.ulonglong, key *C.char, errOut **C.char) C.bool {
	obj, ok := getAny(uint64(handle))
	if !ok {
		*errOut = C.CString("invalid handle")
		return false
	}

	m, ok := obj.(map[string]interface{})
	if !ok {
		*errOut = C.CString("not an object")
		return false
	}

	val, ok := m[C.GoString(key)]
	if !ok {
		*errOut = C.CString("key not found")
		return false
	}

	b, ok := val.(bool)
	if !ok {
		*errOut = C.CString("value is not a bool")
		return false
	}

	*errOut = nil
	return C.bool(b)
}
