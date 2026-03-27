package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"context"
	"fmt"
	"io"
	"net"
	"net/http"
	"strings"
	"sync"
	"time"
)

var (
	serverMu      sync.Mutex
	servers       = make(map[uint64]*http.Server)
	serverID      uint64
	handlersMu    sync.RWMutex
	staticRoutes  = make(map[uint64]map[string]string) // serverID -> path -> response body
	jsonRoutes    = make(map[uint64]map[string]string) // serverID -> path -> json body
)

//export goated_http_server_new
func goated_http_server_new(addr *C.char) C.ulonglong {
	serverMu.Lock()
	defer serverMu.Unlock()

	serverID++
	id := serverID

	staticRoutes[id] = make(map[string]string)
	jsonRoutes[id] = make(map[string]string)

	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		handlersMu.RLock()
		defer handlersMu.RUnlock()

		path := r.URL.Path

		// Check JSON routes first
		if body, ok := jsonRoutes[id][path]; ok {
			w.Header().Set("Content-Type", "application/json")
			io.WriteString(w, body)
			return
		}

		// Check static routes
		if body, ok := staticRoutes[id][path]; ok {
			w.Header().Set("Content-Type", "text/plain")
			io.WriteString(w, body)
			return
		}

		http.NotFound(w, r)
	})

	srv := &http.Server{
		Addr:         C.GoString(addr),
		Handler:      mux,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}
	servers[id] = srv

	return C.ulonglong(id)
}

//export goated_http_server_route
func goated_http_server_route(id C.ulonglong, path *C.char, body *C.char, contentType *C.char) {
	sid := uint64(id)
	handlersMu.Lock()
	defer handlersMu.Unlock()

	ct := C.GoString(contentType)
	p := C.GoString(path)
	b := C.GoString(body)

	if strings.Contains(ct, "json") {
		jsonRoutes[sid][p] = b
	} else {
		staticRoutes[sid][p] = b
	}
}

//export goated_http_server_start
func goated_http_server_start(id C.ulonglong, errOut **C.char) {
	sid := uint64(id)
	serverMu.Lock()
	srv, ok := servers[sid]
	serverMu.Unlock()

	if !ok {
		*errOut = C.CString("server not found")
		return
	}

	// Start in background goroutine
	go func() {
		ln, err := net.Listen("tcp", srv.Addr)
		if err != nil {
			return
		}
		srv.Serve(ln)
	}()

	// Wait for server to be ready
	time.Sleep(10 * time.Millisecond)
	*errOut = nil
}

//export goated_http_server_stop
func goated_http_server_stop(id C.ulonglong) {
	sid := uint64(id)
	serverMu.Lock()
	srv, ok := servers[sid]
	if ok {
		delete(servers, sid)
		delete(staticRoutes, sid)
		delete(jsonRoutes, sid)
	}
	serverMu.Unlock()

	if ok {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		srv.Shutdown(ctx)
	}
}

//export goated_http_server_addr
func goated_http_server_addr(id C.ulonglong) *C.char {
	sid := uint64(id)
	serverMu.Lock()
	srv, ok := servers[sid]
	serverMu.Unlock()

	if !ok {
		return C.CString("")
	}
	return C.CString(srv.Addr)
}

// ============================================================
// Fast static file server
// ============================================================

//export goated_http_fileserver_new
func goated_http_fileserver_new(addr *C.char, dir *C.char) C.ulonglong {
	serverMu.Lock()
	defer serverMu.Unlock()

	serverID++
	id := serverID

	srv := &http.Server{
		Addr:         C.GoString(addr),
		Handler:      http.FileServer(http.Dir(C.GoString(dir))),
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
	}
	servers[id] = srv

	return C.ulonglong(id)
}

// ============================================================
// Simple benchmark: respond with static JSON
// ============================================================

//export goated_http_bench_server
func goated_http_bench_server(addr *C.char, jsonResponse *C.char, errOut **C.char) C.ulonglong {
	serverMu.Lock()
	defer serverMu.Unlock()

	serverID++
	id := serverID

	resp := C.GoString(jsonResponse)
	respBytes := []byte(resp)

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Content-Length", fmt.Sprintf("%d", len(respBytes)))
		w.Write(respBytes)
	})

	srv := &http.Server{
		Addr:         C.GoString(addr),
		Handler:      mux,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}
	servers[id] = srv

	go func() {
		ln, err := net.Listen("tcp", srv.Addr)
		if err != nil {
			return
		}
		srv.Serve(ln)
	}()

	time.Sleep(10 * time.Millisecond)
	*errOut = nil
	return C.ulonglong(id)
}
