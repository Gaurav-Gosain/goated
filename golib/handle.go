package main

import (
	"sync"
	"sync/atomic"
)

var (
	handleCounter uint64
	handles       sync.Map
)

func newHandle(obj any) uint64 {
	h := atomic.AddUint64(&handleCounter, 1)
	handles.Store(h, obj)
	return h
}

func getHandle[T any](h uint64) (T, bool) {
	v, ok := handles.Load(h)
	if !ok {
		var zero T
		return zero, false
	}
	return v.(T), true
}

func deleteHandle(h uint64) {
	handles.Delete(h)
}

func getStringSlice(h uint64) ([]string, bool) {
	return getHandle[[]string](h)
}

// getAny returns the object at the handle as interface{}
func getAny(h uint64) (any, bool) {
	return handles.Load(h)
}
