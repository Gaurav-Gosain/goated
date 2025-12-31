package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"strings"
	"unsafe"
)

//export goated_strings_Contains
func goated_strings_Contains(s *C.char, substr *C.char) C.bool {
	return C.bool(strings.Contains(C.GoString(s), C.GoString(substr)))
}

//export goated_strings_ContainsAny
func goated_strings_ContainsAny(s *C.char, chars *C.char) C.bool {
	return C.bool(strings.ContainsAny(C.GoString(s), C.GoString(chars)))
}

//export goated_strings_Count
func goated_strings_Count(s *C.char, substr *C.char) C.longlong {
	return C.longlong(strings.Count(C.GoString(s), C.GoString(substr)))
}

//export goated_strings_EqualFold
func goated_strings_EqualFold(s *C.char, t *C.char) C.bool {
	return C.bool(strings.EqualFold(C.GoString(s), C.GoString(t)))
}

//export goated_strings_HasPrefix
func goated_strings_HasPrefix(s *C.char, prefix *C.char) C.bool {
	return C.bool(strings.HasPrefix(C.GoString(s), C.GoString(prefix)))
}

//export goated_strings_HasSuffix
func goated_strings_HasSuffix(s *C.char, suffix *C.char) C.bool {
	return C.bool(strings.HasSuffix(C.GoString(s), C.GoString(suffix)))
}

//export goated_strings_Index
func goated_strings_Index(s *C.char, substr *C.char) C.longlong {
	return C.longlong(strings.Index(C.GoString(s), C.GoString(substr)))
}

//export goated_strings_IndexAny
func goated_strings_IndexAny(s *C.char, chars *C.char) C.longlong {
	return C.longlong(strings.IndexAny(C.GoString(s), C.GoString(chars)))
}

//export goated_strings_IndexByte
func goated_strings_IndexByte(s *C.char, c C.char) C.longlong {
	return C.longlong(strings.IndexByte(C.GoString(s), byte(c)))
}

//export goated_strings_LastIndex
func goated_strings_LastIndex(s *C.char, substr *C.char) C.longlong {
	return C.longlong(strings.LastIndex(C.GoString(s), C.GoString(substr)))
}

//export goated_strings_LastIndexAny
func goated_strings_LastIndexAny(s *C.char, chars *C.char) C.longlong {
	return C.longlong(strings.LastIndexAny(C.GoString(s), C.GoString(chars)))
}

//export goated_strings_LastIndexByte
func goated_strings_LastIndexByte(s *C.char, c C.char) C.longlong {
	return C.longlong(strings.LastIndexByte(C.GoString(s), byte(c)))
}

//export goated_strings_Split
func goated_strings_Split(s *C.char, sep *C.char) C.ulonglong {
	result := strings.Split(C.GoString(s), C.GoString(sep))
	return C.ulonglong(newHandle(result))
}

//export goated_strings_SplitN
func goated_strings_SplitN(s *C.char, sep *C.char, n C.longlong) C.ulonglong {
	result := strings.SplitN(C.GoString(s), C.GoString(sep), int(n))
	return C.ulonglong(newHandle(result))
}

//export goated_strings_SplitAfter
func goated_strings_SplitAfter(s *C.char, sep *C.char) C.ulonglong {
	result := strings.SplitAfter(C.GoString(s), C.GoString(sep))
	return C.ulonglong(newHandle(result))
}

//export goated_strings_SplitAfterN
func goated_strings_SplitAfterN(s *C.char, sep *C.char, n C.longlong) C.ulonglong {
	result := strings.SplitAfterN(C.GoString(s), C.GoString(sep), int(n))
	return C.ulonglong(newHandle(result))
}

//export goated_strings_Fields
func goated_strings_Fields(s *C.char) C.ulonglong {
	result := strings.Fields(C.GoString(s))
	return C.ulonglong(newHandle(result))
}

//export goated_strings_Join
func goated_strings_Join(handle C.ulonglong, sep *C.char) *C.char {
	elems, ok := getStringSlice(uint64(handle))
	if !ok {
		return C.CString("")
	}
	return C.CString(strings.Join(elems, C.GoString(sep)))
}

//export goated_strings_Repeat
func goated_strings_Repeat(s *C.char, count C.longlong) *C.char {
	if count < 0 {
		return nil
	}
	return C.CString(strings.Repeat(C.GoString(s), int(count)))
}

//export goated_strings_Replace
func goated_strings_Replace(s *C.char, old *C.char, new *C.char, n C.longlong) *C.char {
	return C.CString(strings.Replace(C.GoString(s), C.GoString(old), C.GoString(new), int(n)))
}

//export goated_strings_ReplaceAll
func goated_strings_ReplaceAll(s *C.char, old *C.char, new *C.char) *C.char {
	return C.CString(strings.ReplaceAll(C.GoString(s), C.GoString(old), C.GoString(new)))
}

//export goated_strings_ToLower
func goated_strings_ToLower(s *C.char) *C.char {
	return C.CString(strings.ToLower(C.GoString(s)))
}

//export goated_strings_ToUpper
func goated_strings_ToUpper(s *C.char) *C.char {
	return C.CString(strings.ToUpper(C.GoString(s)))
}

//export goated_strings_ToTitle
func goated_strings_ToTitle(s *C.char) *C.char {
	return C.CString(strings.ToTitle(C.GoString(s)))
}

//export goated_strings_Title
func goated_strings_Title(s *C.char) *C.char {
	return C.CString(strings.Title(C.GoString(s)))
}

//export goated_strings_Trim
func goated_strings_Trim(s *C.char, cutset *C.char) *C.char {
	return C.CString(strings.Trim(C.GoString(s), C.GoString(cutset)))
}

//export goated_strings_TrimLeft
func goated_strings_TrimLeft(s *C.char, cutset *C.char) *C.char {
	return C.CString(strings.TrimLeft(C.GoString(s), C.GoString(cutset)))
}

//export goated_strings_TrimRight
func goated_strings_TrimRight(s *C.char, cutset *C.char) *C.char {
	return C.CString(strings.TrimRight(C.GoString(s), C.GoString(cutset)))
}

//export goated_strings_TrimSpace
func goated_strings_TrimSpace(s *C.char) *C.char {
	return C.CString(strings.TrimSpace(C.GoString(s)))
}

//export goated_strings_TrimPrefix
func goated_strings_TrimPrefix(s *C.char, prefix *C.char) *C.char {
	return C.CString(strings.TrimPrefix(C.GoString(s), C.GoString(prefix)))
}

//export goated_strings_TrimSuffix
func goated_strings_TrimSuffix(s *C.char, suffix *C.char) *C.char {
	return C.CString(strings.TrimSuffix(C.GoString(s), C.GoString(suffix)))
}

//export goated_slice_string_len
func goated_slice_string_len(handle C.ulonglong) C.longlong {
	slice, ok := getStringSlice(uint64(handle))
	if !ok {
		return 0
	}
	return C.longlong(len(slice))
}

//export goated_slice_string_get
func goated_slice_string_get(handle C.ulonglong, index C.longlong) *C.char {
	slice, ok := getStringSlice(uint64(handle))
	if !ok || int(index) >= len(slice) || index < 0 {
		return nil
	}
	return C.CString(slice[index])
}

//export goated_free_string
func goated_free_string(s *C.char) {
	if s != nil {
		C.free(unsafe.Pointer(s))
	}
}
