package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"net/mail"
	"strings"
	"unsafe"
)

//export goated_email_parse_address
func goated_email_parse_address(addr *C.char, nameOut **C.char, emailOut **C.char) C.bool {
	parsed, err := mail.ParseAddress(C.GoString(addr))
	if err != nil {
		return C.bool(false)
	}
	*nameOut = C.CString(parsed.Name)
	*emailOut = C.CString(parsed.Address)
	return C.bool(true)
}

//export goated_email_parse_address_list
func goated_email_parse_address_list(addrs *C.char) C.ulonglong {
	list, err := mail.ParseAddressList(C.GoString(addrs))
	if err != nil {
		return 0
	}
	return C.ulonglong(newHandle(list))
}

//export goated_batch_email_parse
func goated_batch_email_parse(
	addrs **C.char, count C.int,
	names **C.char, emails **C.char, valid *C.bool,
) {
	n := int(count)
	addrSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(addrs)), n)
	nameSlice := unsafe.Slice((**C.char)(unsafe.Pointer(names)), n)
	emailSlice := unsafe.Slice((**C.char)(unsafe.Pointer(emails)), n)
	validSlice := unsafe.Slice((*C.bool)(unsafe.Pointer(valid)), n)

	for j := 0; j < n; j++ {
		parsed, err := mail.ParseAddress(C.GoString(addrSlice[j]))
		if err != nil {
			validSlice[j] = C.bool(false)
			nameSlice[j] = C.CString("")
			emailSlice[j] = C.CString("")
		} else {
			validSlice[j] = C.bool(true)
			nameSlice[j] = C.CString(parsed.Name)
			emailSlice[j] = C.CString(parsed.Address)
		}
	}
}

//export goated_email_validate
func goated_email_validate(addr *C.char) C.bool {
	s := C.GoString(addr)
	// Quick validation: must have exactly one @, something before and after
	at := strings.IndexByte(s, '@')
	if at <= 0 || at >= len(s)-1 {
		return C.bool(false)
	}
	dot := strings.LastIndexByte(s[at:], '.')
	return C.bool(dot > 1)
}
