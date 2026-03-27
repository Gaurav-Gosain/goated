package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"sort"
	"unsafe"
)

//export goated_sort_strings
func goated_sort_strings(strs **C.char, count C.int) {
	n := int(count)
	if n <= 0 {
		return
	}
	slice := unsafe.Slice(strs, n)
	goStrs := make([]string, n)
	for i := 0; i < n; i++ {
		goStrs[i] = C.GoString(slice[i])
	}
	sort.Strings(goStrs)
	for i := 0; i < n; i++ {
		C.free(unsafe.Pointer(slice[i]))
		slice[i] = C.CString(goStrs[i])
	}
}

//export goated_sort_ints
func goated_sort_ints(data *C.longlong, count C.int) {
	n := int(count)
	if n <= 0 {
		return
	}
	slice := unsafe.Slice((*int64)(unsafe.Pointer(data)), n)
	sort.Slice(slice, func(i, j int) bool {
		return slice[i] < slice[j]
	})
}

//export goated_sort_float64s
func goated_sort_float64s(data *C.double, count C.int) {
	n := int(count)
	if n <= 0 {
		return
	}
	slice := unsafe.Slice((*float64)(unsafe.Pointer(data)), n)
	sort.Float64s(slice)
}

//export goated_sort_strings_are_sorted
func goated_sort_strings_are_sorted(strs **C.char, count C.int) C.bool {
	n := int(count)
	if n <= 0 {
		return C.bool(true)
	}
	slice := unsafe.Slice(strs, n)
	goStrs := make([]string, n)
	for i := 0; i < n; i++ {
		goStrs[i] = C.GoString(slice[i])
	}
	return C.bool(sort.StringsAreSorted(goStrs))
}
