package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"math"
	"runtime"
	"sync"
	"unsafe"
)

//export goated_rgb_to_hsv
func goated_rgb_to_hsv(r, g, b C.double, h, s, v *C.double) {
	rf, gf, bf := float64(r), float64(g), float64(b)
	maxc := math.Max(rf, math.Max(gf, bf))
	minc := math.Min(rf, math.Min(gf, bf))
	*v = C.double(maxc)
	if minc == maxc {
		*h = 0
		*s = 0
		return
	}
	diff := maxc - minc
	*s = C.double(diff / maxc)
	rc := (maxc - rf) / diff
	gc := (maxc - gf) / diff
	bc := (maxc - bf) / diff
	var hf float64
	if rf == maxc {
		hf = bc - gc
	} else if gf == maxc {
		hf = 2.0 + rc - bc
	} else {
		hf = 4.0 + gc - rc
	}
	hf = math.Mod(hf/6.0, 1.0)
	if hf < 0 {
		hf += 1.0
	}
	*h = C.double(hf)
}

//export goated_hsv_to_rgb
func goated_hsv_to_rgb(h, s, v C.double, r, g, b *C.double) {
	hf, sf, vf := float64(h), float64(s), float64(v)
	if sf == 0.0 {
		*r = C.double(vf)
		*g = C.double(vf)
		*b = C.double(vf)
		return
	}
	i := int(hf * 6.0)
	f := hf*6.0 - float64(i)
	p := vf * (1.0 - sf)
	q := vf * (1.0 - sf*f)
	t := vf * (1.0 - sf*(1.0-f))
	switch i % 6 {
	case 0:
		*r, *g, *b = C.double(vf), C.double(t), C.double(p)
	case 1:
		*r, *g, *b = C.double(q), C.double(vf), C.double(p)
	case 2:
		*r, *g, *b = C.double(p), C.double(vf), C.double(t)
	case 3:
		*r, *g, *b = C.double(p), C.double(q), C.double(vf)
	case 4:
		*r, *g, *b = C.double(t), C.double(p), C.double(vf)
	case 5:
		*r, *g, *b = C.double(vf), C.double(p), C.double(q)
	}
}

//export goated_batch_rgb_to_hsv
func goated_batch_rgb_to_hsv(
	rs, gs, bs *C.double, count C.int,
	hs, ss, vs *C.double,
) {
	n := int(count)
	rSlice := unsafe.Slice((*C.double)(unsafe.Pointer(rs)), n)
	gSlice := unsafe.Slice((*C.double)(unsafe.Pointer(gs)), n)
	bSlice := unsafe.Slice((*C.double)(unsafe.Pointer(bs)), n)
	hSlice := unsafe.Slice((*C.double)(unsafe.Pointer(hs)), n)
	sSlice := unsafe.Slice((*C.double)(unsafe.Pointer(ss)), n)
	vSlice := unsafe.Slice((*C.double)(unsafe.Pointer(vs)), n)

	numWorkers := runtime.NumCPU()
	chunkSize := (n + numWorkers - 1) / numWorkers
	var wg sync.WaitGroup

	for i := 0; i < numWorkers; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if end > n {
			end = n
		}
		if start >= n {
			break
		}
		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			for j := start; j < end; j++ {
				goated_rgb_to_hsv(rSlice[j], gSlice[j], bSlice[j],
					&hSlice[j], &sSlice[j], &vSlice[j])
			}
		}(start, end)
	}
	wg.Wait()
}
