"""Go-powered HTTP server: 100K+ requests/second.

Uses Go's net/http under the hood. Ideal for serving APIs, static
content, or running high-throughput benchmarks.
"""

from goated.server import GoServer

# Start a Go HTTP server as a context manager.
# The server runs in Go's own goroutines -- Python just configures routes.
with GoServer(":8080") as app:
    # Serve JSON on an API endpoint
    app.json("/api/health", '{"status": "ok"}')

    # Serve static text
    app.static("/", "Hello from Go!")

    print("Server running at http://localhost:8080")
    print("Endpoints:")
    print("  GET /          -> static text")
    print("  GET /api/health -> JSON response")
    print()
    input("Press Enter to stop the server...")

# Server is automatically stopped when the context manager exits.
print("Server stopped.")
