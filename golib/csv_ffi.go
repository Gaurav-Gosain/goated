package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"bytes"
	"encoding/csv"
	"strings"
)

//export goated_csv_read_all
func goated_csv_read_all(data *C.char, dataLen C.int, errOut **C.char) C.ulonglong {
	input := C.GoStringN(data, dataLen)
	r := csv.NewReader(strings.NewReader(input))
	records, err := r.ReadAll()
	if err != nil {
		*errOut = C.CString(err.Error())
		return 0
	}
	*errOut = nil
	return C.ulonglong(newHandle(records))
}

//export goated_csv_records_len
func goated_csv_records_len(handle C.ulonglong) C.int {
	records, ok := getHandle[[][]string](uint64(handle))
	if !ok {
		return 0
	}
	return C.int(len(records))
}

//export goated_csv_record_len
func goated_csv_record_len(handle C.ulonglong, row C.int) C.int {
	records, ok := getHandle[[][]string](uint64(handle))
	if !ok || int(row) >= len(records) || row < 0 {
		return 0
	}
	return C.int(len(records[row]))
}

//export goated_csv_get_field
func goated_csv_get_field(handle C.ulonglong, row C.int, col C.int) *C.char {
	records, ok := getHandle[[][]string](uint64(handle))
	if !ok || int(row) >= len(records) || row < 0 {
		return nil
	}
	r := records[row]
	if int(col) >= len(r) || col < 0 {
		return nil
	}
	return C.CString(r[col])
}

//export goated_csv_write_all
func goated_csv_write_all(handle C.ulonglong, errOut **C.char) *C.char {
	records, ok := getHandle[[][]string](uint64(handle))
	if !ok {
		*errOut = C.CString("invalid handle")
		return nil
	}
	var buf bytes.Buffer
	w := csv.NewWriter(&buf)
	err := w.WriteAll(records)
	if err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	w.Flush()
	if err := w.Error(); err != nil {
		*errOut = C.CString(err.Error())
		return nil
	}
	*errOut = nil
	return C.CString(buf.String())
}
