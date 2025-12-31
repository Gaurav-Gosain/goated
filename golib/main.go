package main

import "C"

//export goated_handle_delete
func goated_handle_delete(h C.ulonglong) {
	deleteHandle(uint64(h))
}

func main() {}
