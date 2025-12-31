package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"path"
)


//export goated_path_Base
func goated_path_Base(path_ *C.char) *C.char {
	result := path.Base(C.GoString(path_))
	return C.CString(result)
}

//export goated_path_Clean
func goated_path_Clean(path_ *C.char) *C.char {
	result := path.Clean(C.GoString(path_))
	return C.CString(result)
}

//export goated_path_Dir
func goated_path_Dir(path_ *C.char) *C.char {
	result := path.Dir(C.GoString(path_))
	return C.CString(result)
}

//export goated_path_Ext
func goated_path_Ext(path_ *C.char) *C.char {
	result := path.Ext(C.GoString(path_))
	return C.CString(result)
}

//export goated_path_IsAbs
func goated_path_IsAbs(path_ *C.char) C.bool {
	result := path.IsAbs(C.GoString(path_))
	return C.bool(result)
}

//export goated_path_Match
func goated_path_Match(pattern *C.char, name *C.char, errOut **C.char) C.bool {
	result, err := path.Match(C.GoString(pattern), C.GoString(name))
	if err != nil {
		*errOut = C.CString(err.Error())
		return false
	}
	*errOut = nil
	return C.bool(result)
}

