package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"path/filepath"
)


//export goated_filepath_Abs
func goated_filepath_Abs(path_ *C.char, errOut **C.char) *C.char {
	result, err := filepath.Abs(C.GoString(path_))
	if err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	*errOut = nil
	return C.CString(result)
}

//export goated_filepath_Base
func goated_filepath_Base(path_ *C.char) *C.char {
	result := filepath.Base(C.GoString(path_))
	return C.CString(result)
}

//export goated_filepath_Clean
func goated_filepath_Clean(path_ *C.char) *C.char {
	result := filepath.Clean(C.GoString(path_))
	return C.CString(result)
}

//export goated_filepath_Dir
func goated_filepath_Dir(path_ *C.char) *C.char {
	result := filepath.Dir(C.GoString(path_))
	return C.CString(result)
}

//export goated_filepath_EvalSymlinks
func goated_filepath_EvalSymlinks(path_ *C.char, errOut **C.char) *C.char {
	result, err := filepath.EvalSymlinks(C.GoString(path_))
	if err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	*errOut = nil
	return C.CString(result)
}

//export goated_filepath_Ext
func goated_filepath_Ext(path_ *C.char) *C.char {
	result := filepath.Ext(C.GoString(path_))
	return C.CString(result)
}

//export goated_filepath_FromSlash
func goated_filepath_FromSlash(path_ *C.char) *C.char {
	result := filepath.FromSlash(C.GoString(path_))
	return C.CString(result)
}

//export goated_filepath_HasPrefix
func goated_filepath_HasPrefix(p *C.char, prefix *C.char) C.bool {
	result := filepath.HasPrefix(C.GoString(p), C.GoString(prefix))
	return C.bool(result)
}

//export goated_filepath_IsAbs
func goated_filepath_IsAbs(path_ *C.char) C.bool {
	result := filepath.IsAbs(C.GoString(path_))
	return C.bool(result)
}

//export goated_filepath_IsLocal
func goated_filepath_IsLocal(path_ *C.char) C.bool {
	result := filepath.IsLocal(C.GoString(path_))
	return C.bool(result)
}

//export goated_filepath_Localize
func goated_filepath_Localize(path_ *C.char, errOut **C.char) *C.char {
	result, err := filepath.Localize(C.GoString(path_))
	if err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	*errOut = nil
	return C.CString(result)
}

//export goated_filepath_Match
func goated_filepath_Match(pattern *C.char, name *C.char, errOut **C.char) C.bool {
	result, err := filepath.Match(C.GoString(pattern), C.GoString(name))
	if err != nil {
		*errOut = C.CString(err.Error())
		return false
	}
	*errOut = nil
	return C.bool(result)
}

//export goated_filepath_Rel
func goated_filepath_Rel(basepath *C.char, targpath *C.char, errOut **C.char) *C.char {
	result, err := filepath.Rel(C.GoString(basepath), C.GoString(targpath))
	if err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	*errOut = nil
	return C.CString(result)
}

//export goated_filepath_ToSlash
func goated_filepath_ToSlash(path_ *C.char) *C.char {
	result := filepath.ToSlash(C.GoString(path_))
	return C.CString(result)
}

//export goated_filepath_VolumeName
func goated_filepath_VolumeName(path_ *C.char) *C.char {
	result := filepath.VolumeName(C.GoString(path_))
	return C.CString(result)
}

