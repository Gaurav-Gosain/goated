package main

import (
	"flag"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"go/types"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"text/template"
)

type FuncInfo struct {
	Name        string
	GoName      string
	Params      []ParamInfo
	Results     []ParamInfo
	Doc         string
	ReturnsErr  bool
	MultiReturn bool // Has multiple non-error return values
}

type ParamInfo struct {
	Name    string
	GoType  string
	CType   string
	PyType  string
	IsSlice bool
	IsPtr   bool
}

type PackageInfo struct {
	Name      string
	GoPackage string
	Functions []FuncInfo
}

func main() {
	pkgPath := flag.String("pkg", "", "Go package to generate bindings for (e.g., strings, bytes)")
	outGo := flag.String("go-out", "", "Output path for Go FFI code")
	outPy := flag.String("py-out", "", "Output path for Python bindings")
	flag.Parse()

	if *pkgPath == "" {
		fmt.Fprintln(os.Stderr, "Usage: generator -pkg <package> [-go-out <path>] [-py-out <path>]")
		os.Exit(1)
	}

	pkg, err := parseStdlibPackage(*pkgPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing package: %v\n", err)
		os.Exit(1)
	}

	if *outGo != "" {
		if err := generateGoCode(pkg, *outGo); err != nil {
			fmt.Fprintf(os.Stderr, "Error generating Go code: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Generated Go code: %s\n", *outGo)
	}

	if *outPy != "" {
		if err := generatePyCode(pkg, *outPy); err != nil {
			fmt.Fprintf(os.Stderr, "Error generating Python code: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Generated Python code: %s\n", *outPy)
	}

	if *outGo == "" && *outPy == "" {
		printPackageInfo(pkg)
	}
}

func parseStdlibPackage(pkgName string) (*PackageInfo, error) {
	goroot := os.Getenv("GOROOT")
	if goroot == "" {
		out, err := exec.Command("go", "env", "GOROOT").Output()
		if err == nil {
			goroot = strings.TrimSpace(string(out))
		}
	}
	if goroot == "" {
		goroot = "/usr/local/go"
	}

	pkgDir := filepath.Join(goroot, "src", pkgName)
	if _, err := os.Stat(pkgDir); os.IsNotExist(err) {
		return nil, fmt.Errorf("package %s not found at %s", pkgName, pkgDir)
	}

	fset := token.NewFileSet()
	pkgs, err := parser.ParseDir(fset, pkgDir, func(fi os.FileInfo) bool {
		return !strings.HasSuffix(fi.Name(), "_test.go")
	}, parser.ParseComments)

	if err != nil {
		return nil, fmt.Errorf("failed to parse package: %w", err)
	}

	shortName := pkgName
	if idx := strings.LastIndex(pkgName, "/"); idx >= 0 {
		shortName = pkgName[idx+1:]
	}

	info := &PackageInfo{
		Name:      shortName,
		GoPackage: pkgName,
	}

	seen := make(map[string]bool)
	for _, pkg := range pkgs {
		if strings.HasSuffix(pkg.Name, "_test") {
			continue
		}

		for _, file := range pkg.Files {
			for _, decl := range file.Decls {
				if fn, ok := decl.(*ast.FuncDecl); ok {
					if fn.Recv != nil {
						continue
					}
					if !ast.IsExported(fn.Name.Name) {
						continue
					}
					if seen[fn.Name.Name] {
						continue
					}
					funcInfo := extractFuncInfo(fn)
					if funcInfo != nil && isBindable(funcInfo) {
						info.Functions = append(info.Functions, *funcInfo)
						seen[fn.Name.Name] = true
					}
				}
			}
		}
	}

	sort.Slice(info.Functions, func(i, j int) bool {
		return info.Functions[i].Name < info.Functions[j].Name
	})

	return info, nil
}

func extractFuncInfo(fn *ast.FuncDecl) *FuncInfo {
	info := &FuncInfo{
		Name:   fn.Name.Name,
		GoName: fn.Name.Name,
	}

	if fn.Doc != nil {
		info.Doc = strings.TrimSpace(fn.Doc.Text())
	}

	if fn.Type.Params != nil {
		paramIdx := 0
		for _, field := range fn.Type.Params.List {
			paramInfo := typeToParamInfo(field.Type)
			if paramInfo == nil {
				return nil
			}
			for _, name := range field.Names {
				p := *paramInfo
				p.Name = safeParamName(name.Name, paramIdx)
				paramIdx++
				info.Params = append(info.Params, p)
			}
			if len(field.Names) == 0 {
				p := *paramInfo
				p.Name = fmt.Sprintf("arg%d", paramIdx)
				paramIdx++
				info.Params = append(info.Params, p)
			}
		}
	}

	if fn.Type.Results != nil {
		for i, field := range fn.Type.Results.List {
			paramInfo := typeToParamInfo(field.Type)
			if paramInfo == nil {
				return nil
			}
			if paramInfo.GoType == "error" {
				info.ReturnsErr = true
				continue
			}
			for _, name := range field.Names {
				p := *paramInfo
				p.Name = name.Name
				info.Results = append(info.Results, p)
			}
			if len(field.Names) == 0 {
				p := *paramInfo
				p.Name = fmt.Sprintf("r%d", i)
				info.Results = append(info.Results, p)
			}
		}
	}

	if len(info.Results) > 1 {
		info.MultiReturn = true
	}

	return info
}

func typeToParamInfo(expr ast.Expr) *ParamInfo {
	switch t := expr.(type) {
	case *ast.Ident:
		return basicTypeToParam(t.Name)
	case *ast.ArrayType:
		if t.Len == nil {
			elem := typeToParamInfo(t.Elt)
			if elem == nil {
				return nil
			}
			return &ParamInfo{
				GoType:  "[]" + elem.GoType,
				CType:   "C.ulonglong",
				PyType:  "list",
				IsSlice: true,
			}
		}
		return nil
	case *ast.StarExpr:
		return nil
	case *ast.SelectorExpr:
		return nil
	case *ast.InterfaceType:
		return nil
	case *ast.FuncType:
		return nil
	case *ast.MapType:
		return nil
	case *ast.ChanType:
		return nil
	default:
		return nil
	}
}

var reservedNames = map[string]bool{
	"path": true, "filepath": true, "strings": true, "bytes": true, "strconv": true,
	"json": true, "crypto": true, "regexp": true, "time": true,
	"sort": true, "fmt": true, "os": true, "io": true,
}

func safeParamName(name string, idx int) string {
	if reservedNames[name] {
		return fmt.Sprintf("%s_", name)
	}
	return name
}

func basicTypeToParam(name string) *ParamInfo {
	switch name {
	case "string":
		return &ParamInfo{GoType: "string", CType: "*C.char", PyType: "str"}
	case "int":
		return &ParamInfo{GoType: "int", CType: "C.longlong", PyType: "int"}
	case "int8":
		return &ParamInfo{GoType: "int8", CType: "C.char", PyType: "int"}
	case "int16":
		return &ParamInfo{GoType: "int16", CType: "C.short", PyType: "int"}
	case "int32":
		return &ParamInfo{GoType: "int32", CType: "C.int", PyType: "int"}
	case "int64":
		return &ParamInfo{GoType: "int64", CType: "C.longlong", PyType: "int"}
	case "uint":
		return &ParamInfo{GoType: "uint", CType: "C.ulonglong", PyType: "int"}
	case "uint8", "byte":
		return &ParamInfo{GoType: "byte", CType: "C.uchar", PyType: "int"}
	case "uint16":
		return &ParamInfo{GoType: "uint16", CType: "C.ushort", PyType: "int"}
	case "uint32":
		return &ParamInfo{GoType: "uint32", CType: "C.uint", PyType: "int"}
	case "uint64":
		return &ParamInfo{GoType: "uint64", CType: "C.ulonglong", PyType: "int"}
	case "float32":
		return &ParamInfo{GoType: "float32", CType: "C.float", PyType: "float"}
	case "float64":
		return &ParamInfo{GoType: "float64", CType: "C.double", PyType: "float"}
	case "bool":
		return &ParamInfo{GoType: "bool", CType: "C.bool", PyType: "bool"}
	case "rune":
		return &ParamInfo{GoType: "rune", CType: "C.int", PyType: "str"}
	case "error":
		return &ParamInfo{GoType: "error", CType: "**C.char", PyType: "str"}
	default:
		return nil
	}
}

func isBindable(fn *FuncInfo) bool {
	for _, p := range fn.Params {
		if p.CType == "" || p.IsSlice {
			return false
		}
	}
	for _, r := range fn.Results {
		if r.CType == "" || r.IsSlice {
			return false
		}
	}
	if len(fn.Results) > 2 {
		return false
	}
	if fn.MultiReturn && len(fn.Results) > 1 {
		return false
	}
	return true
}

func printPackageInfo(pkg *PackageInfo) {
	fmt.Printf("Package: %s\n", pkg.Name)
	fmt.Printf("Bindable functions: %d\n\n", len(pkg.Functions))

	for _, fn := range pkg.Functions {
		fmt.Printf("  %s(", fn.Name)
		for i, p := range fn.Params {
			if i > 0 {
				fmt.Print(", ")
			}
			fmt.Printf("%s %s", p.Name, p.GoType)
		}
		fmt.Print(")")
		if len(fn.Results) > 0 {
			fmt.Print(" ")
			if len(fn.Results) == 1 {
				fmt.Print(fn.Results[0].GoType)
			} else {
				fmt.Print("(")
				for i, r := range fn.Results {
					if i > 0 {
						fmt.Print(", ")
					}
					fmt.Print(r.GoType)
				}
				fmt.Print(")")
			}
		}
		if fn.ReturnsErr {
			if len(fn.Results) > 0 {
				fmt.Print(", error")
			} else {
				fmt.Print(" error")
			}
		}
		fmt.Println()
	}
}

func generateGoCode(pkg *PackageInfo, outPath string) error {
	tmpl := template.Must(template.New("go").Funcs(template.FuncMap{
		"lower":     strings.ToLower,
		"snakeCase": toSnakeCase,
	}).Parse(goTemplate))

	f, err := os.Create(outPath)
	if err != nil {
		return err
	}
	defer f.Close()

	return tmpl.Execute(f, pkg)
}

func generatePyCode(pkg *PackageInfo, outPath string) error {
	tmpl := template.Must(template.New("py").Funcs(template.FuncMap{
		"lower":     strings.ToLower,
		"snakeCase": toSnakeCase,
		"pyDoc":     formatPyDoc,
	}).Parse(pyTemplate))

	f, err := os.Create(outPath)
	if err != nil {
		return err
	}
	defer f.Close()

	return tmpl.Execute(f, pkg)
}

func toSnakeCase(s string) string {
	var result strings.Builder
	for i, r := range s {
		if i > 0 && r >= 'A' && r <= 'Z' {
			result.WriteByte('_')
		}
		result.WriteRune(r)
	}
	return strings.ToLower(result.String())
}

func formatPyDoc(doc string) string {
	if doc == "" {
		return ""
	}
	// Escape backslashes so Python doesn't interpret them as escape sequences
	doc = strings.ReplaceAll(doc, "\\", "\\\\")
	lines := strings.Split(doc, "\n")
	if len(lines) == 1 {
		return fmt.Sprintf(`"""%s"""`, lines[0])
	}
	var result strings.Builder
	result.WriteString(`"""`)
	for i, line := range lines {
		if i > 0 {
			result.WriteString("\n    ")
		}
		result.WriteString(line)
	}
	result.WriteString(`"""`)
	return result.String()
}

var _ types.Type

const goTemplate = `package main

/*
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
*/
import "C"
import (
	"{{.GoPackage}}"
)

{{range .Functions}}
//export goated_{{$.Name}}_{{.Name}}
func goated_{{$.Name}}_{{.Name}}({{range $i, $p := .Params}}{{if $i}}, {{end}}{{$p.Name}} {{$p.CType}}{{end}}{{if .ReturnsErr}}, errOut **C.char{{end}}) {{if len .Results}}{{if eq (len .Results) 1}}{{(index .Results 0).CType}}{{else}}({{range $i, $r := .Results}}{{if $i}}, {{end}}{{$r.CType}}{{end}}){{end}}{{else}}{{if .ReturnsErr}}C.bool{{end}}{{end}} {
{{- if .ReturnsErr}}
	{{if len .Results}}result, {{end}}err := {{$.Name}}.{{.GoName}}({{range $i, $p := .Params}}{{if $i}}, {{end}}{{if eq $p.GoType "string"}}C.GoString({{$p.Name}}){{else}}{{$p.GoType}}({{$p.Name}}){{end}}{{end}})
	if err != nil {
		*errOut = C.CString(err.Error())
		{{if len .Results}}return {{range $i, $r := .Results}}{{if $i}}, {{end}}{{if eq $r.GoType "string"}}nil{{else if eq $r.GoType "bool"}}false{{else}}0{{end}}{{end}}{{else}}return false{{end}}
	}
	*errOut = nil
	{{if len .Results}}return {{range $i, $r := .Results}}{{if $i}}, {{end}}{{if eq $r.GoType "string"}}C.CString(result){{else}}{{$r.CType}}(result){{end}}{{end}}{{else}}return true{{end}}
{{- else}}
	result := {{$.Name}}.{{.GoName}}({{range $i, $p := .Params}}{{if $i}}, {{end}}{{if eq $p.GoType "string"}}C.GoString({{$p.Name}}){{else}}{{$p.GoType}}({{$p.Name}}){{end}}{{end}})
	{{if len .Results}}return {{range $i, $r := .Results}}{{if $i}}, {{end}}{{if eq $r.GoType "string"}}C.CString(result){{else}}{{$r.CType}}(result){{end}}{{end}}{{else}}_ = result{{end}}
{{- end}}
}
{{end}}
`

const pyTemplate = `"""
Go {{.Name}} package bindings - Auto-generated.

This module provides Python bindings for Go's {{.GoPackage}} package.
"""

from __future__ import annotations

from goated._core import get_lib, is_library_available
from goated.result import Ok, Err, Result, GoError

__all__ = [
{{- range .Functions}}
    "{{.Name}}",
{{- end}}
]


def _encode(s: str) -> bytes:
    return s.encode("utf-8")


def _decode(b: bytes | None) -> str:
    if b is None:
        return ""
    return b.decode("utf-8")

import ctypes

_fn_configured: set[str] = set()

def _configure_fn(lib, name: str, argtypes: list, restype):
    if name in _fn_configured:
        return
    fn = getattr(lib, name)
    fn.argtypes = argtypes
    fn.restype = restype
    _fn_configured.add(name)

{{range .Functions}}

def {{.Name}}({{range $i, $p := .Params}}{{if $i}}, {{end}}{{$p.Name}}: {{$p.PyType}}{{end}}){{if .ReturnsErr}} -> Result[{{if len .Results}}{{(index .Results 0).PyType}}{{else}}None{{end}}, GoError]{{else}}{{if len .Results}} -> {{(index .Results 0).PyType}}{{end}}{{end}}:
    {{pyDoc .Doc}}
{{- if .ReturnsErr}}
    if not is_library_available():
        raise NotImplementedError("Go library not available")
    
    lib = get_lib()
    _configure_fn(lib, "goated_{{$.Name}}_{{.Name}}", [{{range $i, $p := .Params}}{{if $i}}, {{end}}ctypes.c_char_p{{end}}, ctypes.POINTER(ctypes.c_char_p)], {{if len .Results}}{{if eq (index .Results 0).GoType "string"}}ctypes.c_char_p{{else if eq (index .Results 0).GoType "bool"}}ctypes.c_bool{{else}}ctypes.c_longlong{{end}}{{else}}ctypes.c_bool{{end}})
    err_out = ctypes.c_char_p()
    result = lib.goated_{{$.Name}}_{{.Name}}({{range $i, $p := .Params}}{{if $i}}, {{end}}{{if eq $p.GoType "string"}}_encode({{$p.Name}}){{else}}{{$p.Name}}{{end}}{{end}}, ctypes.byref(err_out))
    
    if err_out.value:
        return Err(GoError(_decode(err_out.value)))
    {{if len .Results}}return Ok({{if eq (index .Results 0).GoType "string"}}_decode(result){{else}}result{{end}}){{else}}return Ok(None){{end}}
{{- else}}
    if not is_library_available():
        {{if eq (len .Results) 0}}return{{else}}{{if eq (index .Results 0).GoType "string"}}return ""{{else if eq (index .Results 0).GoType "bool"}}return False{{else if eq (index .Results 0).GoType "int"}}return 0{{else}}return None{{end}}{{end}}
    
    lib = get_lib()
    _configure_fn(lib, "goated_{{$.Name}}_{{.Name}}", [{{range $i, $p := .Params}}{{if $i}}, {{end}}ctypes.c_char_p{{end}}], {{if len .Results}}{{if eq (index .Results 0).GoType "string"}}ctypes.c_char_p{{else if eq (index .Results 0).GoType "bool"}}ctypes.c_bool{{else}}ctypes.c_longlong{{end}}{{else}}None{{end}})
    result = lib.goated_{{$.Name}}_{{.Name}}({{range $i, $p := .Params}}{{if $i}}, {{end}}{{if eq $p.GoType "string"}}_encode({{$p.Name}}){{else}}{{$p.Name}}{{end}}{{end}})
    {{if len .Results}}return {{if eq (index .Results 0).GoType "string"}}_decode(result){{else if eq (index .Results 0).GoType "bool"}}bool(result){{else}}result{{end}}{{end}}
{{- end}}
{{end}}
`
