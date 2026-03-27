package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"net"
	"unsafe"
)

//export goated_ip_parse
func goated_ip_parse(s *C.char) *C.char {
	ip := net.ParseIP(C.GoString(s))
	if ip == nil {
		return nil
	}
	return C.CString(ip.String())
}

//export goated_ip_is_valid
func goated_ip_is_valid(s *C.char) C.bool {
	return C.bool(net.ParseIP(C.GoString(s)) != nil)
}

//export goated_cidr_contains
func goated_cidr_contains(cidr *C.char, ip *C.char) C.bool {
	_, network, err := net.ParseCIDR(C.GoString(cidr))
	if err != nil {
		return C.bool(false)
	}
	return C.bool(network.Contains(net.ParseIP(C.GoString(ip))))
}

//export goated_batch_ip_validate
func goated_batch_ip_validate(
	ips **C.char, count C.int,
	results *C.bool,
) {
	n := int(count)
	ipSlice := unsafe.Slice((*(*C.char))(unsafe.Pointer(ips)), n)
	resSlice := unsafe.Slice((*C.bool)(unsafe.Pointer(results)), n)

	for j := 0; j < n; j++ {
		resSlice[j] = C.bool(net.ParseIP(C.GoString(ipSlice[j])) != nil)
	}
}
