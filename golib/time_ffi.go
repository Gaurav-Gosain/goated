package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"time"
)

//export goated_time_now_unix
func goated_time_now_unix() C.longlong {
	return C.longlong(time.Now().Unix())
}

//export goated_time_now_unix_nano
func goated_time_now_unix_nano() C.longlong {
	return C.longlong(time.Now().UnixNano())
}

//export goated_time_parse
func goated_time_parse(layout *C.char, value *C.char, errOut **C.char) C.longlong {
	t, err := time.Parse(C.GoString(layout), C.GoString(value))
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}
	*errOut = nil
	return C.longlong(t.Unix())
}

//export goated_time_format
func goated_time_format(unix_sec C.longlong, unix_nsec C.longlong, layout *C.char) *C.char {
	t := time.Unix(int64(unix_sec), int64(unix_nsec))
	return C.CString(t.UTC().Format(C.GoString(layout)))
}

//export goated_time_since_ns
func goated_time_since_ns(start_ns C.longlong) C.longlong {
	now := time.Now().UnixNano()
	return C.longlong(now - int64(start_ns))
}
